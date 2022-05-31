from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Any, Dict, List

import feedparser
import pandas as pd
import pangres
import spacy
from mmh3 import hash as mmh3_hash
from spacy.lang.en import English as SpacyEnglishPipeline
from spacy.language import Language
from spacy_langdetect import LanguageDetector
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import IntegrityError
from tqdm import tqdm

from crypto_sentiment_demo_app.utils import (
    get_db_connection_engine,
    get_logger,
    load_config_params,
    parse_time,
)

logger = get_logger(Path(__file__).name)


class Crawler:
    def __init__(self, sqlalchemy_engine: Engine, path_to_rss_feeds: str, spacy_model: SpacyEnglishPipeline):
        """
        :param sqlalchemy_engine: SQLAlchemy engine to connect to a database
        :param path_to_rss_feeds: path to a file with a list of RSS feeds to parse
        :param spacy_model: Spacy pipeline: spacy.lang.en.English object
        """
        self.sqlalchemy_engine = sqlalchemy_engine
        self.path_to_rss_feeds = path_to_rss_feeds
        self.spacy_model = spacy_model
        Crawler.__enable_langdetect_with_spacy(spacy_model=self.spacy_model)

    def parse_rss_feeds(self) -> pd.DataFrame:
        """
        Goes through all RSS feeds, calls `__parse_rss_feed` for each one of them to fetch
        titles, sources, and publication timestamps.
        :return: a DataFrame with titles, sources, and publication timestamps
        """
        urls = self.__get_rss_urls(path_to_rss_feed_list=self.path_to_rss_feeds)
        dataframes_per_url: List[pd.DataFrame] = []

        for url in tqdm(urls, total=len(urls)):
            feed: List[feedparser.util.FeedParserDict] = feedparser.parse(url)["entries"]
            curr_df: pd.DataFrame = self.__parse_rss_feed(feed)
            dataframes_per_url.append(curr_df)
            logger.info(f"Parsed feed {url} with {len(feed)} records.")

        df = pd.concat(dataframes_per_url).drop_duplicates(subset="title_id")

        df.set_index("title_id", inplace=True)
        logger.info(f"Parsed {len(urls)} feeds with {len(df)} records in total.")
        return df

    @staticmethod
    def __parse_rss_feed(feed: List[feedparser.util.FeedParserDict]) -> pd.DataFrame:
        """
        Parses a single RSS feed and fetches
        titles, sources, and publication timestamps.
        :param feed: a list of dictionaries, output of feedparser.parse(<RSS_FEED_URL>)['entries']
        :return: a DataFrame with titles, sources, and publication timestamps
        """

        ids, parsed_titles, sources, pub_times = [], [], [], []

        for title_metadata in feed:
            # "title", "published" are obligatory fields
            if ("title" not in title_metadata.keys()) or ("published" not in title_metadata.keys()):
                continue
            else:
                #  obligatory fields are there
                ids.append(mmh3_hash(title_metadata.title, seed=17))
                parsed_titles.append(title_metadata.title)
                if "summary_detail" in title_metadata.keys():
                    sources.append(title_metadata.summary_detail["base"])
                elif "title_detail" in title_metadata.keys():
                    sources.append(title_metadata.title_detail["base"])
                else:
                    sources.append("missing")
                pub_times.append(parse_time(title_metadata.published))

        df = pd.DataFrame(
            {
                "title_id": ids,
                "title": parsed_titles,
                "source": sources,
                "pub_time": pub_times,
            }
        )

        return df

    @staticmethod
    def get_lang_detector_spacy(nlp: SpacyEnglishPipeline, name: str):
        """
        A function to be used to add a Spacy language detector pipeline.
        Taken from here:
        https://stackoverflow.com/questions/66712753/how-to-use-languagedetector-from-spacy-langdetect-package
        :param nlp:
        :param name: pipeline name
        :return:
        """
        return LanguageDetector()

    @staticmethod
    def __enable_langdetect_with_spacy(spacy_model: SpacyEnglishPipeline):
        Language.factory("language_detector", func=Crawler.get_lang_detector_spacy)
        spacy_model.add_pipe("language_detector", last=True)

    @staticmethod
    def __get_rss_urls(path_to_rss_feed_list: str) -> List[str]:
        """
        Gets a list of URLs form a text file
        :param path_to_rss_feed_list: path to a text file
        :return: a list of strings
        """
        with open(path_to_rss_feed_list) as f:
            urls = [line.strip() for line in f.readlines()]
        return urls

    @staticmethod
    def __filter_out_question_marks(df: pd.DataFrame, text_col_name: str = "title") -> pd.DataFrame:
        """
        A primitive method returning True if a question mark is found in the text
        :param df: a DataFrame
        :param text_col_name: column name to filter on
        :return: bool
        """
        return df.loc[~df[text_col_name].str.contains("\?")]

    def __filter_verbs_spacy(self, df: pd.DataFrame, text_col_name: str = "title") -> pd.DataFrame:
        """
        A primitive method returning True if a question mark is found in the text
        :param df: a DataFrame
        :param text_col_name: column name to filter on
        :return: bool
        """
        return df.loc[
            df[text_col_name].apply(lambda sent: Crawler.__has_verb_spacy(sent=sent, spacy_model=self.spacy_model))
        ]

    @staticmethod
    def __has_verb_spacy(sent: str, spacy_model: SpacyEnglishPipeline) -> bool:
        """
        Determines whether a string `sent` contains a verb, according to the Spacy model.
        :param sent: any string
        :param spacy_model: Spacy pipeline: spacy.lang.en.English object
        :return: bool
        """
        # https://ashutoshtripathi.com/2020/04/13/parts-of-speech-tagging-and-dependency-parsing-using-spacy-nlp/
        doc = spacy_model(sent)

        verb_found = False
        for t in doc:
            if t.pos_ == "VERB":
                verb_found = True
                break

        return verb_found

    @staticmethod
    def __filter_on_text_length(
        df: pd.DataFrame, text_col_name: str = "title", min_length_words: int = 6
    ) -> pd.DataFrame:
        """
        Leave only texts in `text_col_name` column of the DataFrame `df` that are longer than
        `min_length_words` words.
        :param df: a DataFrame
        :param text_col_name: column name to filter on
        :param min_length_words: minimal number of words
        :return: bool
        """
        return df.loc[df[text_col_name].apply(lambda sent: len(sent.split())) >= min_length_words]

    def __filter_out_non_english_spacy(self, df: pd.DataFrame, text_col_name: str = "title") -> pd.DataFrame:
        """
        A primitive method returning True if a question mark is found in the text
        :param df: a DataFrame
        :param text_col_name: column name to filter on
        :return: bool
        """
        return df.loc[
            df[text_col_name].apply(lambda sent: Crawler.__is_english_spacy(text=sent, spacy_model=self.spacy_model))
        ]

    @staticmethod
    def __is_english_spacy(text: str, spacy_model: SpacyEnglishPipeline, min_confidence: float = 0.8) -> bool:
        """
        Determines if  a text is in English, according to the Spacy language detector.
        :param text: any string
        :param spacy_model: Spacy pipeline: spacy.lang.en.English object
        :param min_confidence: minimal language classifier confidence
        :return: whether the text is in English, according to the Spacy language detector
        """
        doc = spacy_model(text, disable=["ner", "tok2vec"])
        lang, confidence = doc._.language["language"], doc._.language["score"]

        return (lang == "en") and (confidence >= min_confidence)

    @staticmethod
    def __filter_on_publication_date(
        df: pd.DataFrame, min_date: str, pub_timestamp_col_name: str = "pub_time"
    ) -> pd.DataFrame:
        """
        Leave only texts in `text_col_name` column of the DataFrame `df` that are longer than
        `min_length_words` words.
        :param df: a DataFrame
        :param min_date: date formatted as YYYY-MM-DD
        :param pub_timestamp_col_name: column name to filter on
        :return: bool
        """
        return df.loc[df[pub_timestamp_col_name] >= parse_time(min_date)]

    def filter_titles(
        self, df: pd.DataFrame, min_date: str, text_col_name: str = "title", pub_timestamp_col_name: str = "pub_time"
    ) -> pd.DataFrame:
        """

        Applies filters on `text_col_name` column of the DataFrame `df`.
        :param df: a crawled pandas DataFrame
        :param min_date: oldest publication date to keep, formatted as YYYY-MM-DD
        :param text_col_name: column name with text to filter on
        :param pub_timestamp_col_name: column name with publication date to filter on
        :return: a filtered DataFrame
        """

        tmp_df = self.__filter_on_publication_date(
            df=df, pub_timestamp_col_name=pub_timestamp_col_name, min_date=min_date
        )
        tmp_df1 = self.__filter_out_question_marks(df=tmp_df, text_col_name=text_col_name)
        tmp_df2 = self.__filter_on_text_length(df=tmp_df1, text_col_name=text_col_name)
        tmp_df3 = self.__filter_verbs_spacy(df=tmp_df2, text_col_name=text_col_name)
        result_df = self.__filter_out_non_english_spacy(df=tmp_df3, text_col_name=text_col_name)

        return result_df

    def write_news_to_db(self, df: pd.DataFrame, table_name: str):
        """
        Writes scraped content into a table

        :param df: a pandas DataFrame output by the `parse_bitcointicker` method
        :param table_name: table name to write data to
        :return: None
        """

        # pandas `to_sql` doesn't yet support updating records ("upsert")
        # https://github.com/pandas-dev/pandas/issues/15988
        # hence using Pangres upsert https://github.com/ThibTrip/pangres/wiki/Upsert

        pangres.upsert(df=df, con=self.sqlalchemy_engine, table_name=table_name, if_row_exists="update")

    def write_ids_to_db(self, df: pd.DataFrame, index_name: str, table_name: str):
        """
        Writes news IDs into a table for model predictions to be further picked up by the
        `model_scorer` service.

        :param df: a pandas DataFrame output by the `parse_rss_feeds` method
        :param index_name: index name of a table to write data to
        :param table_name: table name to write IDs to
        :return: None
        """

        # write news title IDs to a table for predictions
        # pandas `to_sql` doesn't yet support updating records ("upsert")
        # https://github.com/pandas-dev/pandas/issues/15988
        # hence using Pangres upsert https://github.com/ThibTrip/pangres/wiki/Upsert
        df[index_name] = df.index
        # index can not be ignored, hence a workaround with an empty list of columns
        pangres.upsert(df=df[[]], con=self.sqlalchemy_engine, table_name=table_name, if_row_exists="update")

    def run(
        self,
        content_index_name: str,
        content_table_name: str,
        model_pred_table_name: str,
    ):
        """
        Runs the crawler

        :param content_index_name: index name of a table to write data to
        :param content_table_name: table name to write content to
        :param model_pred_table_name: table name to write IDs to
        :return: None
        """

        # # TODO: run with crontab instead
        # while 1:
        df = self.parse_rss_feeds()

        logger.info(f"Crawled {len(df)} records.")

        # we'll keep only today's news
        today = datetime.today().strftime("%Y-%m-%d")

        filtered_df = self.filter_titles(df=df, text_col_name="title", min_date=today)

        logger.info(f"{len(filtered_df)} records left after filtering.")

        try:
            self.write_news_to_db(df=filtered_df, table_name=content_table_name)
            self.write_ids_to_db(
                df=filtered_df,
                table_name=model_pred_table_name,
                index_name=content_index_name,
            )
            logger.info(f"Wrote {len(filtered_df)} records")

        except IntegrityError as e:
            logger.error(e)

        # finally:
        #     # There're max ~180 news per day, and the parser get's 50 at a time,
        #     # so it's fine to sleep for a quarter of a day a day
        #     # TODO: replace this with crontab service
        #     sleep(21600)


def main():
    """
    Creates and runs the crawler

    :return: None
    """
    # load project-wide params
    params: Dict[str, Any] = load_config_params()

    # load the spacy model
    spacy_model = spacy.load(params["crawler"]["spacy_model_name"])

    engine = get_db_connection_engine()
    crawler = Crawler(
        sqlalchemy_engine=engine, path_to_rss_feeds=params["crawler"]["path_to_feeds_list"], spacy_model=spacy_model
    )

    # run crawler specifying database params to write content to
    crawler.run(
        content_index_name=params["database"]["content_index_name"],
        content_table_name=params["database"]["content_table_name"],
        model_pred_table_name=params["database"]["model_pred_table_name"],
    )


if __name__ == "__main__":
    main()

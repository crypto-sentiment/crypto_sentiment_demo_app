from pathlib import Path
from time import sleep
from typing import Any, Dict, List

import feedparser
import langid
import pandas as pd
from mmh3 import hash as mmh3_hash
from sqlalchemy.engine.base import Engine

# from sqlalchemy.exc import IntegrityError
from tqdm import tqdm

from crypto_sentiment_demo_app.utils import (
    get_db_connection_engine,
    get_logger,
    insert_on_duplicate,
    load_config_params,
    tag_question_mark,
)

logger = get_logger(Path(__file__).name)


class Crawler:
    def __init__(self, sqlalchemy_engine: Engine, path_to_rss_feeds: str):
        """
        :param sqlalchemy_engine: SQLAlchemy engine to connect to a database
        :param path_to_rss_feeds: path to a file with a list of RSS feeds to parse
        """
        self.sqlalchemy_engine = sqlalchemy_engine
        self.path_to_rss_feeds = path_to_rss_feeds

    def parse_rss_feeds(self) -> pd.DataFrame:
        urls = self.__get_rss_urls(path_to_rss_feed_list=self.path_to_rss_feeds)
        ids, parsed_titles, sources, pub_times = [], [], [], []

        for url in tqdm(urls, total=len(urls)):
            feed: List[feedparser.util.FeedParserDict] = feedparser.parse(url)["entries"]
            for title_metadata in feed:
                # add only eng titles and without question marks
                if (langid.classify(title_metadata.title)[0] == "en") & (tag_question_mark(title_metadata.title)):
                    parsed_titles.append(title_metadata.title)
                    ids.append(mmh3_hash(title_metadata.title, seed=17))
                    if "summary_detail" in title_metadata.keys():
                        sources.append(title_metadata.summary_detail["base"])
                    else:
                        sources.append(title_metadata.title_detail["base"])
                    if "published" in title_metadata.keys():
                        pub_times.append(title_metadata.published)
                    else:
                        pub_times.append(None)
            logger.info(f"Parsed feed {url}")
        df = pd.DataFrame(
            {
                "title_id": ids,
                "title": parsed_titles,
                "source": sources,
                "pub_time": pub_times,
            }
        ).drop_duplicates(
            subset="title_id"
        )  # TODO resolve duplications better

        df.set_index("title_id", inplace=True)

        logger.info(df.head())
        return df

    @staticmethod
    def __get_rss_urls(path_to_rss_feed_list: str) -> List[str]:
        with open(path_to_rss_feed_list) as f:
            urls = [line.strip() for line in f.readlines()]
        return urls

    def write_news_to_db(self, df: pd.DataFrame, table_name: str):
        """
        Writes scraped content into a table

        :param df: a pandas DataFrame output by the `parse_bitcointicker` method
        :param table_name: table name to write data to
        :return: None
        """

        # Write news titles to the table
        df.to_sql(
            name=table_name, con=self.sqlalchemy_engine, if_exists="append", index=True, method=insert_on_duplicate
        )

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
        df[index_name] = df.index
        df[index_name].to_sql(
            name=table_name, con=self.sqlalchemy_engine, if_exists="append", index=False, method=insert_on_duplicate
        )

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

        # TODO: run with crontab instead
        while 1:
            df = self.parse_rss_feeds()

            logger.info(f"Crawled {len(df)} records")

            # try:
            if 1:
                self.write_news_to_db(df=df, table_name=content_table_name)
                self.write_ids_to_db(
                    df=df,
                    table_name=model_pred_table_name,
                    index_name=content_index_name,
                )
                logger.info(f"Wrote {len(df)} records")

            # TODO: fix duplicates better
            # except IntegrityError as e:
            #    logger.info(e)

            # finally:
            # There're max ~180 news per day, and the parser get's 50 at a time,
            # so it's fine to sleep for a quarter of a day a day
            sleep(21600)


def main():
    """
    Creates and runs the crawler

    :return: None
    """
    # load project-wide params
    params: Dict[str, Any] = load_config_params()

    engine = get_db_connection_engine()
    crawler = Crawler(
        sqlalchemy_engine=engine,
        path_to_rss_feeds=params["crawler"]["path_to_feeds_list"],
    )

    # run crawler specifying database params to write content to
    crawler.run(
        content_index_name=params["database"]["content_index_name"],
        content_table_name=params["database"]["content_table_name"],
        model_pred_table_name=params["database"]["model_pred_table_name"],
    )


if __name__ == "__main__":
    main()

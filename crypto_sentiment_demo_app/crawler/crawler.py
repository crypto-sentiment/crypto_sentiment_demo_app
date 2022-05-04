from time import sleep
from typing import Any, Dict

import pandas as pd
import requests
from bs4 import BeautifulSoup
from mmh3 import hash as mmh3_hash
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import IntegrityError

from crypto_sentiment_demo_app.utils import get_db_connection_engine, load_config_params


class BitcointickerCrawler:
    def __init__(self, sqlalchemy_engine: Engine, url: str):
        """

        :param sqlalchemy_engine: SQLAlchemy engine to connect to a database
        :param url: URL to scrape, this crawler only works with "https://bitcointicker.co/news/"
        """
        self.url = url
        self.sqlalchemy_engine = sqlalchemy_engine

    def parse_bitcointicker(self) -> pd.DataFrame:
        """
        Parse 50 latest news and return a dataframe with 50 rows and columns:
        title_id, title, source, pub_time (these are hardcoded).

        :return: a pandas DataFrame
        """
        page = requests.get(self.url)
        soup_object = BeautifulSoup(page.content, "html.parser")

        ids, parsed_titles, sources, pub_times = [], [], [], []

        # getting titles and sources
        for el in soup_object.find_all("div", attrs={"style": "overflow:hidden;"}):
            elem_text = el.get_text()
            title = elem_text.split(" - ")[0].strip()
            source = elem_text.split(" - ")[-1].strip()
            parsed_titles.append(title)
            sources.append(source)
            ids.append(mmh3_hash(title, seed=17))  # strange, Python hashes are different from time to time

        # getting publication times
        for el in soup_object.find_all("div", attrs={"style": "margin-left:30px"}):
            elem_text = el.get_text()
            if "Posted" in elem_text:  # e.g. "Posted: 2022-04-15 06:00:19\n0 Comments"
                pub_time = elem_text.strip().split("\n")[0].replace("Posted:", "").strip()
                pub_times.append(pub_time)

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

        # TODO apply filters
        pass

        df.set_index("title_id", inplace=True)
        return df

    def write_news_to_db(self, df: pd.DataFrame, table_name: str):
        """
        Writes scraped content into a table

        :param df: a pandas DataFrame output by the `parse_bitcointicker` method
        :param table_name: table name to write data to
        :return: None
        """

        # Write news titles to the table
        df.to_sql(name=table_name, con=self.sqlalchemy_engine, if_exists="append", index=True)

    def write_ids_to_db(self, df: pd.DataFrame, index_name: str, table_name: str):
        """
        Writes news IDs into a table for model predictions to be furtherpicked up by the
        `model_scorer` service.

        :param df: a pandas DataFrame output by the `parse_bitcointicker` method
        :param index_name: index name of a table to write data to
        :param table_name: table name to write IDs to
        :return: None
        """

        # write news title IDs to a table for predictions
        df[index_name] = df.index
        df[index_name].to_sql(name=table_name, con=self.sqlalchemy_engine, if_exists="append", index=False)

    def run(self, content_index_name: str, content_table_name: str, model_pred_table_name: str):
        """
        Runs the crawler

        :param content_index_name: index name of a table to write data to
        :param content_table_name: table name to write content to
        :param model_pred_table_name: table name to write IDs to
        :return: None
        """

        # TODO: run with crontab instead
        while 1:
            df = self.parse_bitcointicker()

            try:
                self.write_news_to_db(df=df, table_name=content_table_name)
                self.write_ids_to_db(df=df, table_name=model_pred_table_name, index_name=content_index_name)
                print(f"Wrote {len(df)} records")  # TODO: set up logging

                # There're max ~180 news per day, and the parser get's 50 at a time,
                # so it's fine to sleep for a quarter of a day a day
                sleep(21600)

            # TODO: fix duplicates better
            except IntegrityError:
                pass


def main():
    """
    Creates and runs the crawler

    :return: None
    """
    # load project-wide params
    params: Dict[str, Any] = load_config_params()

    engine = get_db_connection_engine()
    crawler = BitcointickerCrawler(sqlalchemy_engine=engine, url=params["crawler"]["url"])

    # run crawler specifying database params to write content to
    crawler.run(
        content_index_name=params["database"]["content_index_name"],
        content_table_name=params["database"]["content_table_name"],
        model_pred_table_name=params["database"]["model_pred_table_name"],
    )


if __name__ == "__main__":
    main()

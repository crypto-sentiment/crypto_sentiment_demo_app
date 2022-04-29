import mmh3
import pandas as pd
import requests
from bs4 import BeautifulSoup
from crypto_sentiment_demo_app.utils import get_db_connection_engine
from sqlalchemy.engine.base import Engine


class BitcointickerCrawler:
    def __init__(self, sqlalchemy_engine: Engine):
        # this url is hardcoded
        self.url = "https://bitcointicker.co/news/"
        self.sqlalchemy_engine = sqlalchemy_engine

    def parse_bitcointicker(self) -> pd.DataFrame:
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
            ids.append(mmh3.hash(title, seed=17))  # TODO strange, hashes are different from time to time

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

    def write_news_to_db(self, df: pd.DataFrame, table_name="news_titles"):
        # TODO read table name from configs
        # Write news titles to the table
        df.to_sql(name=table_name, con=self.sqlalchemy_engine, if_exists="append", index=True)

    def write_ids_to_db(self, df: pd.DataFrame, index_name="title_id", table_name="model_predictions"):
        # TODO read table name from configs
        # write news title IDs to a table for predictions
        df[index_name] = df.index
        df[index_name].to_sql(name=table_name, con=self.sqlalchemy_engine, if_exists="append", index=False)


if __name__ == "__main__":

    engine = get_db_connection_engine()
    crawler = BitcointickerCrawler(sqlalchemy_engine=engine)

    df = crawler.parse_bitcointicker()
    crawler.write_news_to_db(df=df, table_name="news_titles")
    crawler.write_ids_to_db(df=df, table_name="model_predictions", index_name="title_id")

    print(f"Wrote {len(df)} records")

from pathlib import Path

import click
import pandas as pd
import pangres
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import ProgrammingError

from crypto_sentiment_demo_app.utils import get_db_connection_engine, get_logger

engine = get_db_connection_engine()
logger = get_logger(Path(__file__).name)


@click.command()
@click.option("--path_to_csv", help="Path to a CSV file to write to a database.")
@click.option("--table_name", help="Table name to write data into.")
@click.option("--index_col_name", default="title_id", help="Index column name")
def write_df_to_db(path_to_csv: str, table_name: str, engine: Engine = engine, index_col_name: str = "title_id"):
    """
    Writes scraped content into a table.
    This is a naive implementation: columns in the CSV file must match table columns in `table_name` exactly.

    :param path_to_csv: Path to a CSV file to write to a database
    :param table_name: table name to write data into
    :param engine: connection engine object
    :return: None
    """

    # pandas `to_sql` doesn't yet support updating records ("upsert")
    # https://github.com/pandas-dev/pandas/issues/15988
    # hence using Pangres upsert https://github.com/ThibTrip/pangres/wiki/Upsert

    try:
        df = pd.read_csv(path_to_csv)
        df[index_col_name] = df.index
        df.set_index(index_col_name, inplace=True, drop=True)  # pangres obliges a df to have an index name provided
        logger.info(df.head(2))
        pangres.upsert(df=df, con=engine, table_name=table_name, if_row_exists="update")
    except ProgrammingError:
        logger.info("Column names don't match")


if __name__ == "__main__":
    write_df_to_db()

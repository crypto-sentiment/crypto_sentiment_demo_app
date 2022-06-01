import pandas as pd
import pangres

from crypto_sentiment_demo_app.utils import get_db_connection_engine


def read_data_from_db() -> pd.DataFrame:
    """Read data from db.

    :return: dataframe with data from db
    """
    sqlalchemy_engine = get_db_connection_engine()

    query = """
    SELECT news_titles.title,
        model_predictions.title_id,
        model_predictions.negative,
        model_predictions.neutral,
        model_predictions.positive,
        model_predictions.predicted_class
    FROM news_titles
    INNER JOIN model_predictions
    ON news_titles.title_id = model_predictions.title_id
    WHERE  predicted_class IS NOT NULL;
    """

    df = pd.read_sql_query(query, con=sqlalchemy_engine)

    return df


def write_data_to_db(df: pd.DataFrame, table_name: str):
    """
    Writes exported samples into a table

    :param df: a pandas DataFrame output by the label studio export method
    :param table_name: table name to write data to
    """
    sqlalchemy_engine = get_db_connection_engine()

    # Write news titles to the table
    df.set_index("title_id", inplace=True)
    pangres.upsert(df=df, con=sqlalchemy_engine, table_name=table_name, if_row_exists="update")

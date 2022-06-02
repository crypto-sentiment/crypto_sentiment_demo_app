import pandas as pd
import pangres

from crypto_sentiment_demo_app.utils import get_db_connection_engine


def read_data_from_db() -> pd.DataFrame:
    """Read data from db.

    :return: dataframe with data from db
    """
    sqlalchemy_engine = get_db_connection_engine()

    read_query = """
    SELECT news_titles.title,
        model_predictions.title_id,
        model_predictions.negative,
        model_predictions.neutral,
        model_predictions.positive,
        model_predictions.predicted_class
    FROM news_titles
    INNER JOIN model_predictions
    ON news_titles.title_id = model_predictions.title_id
    WHERE  predicted_class IS NOT NULL AND is_annotating = False;
    """

    df = pd.read_sql_query(read_query, con=sqlalchemy_engine)

    return df


def write_data_to_db(df: pd.DataFrame, table_name: str):
    """Write exported samples into a table.

    :param df: a pandas DataFrame output by the label studio export method
    :param table_name: table name to write data to
    """
    sqlalchemy_engine = get_db_connection_engine()

    # Write news titles to the table
    df.set_index("title_id", inplace=True)
    pangres.upsert(df=df, con=sqlalchemy_engine, table_name=table_name, if_row_exists="update")


def set_annotation_flag(df: pd.DataFrame):
    """Update model_predictions table.

    Set is_annotating to True for the given samples.

    :param df: set is_annotating = True for that samples
    """
    sqlalchemy_engine = get_db_connection_engine()

    title_ids = df["title_id"].values
    insert_str = ",".join([str(title_id) for title_id in title_ids])

    update_query = f"""
    UPDATE model_predictions SET is_annotating = True
    WHERE title_id IN ({insert_str});
    """
    sqlalchemy_engine.execute(update_query)

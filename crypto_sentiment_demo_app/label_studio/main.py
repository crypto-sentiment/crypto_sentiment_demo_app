import argparse

import pandas as pd

from crypto_sentiment_demo_app.label_studio.label_studio import LabelStudioProject
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
    df["model_score"] = df[["positive", "negative", "neutral"]].max(axis=1)

    return df


def write_data_to_db(df: pd.DataFrame, table_name: str):
    """
    Writes exported samples into a table

    :param df: a pandas DataFrame output by the label studio export method
    :param table_name: table name to write data to
    :return: None
    """
    sqlalchemy_engine = get_db_connection_engine()

    # Write news titles to the table
    df.to_sql(name=table_name, con=sqlalchemy_engine, if_exists="append", index=False)


parser = argparse.ArgumentParser()
parser.add_argument("--mode", type=str, default="import", choices=["import", "export"])
parser.add_argument("--project_title", type=str, default="Crypto Sentiment project")
parser.add_argument("--api_key", type=str, required=True)
parser.add_argument("--label_studio_url", type=str, required=True)

if __name__ == "__main__":
    args = parser.parse_args()

    label_studio = LabelStudioProject(
        api_key=args.api_key, label_studio_url=args.label_studio_url, project_title=args.project_title
    )

    if args.mode == "import":
        data = read_data_from_db()

        label_studio.import_tasks(data, model_score_column_name="model_score")

    elif args.mode == "export":
        tasks: pd.DataFrame = label_studio.export_tasks(export_type="JSON_MIN")

        # print(f"tasks: {tasks}")
        if len(tasks) != 0:
            write_data_to_db(tasks, "labeled_titles")

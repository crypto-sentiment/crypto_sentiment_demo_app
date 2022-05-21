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


parser = argparse.ArgumentParser()
parser.add_argument("--mode", type=str, default="import", choices=["import", "export"])
parser.add_argument("--project_title", type=str, default="Crypto Sentiment project")

if __name__ == "__main__":
    args = parser.parse_args()

    label_studio = LabelStudioProject(args.project_title)

    if args.mode == "import":
        data = read_data_from_db()

        label_studio.import_tasks(data, model_score_column_name="model_score")

    elif args.mode == "export":
        tasks = label_studio.export_tasks(export_type="JSON")

        print(f"tasks: {tasks[:1]}")

    # if args.mode == "create":
    #     project = create_project(ls, args.project_title)

    #     import_tasks(project)
    # elif args.mode == "append":
    #     projects = ls.get_projects()

    #     selected_project = None
    #     for project in projects:
    #         if project.params["title"] == args.project_title:
    #             selected_project = project
    #             break

    #     if selected_project is None:
    #         raise ValueError(f"Project with title: {args.title} not found! You should create it before append tasks")

    #     import_tasks(selected_project)

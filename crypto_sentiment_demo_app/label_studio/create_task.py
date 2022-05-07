import argparse
import os
from typing import Any, Dict, List

import pandas as pd
from label_studio_sdk import Client, Project

from crypto_sentiment_demo_app.utils import get_db_connection_engine


def read_data_from_db() -> pd.DataFrame:
    """Read data from db.

    :return: dataframe with data from db
    """
    sqlalchemy_engine = get_db_connection_engine()

    query = """
    SELECT news_titles.title,
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


def collect_tasks(content_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Create labelling tasks.

    :param content_df: dataframe with samples from db
    :return: list of tasks in the format supported by label studio
    """
    tasks: List[Dict[str, Any]] = []
    predicted_mapping = {0: "Negative", 1: "Neutral", 2: "Positive"}

    for _, row in content_df.iterrows():
        task = {
            "data": {"reviewText": row["title"]},
            "predictions": [
                {
                    "result": [
                        {
                            "from_name": "sentiment",
                            "to_name": "title",
                            "type": "choices",
                            "readonly": False,
                            "hidden": False,
                            "value": {"choices": [predicted_mapping[row["predicted_class"]]]},
                        }
                    ],
                    "score": row["model_score"],
                }
            ],
        }

        tasks.append(task)

    return tasks


def create_project(client: Client, project_title: str) -> Project:
    """Create label studio project.

    :param client: label studio client
    :param project_title: title of the project
    :return: created label studio project
    """
    project = client.start_project(
        title=project_title,
        label_config="""
        <View>
        <Header value="Choose text sentiment:"/>
        <Text name="title" value="$reviewText"/>
        <Choices name="sentiment" toName="title" choice="single" showInline="true">
            <Choice value="Positive"/>
            <Choice value="Negative"/>
            <Choice value="Neutral"/>
        </Choices>
        </View>
        """,
    )

    return project


def import_tasks(project: Project) -> None:
    """Import tasks into label studio project.

    :param project: import tasks to that project
    """
    content_df = read_data_from_db()

    # Model score is required for active learning
    content_df["model_score"] = content_df[["positive", "negative", "neutral"]].max(axis=1)

    tasks = collect_tasks(content_df)

    project.import_tasks(tasks)


parser = argparse.ArgumentParser()
parser.add_argument("--mode", type=str, default="create", choices=["create", "append"])
parser.add_argument("--project_title", type=str, default="Crypto Sentiment project")

if __name__ == "__main__":
    args = parser.parse_args()

    LABEL_STUDIO_URL = os.environ.get("LABEL_STUDIO_URL")
    API_KEY = os.environ.get("API_KEY")

    ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)

    conn_check: Dict[str, str] = ls.check_connection()
    if conn_check["status"] != "UP":
        raise ValueError("Cannot connect to label studio, check LABEL_STUDIO_URL and API_KEY env variables.")

    if args.mode == "create":
        project = create_project(ls, args.project_title)

        import_tasks(project)
    elif args.mode == "append":
        projects = ls.get_projects()

        selected_project = None
        for project in projects:
            if project.params["title"] == args.project_title:
                selected_project = project
                break

        if selected_project is None:
            raise ValueError(f"Project with title: {args.title} not found! You should create it before append tasks")

        import_tasks(selected_project)

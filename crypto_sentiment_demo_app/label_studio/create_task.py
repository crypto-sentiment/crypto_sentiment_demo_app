# Import the SDK and the client module
from typing import Any, Dict, List

import pandas as pd
from label_studio_sdk import Client

from crypto_sentiment_demo_app.utils import get_db_connection_engine

LABEL_STUDIO_URL = ""
API_KEY = ""


def read_data_from_db() -> pd.DataFrame:
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
    tasks = []
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


def main():
    # Connect to the Label Studio API and check the connection
    ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
    print(ls.check_connection())

    project = ls.start_project(
        title="Crypto Sentiment project",
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

    content_df = read_data_from_db()
    content_df["model_score"] = content_df[["positive", "negative", "neutral"]].max(axis=1)
    print(content_df.head())

    tasks = collect_tasks(content_df)

    project.import_tasks(tasks)


if __name__ == "__main__":
    main()

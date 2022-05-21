import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

import pandas as pd
import requests
from label_studio_sdk import Client, Project

from crypto_sentiment_demo_app.utils import get_label_studio_endpoint


class LabelStudioProject:
    def __init__(self, project_title: str) -> None:
        LABEL_STUDIO_URL = os.environ.get("LABEL_STUDIO_URL")
        self.API_KEY = os.environ.get("API_KEY")

        self.client = Client(url=LABEL_STUDIO_URL, api_key=self.API_KEY)

        conn_check: Dict[str, str] = self.client.check_connection()
        if conn_check["status"] != "UP":
            raise ValueError("Cannot connect to label studio, check LABEL_STUDIO_URL and API_KEY env variables.")

        self.project = self._create_project(project_title)

    def _create_project(self, project_title: str) -> Project:
        """Create label studio project.

        :param client: label studio client
        :param project_title: title of the project
        :return: created label studio project
        """

        existing_projects = self.client.get_projects()

        for project in existing_projects:
            if project.params["title"] == project_title:
                return project

        project = self.client.start_project(
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

    def _collect_tasks_from_df(self, content_df: pd.DataFrame, model_score_column_name: str) -> List[Dict[str, Any]]:
        """Create labelling tasks.

        :param content_df: dataframe with samples from db
        :return: list of tasks in the format supported by label studio
        """
        tasks: List[Dict[str, Any]] = []
        predicted_mapping = {0: "Negative", 1: "Neutral", 2: "Positive"}

        if "predicted_class" not in content_df.columns or model_score_column_name not in content_df.columns:
            raise ValueError(
                f"Dataframe with samples should contain 'predicted_class' and {model_score_column_name} columns"
            )

        for _, row in content_df.iterrows():
            task = {
                "data": {
                    "reviewText": row["title"],
                    "title_id": row["title_id"],
                },
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
                        "score": row[model_score_column_name],
                    }
                ],
            }

            tasks.append(task)

        return tasks

    def import_tasks(self, data: pd.DataFrame, model_score_column_name: str = "model_score"):

        existing_tasks = self.project.get_tasks()

        # Remove existing tasks from the passed data
        # This could be very slow if the project has a lot of tasks
        existing_tasks_ids = [task["data"]["title_id"] for task in existing_tasks]
        data = data.loc[~data["title_id"].isin(existing_tasks_ids)]

        if len(data) != 0:

            tasks: List[Dict[str, Any]] = self._collect_tasks_from_df(data, model_score_column_name)

            self.project.import_tasks(tasks)

    def _delete_labelled_tasks(self):
        labeled_tasks_ids = self.project.get_labeled_tasks_ids()

        def delete_task(url: str):
            return requests.delete(
                url,
                headers={"Authorization": f"Token {self.API_KEY}", "content-Type": "application/json"},
            )

        list_of_urls = [get_label_studio_endpoint(f"api/tasks/{id}") for id in labeled_tasks_ids]

        num_workers = os.cpu_count() // 2
        with ThreadPoolExecutor(max_workers=num_workers) as pool:
            response_list = list(pool.map(delete_task, list_of_urls))

        print(f"response_list: {response_list}")

    def export_tasks(self, export_type: str):
        export_tasks = self.project.export_tasks(export_type)

        self._delete_labelled_tasks()

        return export_tasks

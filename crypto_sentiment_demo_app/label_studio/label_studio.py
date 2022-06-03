import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

import pandas as pd
import requests
from dateutil import parser
from label_studio_sdk import Client, Project

from crypto_sentiment_demo_app.utils import get_label_studio_endpoint


class LabelStudioProject:
    """Label studio project. Imports and exports tasks.

    :param api_key: label studio api key (see Account and Setting)
    :param label_studio_url: service url
    :param project_title: title of the project
    """

    def __init__(self, api_key: str, label_studio_url: str, project_title: str) -> None:
        """Init Label studio project."""
        self.api_key = api_key
        self.project_title = project_title
        self.client = Client(url=label_studio_url, api_key=api_key)

        conn_check: Dict[str, str] = self.client.check_connection()
        if conn_check["status"] != "UP":
            raise ValueError("Cannot connect to the label studio, check label studio api key.")

        self.project = self._create_project(self.project_title)

    def _create_project(self, project_title: str) -> Project:
        """Create label studio project.

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

    def _collect_tasks_from_df(self, content_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Create labelling tasks.

        :param content_df: dataframe with samples from db
        :return: list of tasks in the format supported by label studio
        """
        tasks: List[Dict[str, Any]] = []
        predicted_mapping = {0: "Negative", 1: "Neutral", 2: "Positive"}

        if "predicted_class" not in content_df.columns:
            raise ValueError("Dataframe with samples should contain 'predicted_class' column")

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
                        "score": row["criterion_score"],
                    }
                ],
            }

            tasks.append(task)

        return tasks

    def import_tasks(self, data: pd.DataFrame):
        """Import tasks to the project.

        :param data: samples with titles to annotate
        """
        existing_tasks = self.project.get_tasks()

        # Remove existing tasks from the passed data
        # This could be very slow if the project has a lot of tasks
        existing_tasks_ids = [task["data"]["title_id"] for task in existing_tasks]
        data = data.loc[~data["title_id"].isin(existing_tasks_ids)]

        if len(data) != 0:
            tasks: List[Dict[str, Any]] = self._collect_tasks_from_df(data)

            self.project.import_tasks(tasks)

    def _remove_annotated_tasks(self):
        """Remove annotated tasks from the project."""
        labeled_tasks_ids = self.project.get_labeled_tasks_ids()

        def remove_task(url: str):
            return requests.delete(
                url,
                headers={"Authorization": f"Token {self.api_key}", "content-Type": "application/json"},
            )

        list_of_urls = [get_label_studio_endpoint(f"api/tasks/{id}") for id in labeled_tasks_ids]

        # That is really ugly and unreliable way to remove tasks.
        # But it seems there is no general way to remove multiple tasks at once using exiting python sdk or api.
        # https://github.com/heartexlabs/label-studio/issues/1597#issuecomment-940975350
        num_workers = os.cpu_count()  # take one thread per cpu
        with ThreadPoolExecutor(max_workers=num_workers) as pool:
            pool.map(remove_task, list_of_urls)

    def export_tasks(self, export_type: str, remove_tasks: bool = True) -> pd.DataFrame:
        """Export tasks from the project.

        Also removes exported tasks from the project if remove_tasks is True.

        :param export_type: export type format
        :param remove_tasks: whether to remove exporting tasks from the project
        :return: dataframe with exported tasks
        """
        export_tasks = self.project.export_tasks(export_type)

        export_data: Dict[str, list] = {"title_id": [], "label": [], "annot_time": []}

        labels_mapping: Dict[str, int] = {"Negative": 0, "Neutral": 1, "Positive": 2}

        for task in export_tasks:
            export_data["title_id"].append(task["title_id"])
            export_data["label"].append(labels_mapping[task["sentiment"]])

            timestamp = parser.parse(task["updated_at"]).strftime("%Y-%m-%d %H:%M:%S")
            export_data["annot_time"].append(timestamp)

        if remove_tasks:
            self._remove_annotated_tasks()

        return pd.DataFrame(export_data)

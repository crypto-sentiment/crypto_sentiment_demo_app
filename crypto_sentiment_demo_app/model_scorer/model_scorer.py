from time import sleep
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import requests
from sqlalchemy import text
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import IntegrityError

from crypto_sentiment_demo_app.utils import (
    get_db_connection_engine,
    get_model_inference_api_endpoint,
    load_config_params,
)


class ModelScorer:
    def __init__(
        self,
        sqlalchemy_engine: Engine,
        model_api_endpoint: str,
        model_classes: List[str],
    ):
        #
        self.sqlalchemy_engine = sqlalchemy_engine
        # this assumes that the endpoint is up and running
        self.model_api_endpoint = model_api_endpoint
        self.model_classes = model_classes

    def get_data_to_run_model(self) -> pd.DataFrame:
        query = """
        SELECT title_id,
               title
        FROM   news_titles
        WHERE  title_id IN (SELECT title_id
                    FROM   model_predictions
                    WHERE  predicted_class IS NULL);
        """

        df = pd.read_sql_query(query, con=self.sqlalchemy_engine).drop_duplicates(subset="title_id")

        return df

    def run_model_on_single_text(self, id: int, text: str) -> Dict[str, float]:
        response = requests.post(
            self.model_api_endpoint,
            headers={"Content-Type": "application/json"},
            json={"title": text},
        )

        pred_dict = response.json()
        pred_dict["title_id"] = id

        return pred_dict

    def run_model_on_dataframe(self, content_df: pd.DataFrame, text_field_name="title"):

        pred_dicts: List[dict] = []
        for _, row in content_df.iterrows():

            pred_dict = self.run_model_on_single_text(text=row[text_field_name], id=row["title_id"])
            pred_dicts.append(pred_dict)
        pred_df = pd.DataFrame(pred_dicts)

        pred_df["predicted_class"] = np.argmax(pred_df[self.model_classes].values, axis=1)
        pred_df.set_index("title_id", inplace=True)

        return pred_df

    def write_preds_to_db(self, pred_df: pd.DataFrame, table_name="model_predictions"):
        # TODO read table name from configs
        # Write predictions to the table
        pred_df.columns = [col.lower() for col in pred_df.columns]

        # TODO avoid hardcoded class names
        query = text(
            f"""
                                INSERT INTO {table_name} (title_id, negative, neutral, positive, predicted_class)
                                VALUES {','.join([str(i) for i in list(pred_df.to_records(index=True))])}
                                ON CONFLICT (title_id)
                                DO  UPDATE SET title_id=excluded.title_id,
                                               negative=excluded.negative,
                                               neutral=excluded.neutral,
                                               positive=excluded.positive,
                                               predicted_class=excluded.predicted_class

                         """
        )
        self.sqlalchemy_engine.execute(query)

    def run(self):

        # TODO: run with crontab instead
        while 1:

            try:
                df = self.get_data_to_run_model()

                if len(df):
                    pred_df = self.run_model_on_dataframe(df)
                    self.write_preds_to_db(pred_df)
                    print(f"Wrote predictions for {len(df)} records into model_predictions.")  # TODO: set up logging

                # There're max ~180 news per day, and the parser get's 50 at a time,
                # so it's fine to sleep for a quarter of a day a day
                sleep(21600)

            # TODO: fix duplicates better
            except IntegrityError:
                pass


def main():
    # load project-wide params
    params: Dict[str, Any] = load_config_params()

    engine = get_db_connection_engine()
    model_api_endpoint = get_model_inference_api_endpoint()
    model_scorer = ModelScorer(
        sqlalchemy_engine=engine,
        model_api_endpoint=model_api_endpoint,
        model_classes=params["data"]["class_names"],
    )

    model_scorer.run()


if __name__ == "__main__":
    main()

import pickle
from pathlib import Path
from typing import Any, Dict

import mlflow
import numpy as np
from skl2onnx import to_onnx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline

from crypto_sentiment_demo_app.utils import get_logger, timer

from .base import IModelTrain, TrainRegistry

logger = get_logger(Path(__file__).name)


@TrainRegistry.register("tf_idf")
class TfidfLogisticRegression(IModelTrain):
    """Logistic regression with tf-idf model.

    :param cfg: model config
    """

    def __init__(self, cfg: Dict[str, Any]) -> None:
        super().__init__(cfg)

        self.model_cfg = self.cfg["model"]
        self.model: Pipeline = self._initialize_model(self.model_cfg)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit model.

        :param X: train data
        :param y: train labels
        """
        
        self.train_sample = X[:1]
        self.model.fit(X, y)

        if self.model_cfg["cross_validation"]["cv_perform_cross_val"]:
            cross_val_params = self.model_cfg["cross_validation"]

            with timer("Cross-validation", logger=logger):
                skf = StratifiedKFold(
                    n_splits=cross_val_params["cv_n_splits"],
                    shuffle=cross_val_params["cv_shuffle"],
                    random_state=cross_val_params["cv_random_state"],
                )

                # Running cross-validation
                cv_results = cross_val_score(
                    estimator=self.model,
                    X=X,
                    y=y,
                    cv=skf,
                    n_jobs=cross_val_params["cv_n_jobs"],
                    scoring=cross_val_params["cv_scoring"],
                )

                avg_cross_score = round(100 * cv_results.mean(), 2)
                logger.info(
                    "Average cross-validation {}: {}%.".format(cross_val_params["cv_scoring"], avg_cross_score)
                )

    def _save_model(self, env: str = "dev"):
        if env == "dev":
            with open(self.model_cfg["checkpoint_path"], "wb") as f:
                pickle.dump(self.model, f)
        elif env == "prod":
            model_onnx = to_onnx(self.model, self.train_sample)
            mlflow.onnx.log_model(
                onnx_model=model_onnx,
                artifact_path="tf_idf",
                registered_model_name="tf_idf"
                )
            with open(self.model_cfg["path_to_model"], "wb") as f:
                f.write(model_onnx.SerializeToString())
        else:
            raise ValueError(f"Unknown env passed: expected one of ('dev', 'prod'), given: {env}")

    def save(self) -> None:
        """Save model.

        :param path: save path, defaults to None
        """

        self._save_model("dev")
        self._save_model("prod")

    def load(self) -> None:
        """Load model checkpoint.

        :param path: checkpoint path, defaults to None
        """

        with open(self.cfg["model_checkpoint"], "rb") as f:
            self.model = pickle.load(f)

    def _initialize_model(self, cfg: Dict[str, Any]) -> Pipeline:
        """Initializes the model, an Sklearn Pipeline with two steps: tf-idf and logreg.

        :param model_params: a dictionary read from the `config.yml` file, section "model"
        :return: an Sklearn Pipeline object
        """
        # initialize TfIdf, logreg, and the Pipeline with the params from a config file
        text_transformer = TfidfVectorizer(**cfg["tfidf"])

        logreg = LogisticRegression(**cfg["logreg"])

        model = Pipeline([("tfidf", text_transformer), ("logreg", logreg)])

        return model
    
    def enable_mlflow_logging(self) -> None:
        mlflow.set_experiment("tf_idf")
        mlflow.sklearn.autolog()

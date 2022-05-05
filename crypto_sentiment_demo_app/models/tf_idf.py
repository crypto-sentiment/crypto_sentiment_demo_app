from typing import Dict, Any, Iterable, Optional, cast
from crypto_sentiment_demo_app.models.base import ModelEngine, ModelsRegistry

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_score
from crypto_sentiment_demo_app.utils import get_logger, timer
from pathlib import Path
import pickle

logger = get_logger(Path(__file__).name)


@ModelsRegistry.register("tf_idf")
class TfidfLogisticRegression(ModelEngine):
    """Logistic regression with tf-idf model.

    :param cfg: model config
    """

    def __init__(self, cfg: Dict[str, Any]):
        """Init model."""
        self.cfg = cfg["model"]
        self.class_names = cfg["data"]["class_names"]
        self.model: Pipeline = self._initialize_model(self.cfg)

    def fit(self, X: Iterable, y: Iterable, *args: Any, **kwargs: Any) -> None:
        """Fit model.

        :param X: train data
        :param y: train labels
        """
        self.model.fit(X, y)

        if self.cfg["cross_validation"]["cv_perform_cross_val"]:
            cross_val_params = self.cfg["cross_validation"]

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
                print("Average cross-validation {}: {}%.".format(cross_val_params["cv_scoring"], avg_cross_score))

    def predict(self, input_text: str) -> Dict[str, str]:
        """Predict sentiment probabilitites for the input text.

        :param input_text: input text
        :return: dictionary mapping class names to predicted probabilities
        """
        prediction = self.model.predict_proba([input_text]).squeeze().round(self.cfg["inference"]["round_prob"])
        response_dict: Dict[str, str] = dict(zip(self.class_names, map(str, prediction.tolist())))

        return response_dict

    def save(self, path: Optional[str] = None) -> None:
        """Save model.

        :param path: save path, defaults to None
        """
        # TODO: replace with saving to MlFlow registry
        path_to_saved_model = cast(str, self.cfg["path_to_model"] or path)

        with open(path_to_saved_model, "wb") as f:
            pickle.dump(self.model, f)

    def load(self, path: Optional[str] = None) -> None:
        """Load model checkpoint.

        :param path: checkpoint path, defaults to None
        """
        path_to_saved_model = cast(str, self.cfg["path_to_model"] or path)

        # TODO: replace with loading from MlFlow registry
        with open(path_to_saved_model, "rb") as f:
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

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, Union, cast

import mlflow
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient
from onnxruntime import InferenceSession

from crypto_sentiment_demo_app.utils import get_logger

logger = get_logger(Path(__file__).name)


def load_mlflow_model(model_name: str, model_version: Union[str, int]):
    client = MlflowClient()
    model = client.get_registered_model(model_name)
    if model_version == "latest":
        model_version = model.latest_versions[0].version
    return mlflow.pyfunc.load_model(model_uri=f"models:/{model_name}/{model_version}")


def load_model_pred_func(model_cfg: Dict[str, Any]):
    model_name = model_cfg["name"]
    model_version = model_cfg["version"]

    try:
        session = load_mlflow_model(model_name=model_name, model_version=model_version)

        def pred_func(input_data):
            prediction = session.predict(input_data)
            prediction = list(prediction.values())
            return prediction

        logger.info(f"Successfully loaded model '{model_name}', version {model_version} from MLflow")
        return pred_func

    except MlflowException as exc:
        local_path = model_cfg["path_to_model"]
        logger.error(f"Coudn't load model from MLflow: {exc.message}")
        logger.info(f"Loading model from local path: {local_path}")

        session = InferenceSession(local_path)
        output_names = model_cfg["onnx_config"]["output_names"]

        def pred_func(input_data):
            return session.run(output_names=output_names, input_feed=input_data)

        logger.info(f"Successfully loaded model '{model_name}', version {model_version} from local path: {local_path}")
        return pred_func


class IModelInference(ABC):
    """Inference models interface."""

    def __init__(self, cfg: Dict[str, Any]) -> None:
        self.cfg = cfg

    @abstractmethod
    def predict(self, input_text: str) -> Dict[str, str]:
        """Predict sentiment probabilitites for the input text.

        :param input_text: input text
        :return: dictionary mapping class names to predicted probabilities
        """
        pass


class InferenceRegistry:
    """Inference models factory."""

    registry: Dict[str, IModelInference] = {}

    @classmethod
    def register(cls, name: str) -> Callable:
        def inner_wrapper(
            wrapped_class: IModelInference,
        ) -> IModelInference:

            if name in cls.registry:
                logger.info(f"Model {name} already exists. " "It will be replaced")

            cls.registry[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def get_model(cls, name: str, cfg: Dict[str, Any]) -> IModelInference:
        if name in cls.registry:
            return cast(Callable, cls.registry[name])(cfg)
        else:
            raise ValueError(f"There is no model: {name}, available: {cls.registry.keys()}")

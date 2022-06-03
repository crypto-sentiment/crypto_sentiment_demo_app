from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, cast

from crypto_sentiment_demo_app.utils import get_logger

logger = get_logger(Path(__file__).name)


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

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Iterable, Optional, cast
import pandas as pd


class ModelEngine(ABC):
    """Model abstract class."""

    @abstractmethod
    def fit(self, X: pd.Series, y: pd.Series, *args, **kwargs) -> None:
        """Fit model.

        :param X: train data
        :param y: train labels
        """
        pass

    @abstractmethod
    def predict(self, input_text: str) -> Dict[str, str]:
        """Predict sentiment probabilitites for the input text.

        :param input_text: input text
        :return: dictionary mapping class names to predicted probabilities
        """
        pass

    @abstractmethod
    def save(self, path: Optional[str] = None) -> None:
        """Save model.

        :param path: save path, defaults to None
        """
        pass

    @abstractmethod
    def load(self, path: Optional[str] = None) -> None:
        """Load model checkpoint.

        :param path: checkpoint path, defaults to None
        """
        pass


class ModelsRegistry:
    """Models factory."""

    registry: Dict[str, ModelEngine] = {}

    @classmethod
    def register(cls, name: str) -> Callable:
        """Register model.

        :param name: model name, note that config schould of the model schould have the same name
        :return: wrapper function that saves model in registry
        """

        def inner_wrapper(
            wrapped_class: ModelEngine,
        ) -> ModelEngine:
            if name in cls.registry:
                print(f"ModelEngine {name} already exists. " "It will be replaced")

            cls.registry[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def get_model(cls, name: str, cfg: Dict[str, Any]) -> "ModelEngine":
        """Get model by name.

        :param name: model name
        :param cfg: model config
        :raises ValueError: if there is no models with name in registry
        :return: model with ModelEngine interface
        """
        if name in cls.registry:
            return cast(Callable, cls.registry[name])(cfg)
        else:
            raise ValueError(f"There is no model: {name}, available: {cls.registry.keys()}")

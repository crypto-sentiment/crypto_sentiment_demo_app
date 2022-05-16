from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, cast

import numpy as np


class IModelTrain(ABC):
    """Model abstract class."""

    def __init__(self, cfg: Dict[str, Any]) -> None:
        self.cfg = cfg

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit model.

        :param X: train data
        :param y: train labels
        """
        pass

    @abstractmethod
    def save(self) -> None:
        """Save model."""
        pass

    @abstractmethod
    def load(self) -> None:
        """Load model."""
        pass


class TrainRegistry:
    registry: Dict[str, IModelTrain] = {}

    @classmethod
    def register(cls, name: str) -> Callable:
        def inner_wrapper(
            wrapped_class: IModelTrain,
        ) -> IModelTrain:

            if name in cls.registry:
                print(f"Model {name} already exists. " "It will be replaced")

            cls.registry[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def get_model(cls, name: str, cfg: Dict[str, Any]) -> IModelTrain:
        if name in cls.registry:
            return cast(Callable, cls.registry[name])(cfg)
        else:
            raise ValueError(f"There is no model: {name}, available: {cls.registry.keys()}")

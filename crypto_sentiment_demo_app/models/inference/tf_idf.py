from typing import Any, Dict

import numpy as np
from onnxruntime import InferenceSession

from .base import IModelInference, InferenceRegistry


@InferenceRegistry.register("tf_idf")
class TfidfLogisticRegressionInference(IModelInference):
    def __init__(self, cfg: Dict[str, Any]) -> None:
        super().__init__(cfg)

        self.model_cfg = self.cfg["model"]

        self.session = InferenceSession(self.model_cfg["path_to_model"])

    def predict(self, input_text: str) -> Dict[str, str]:
        """Predict sentiment probabilitites for the input text.

        :param input_text: input text
        :return: dictionary mapping class names to predicted probabilities
        """
        pred_onnx = self.session.run(None, {"X": np.array([input_text])})[1][0]

        response_dict = {k: round(v, self.model_cfg["inference"]["round_prob"]) for k, v in pred_onnx.items()}

        return response_dict

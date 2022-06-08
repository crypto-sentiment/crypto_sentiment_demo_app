from typing import Any, Dict

import numpy as np

from .base import IModelInference, InferenceRegistry, load_model_pred_func


@InferenceRegistry.register("tf_idf")
class TfidfLogisticRegressionInference(IModelInference):
    """Tf-idf logreg inference model.

    :param cfg: model config.
    """

    def __init__(self, cfg: Dict[str, Any]) -> None:
        """Init model."""
        super().__init__(cfg)

        self.model_cfg = self.cfg["model"]

        self.session = load_model_pred_func(self.model_cfg)

    def predict(self, input_text: str) -> Dict[str, str]:
        """Predict sentiment probabilitites for the input text.

        :param input_text: input text
        :return: dictionary mapping class names to predicted probabilities
        """
        pred_onnx = self.session({"X": np.asarray([input_text])})[1][0]

        response_dict = {k: round(v, self.model_cfg["inference"]["round_prob"]) for k, v in pred_onnx.items()}

        return response_dict
        

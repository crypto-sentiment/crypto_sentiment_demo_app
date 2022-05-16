from copy import deepcopy
from typing import Any, Dict

import numpy as np
from onnxruntime import InferenceSession

from crypto_sentiment_demo_app.models.utils import build_object

from .base import IModelInference, InferenceRegistry


@InferenceRegistry.register("bert")
class BertInference(IModelInference):
    """Bert inference model.

    :param cfg: model config
    """

    def __init__(self, cfg: Dict[str, Any]) -> None:
        """Init model."""
        super().__init__(cfg)

        self.model_cfg = self.cfg["model"]
        self.class_names = cfg["data"]["class_names"]
        self.tokenizer = build_object(self.model_cfg["tokenizer"], is_hugging_face=True)

        self.session = InferenceSession(self.model_cfg["path_to_model"])

    def predict(self, input_text: str) -> Dict[str, str]:
        """Predict sentiment probabilitites for the input text.

        :param input_text: input text
        :return: dictionary mapping class names to predicted probabilities
        """
        tokenizer_call_params = deepcopy(self.model_cfg["tokenizer"]["call_params"])
        if "return_tensors" in tokenizer_call_params:
            del tokenizer_call_params["return_tensors"]

        inputs = self.tokenizer(input_text, return_tensors="np", **tokenizer_call_params)

        outputs = self.session.run(output_names=["logits"], input_feed=dict(inputs))[0].squeeze()

        predicted_probs = np.exp(outputs) / np.sum(np.exp(outputs), axis=0)

        response_dict = dict(zip(self.class_names, map(str, predicted_probs.tolist())))

        return response_dict

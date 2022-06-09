from copy import deepcopy
from typing import Any, Callable, Dict

import numpy as np

from crypto_sentiment_demo_app.models.utils import build_object

from .base import IModelInference, InferenceRegistry, load_model_pred_func


def log_sum_exp_softmax(x: np.ndarray) -> np.ndarray:
    c = np.max(x)

    return np.exp(x - np.log(np.exp(x - c).sum()) - c)


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
        self.tokenizer = self.load_tokenizer()

        self.session = load_model_pred_func(self.model_cfg)

    def predict(self, input_text: str) -> Dict[str, str]:
        """Predict sentiment probabilitites for the input text.

        :param input_text: input text
        :return: dictionary mapping class names to predicted probabilities
        """
        inputs = self.tokenizer(input_text)

        outputs = self.session(input_data=dict(inputs))[0].squeeze()

        predicted_probs = log_sum_exp_softmax(outputs)

        response_dict = dict(zip(self.class_names, map(str, predicted_probs.tolist())))

        return response_dict

    def load_tokenizer(self) -> Callable:
        """Loads tokenizer."""
        tokenizer = build_object(self.model_cfg["tokenizer"], is_hugging_face=True)
        tokenizer_call_params = deepcopy(self.model_cfg["tokenizer"]["call_params"])
        tokenizer_call_params["return_tensors"] = "np"

        def tokenize_func(input_text):
            return tokenizer(input_text, **tokenizer_call_params)

        return tokenize_func

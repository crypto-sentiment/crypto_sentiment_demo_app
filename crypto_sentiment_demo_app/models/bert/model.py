from typing import Any, Dict, Iterable, Optional

import torch
from crypto_sentiment_demo_app.models.base import ModelEngine, ModelsRegistry
from torch.nn import functional as F
from .pipeline import SentimentPipeline
from .utils import build_object


@ModelsRegistry.register("bert")
class Bert(ModelEngine):
    def __init__(self, cfg: Dict[str, Any]):

        self.cfg = cfg["model"]
        self.class_names = cfg["data"]["class_names"]

        if self.cfg["device"] == "gpu" and not torch.cuda.is_available():
            self.device = torch.device("cpu")
        else:
            self.device = torch.device(self.cfg["device"])

        self.tokenizer = build_object(self.cfg["tokenizer"], is_hugging_face=True)

    def fit(self, X: Iterable, y: Iterable, *args, **kwargs) -> None:
        pass

    @torch.no_grad()
    def predict(self, input_text: str) -> Dict[str, str]:

        encodings = self.tokenizer([input_text], **self.cfg["tokenizer"]["call_params"])

        item = {
            key: torch.tensor(val, device=self.device) for key, val in encodings.items()
        }

        logits = self.model.model(**item).logits

        prediction = F.softmax(logits, dim=-1).cpu().numpy().squeeze()
        response_dict = dict(zip(self.class_names, map(str, prediction.tolist())))

        return response_dict

    def save(self, path: Optional[str] = None) -> None:
        pass

    def load(self, path: Optional[str] = None) -> None:
        filepath = path or self.cfg["path_to_model"]
        self.model = SentimentPipeline.load_from_checkpoint(filepath, cfg=self.cfg)
        self.model = self.model.to(self.device)

import os
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import torch
from pytorch_lightning import Trainer, seed_everything
from pytorch_lightning.callbacks import ModelCheckpoint
from torch.nn import functional as F

from crypto_sentiment_demo_app.models.base import ModelEngine, ModelsRegistry

from .dataset import build_dataloaders, split_train_val
from .pipeline import MetricTracker, SentimentPipeline
from .utils import build_object


@ModelsRegistry.register("bert")
class Bert(ModelEngine):
    """Bert model. Wrapper for hugging face models.

    :param cfg: model config
    """

    def __init__(self, cfg: Dict[str, Any]):
        """Init model."""
        self.cfg = cfg["model"]
        self.class_names = cfg["data"]["class_names"]

        if self.cfg["device"] == "gpu" and not torch.cuda.is_available():
            self.device = torch.device("cpu")
        else:
            self.device = torch.device(self.cfg["device"])

        self.tokenizer = build_object(self.cfg["tokenizer"], is_hugging_face=True)

    def fit(self, X: Iterable, y: Iterable, *args, **kwargs) -> None:
        """Fit model.

        :param X: train data
        :param y: train labels
        """
        train_data, val_data, train_labels, val_labels = split_train_val(X, y)

        train_dataloader, val_dataloader = build_dataloaders(self.cfg, train_data, train_labels, val_data, val_labels)

        seed_everything(self.cfg["seed"])

        self.model = SentimentPipeline(self.cfg)

        metric_tracker = MetricTracker()

        checkpoint_path = os.path.dirname(self.cfg["path_to_model"])
        checkpoint_filename = Path(self.cfg["path_to_model"]).stem

        checkpoint_callback = ModelCheckpoint(
            save_top_k=1,
            monitor="val_acc",
            mode="max",
            dirpath=checkpoint_path,
            filename=checkpoint_filename,
        )

        gpus = 1 if self.device.type == "cuda" and torch.cuda.is_available() else 0

        self.trainer = Trainer(
            max_epochs=self.cfg["epochs"],
            gpus=gpus,
            callbacks=[metric_tracker, checkpoint_callback],
            num_sanity_val_steps=0,
            enable_checkpointing=True,
            logger=False,
        )

        self.trainer.fit(
            self.model,
            train_dataloaders=train_dataloader,
            val_dataloaders=val_dataloader,
        )

    @torch.no_grad()
    def predict(self, input_text: str) -> Dict[str, str]:
        """Predict sentiment probabilitites for the input text.

        :param input_text: input text
        :return: dictionary mapping class names to predicted probabilities
        """
        encodings = self.tokenizer([input_text], **self.cfg["tokenizer"]["call_params"])

        item = {key: torch.tensor(val, device=self.device) for key, val in encodings.items()}

        logits = self.model.model(**item).logits

        prediction = F.softmax(logits, dim=-1).cpu().numpy().squeeze()
        response_dict = dict(zip(self.class_names, map(str, prediction.tolist())))

        return response_dict

    def save(self, path: Optional[str] = None) -> None:
        """Save model.

        Not implemented, because pytorch lightning saves checkpoints during training.

        :param path: save path, defaults to None
        """
        # TODO: replace with saving to MlFlow registry
        pass

    def load(self, path: Optional[str] = None) -> None:
        """Load model checkpoint.

        :param path: checkpoint path, defaults to None
        """
        # TODO: replace with loading from MlFlow registry
        filepath = path or self.cfg["path_to_model"]
        self.model = SentimentPipeline.load_from_checkpoint(filepath, cfg=self.cfg)
        self.model = self.model.to(self.device)

from typing import Any, Dict

import pytorch_lightning as pl
import torch
from datasets import load_metric
from pytorch_lightning import Callback
from torch import Tensor
from transformers import get_scheduler
from transformers.modeling_outputs import SequenceClassifierOutput

from crypto_sentiment_demo_app.models.utils import build_object


class SentimentPipeline(pl.LightningModule):
    """Class for training text classification models"""

    def __init__(self, cfg: Dict[str, Any]):
        super().__init__()

        self.cfg = cfg
        self.model = build_object(cfg["model"], is_hugging_face=True)
        self.metric = load_metric("accuracy")

        self.tokenizer = build_object(cfg["tokenizer"], is_hugging_face=True)

    def configure_optimizers(self):
        optimizer = build_object(self.cfg["optimizer"], params=self.model.parameters())

        lr_scheduler = get_scheduler(
            optimizer=optimizer,
            num_training_steps=self.trainer.estimated_stepping_batches,
            **self.cfg["scheduler"]["params"],
        )

        scheduler = {
            "scheduler": lr_scheduler,
            "interval": "step",
            "frequency": 1,
        }

        return {"optimizer": optimizer, "lr_scheduler": scheduler}

    def forward(self, batch: Dict[str, Tensor]):
        encodings = self.tokenizer(batch["news"], **self.cfg["tokenizer"]["call_params"])

        item = {key: val.to(self.device) for key, val in encodings.items()}
        item["labels"] = batch["labels"]

        return self.model(**item)

    def training_step(self, batch: Dict[str, Tensor], batch_idx: int) -> Tensor:
        outputs: SequenceClassifierOutput = self.forward(batch)

        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1)
        self.metric.add_batch(predictions=predictions, references=batch["labels"])

        self.log(
            "train_acc",
            self.metric.compute()["accuracy"],
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            logger=False,
        )

        self.log(
            "train_loss",
            outputs.loss,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            logger=False,
        )

        return outputs.loss

    def validation_step(self, batch: Dict[str, Tensor], batch_idx: int) -> None:
        with torch.no_grad():
            outputs = self.forward(batch)

        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1)
        self.metric.add_batch(predictions=predictions, references=batch["labels"])

        self.log(
            "val_acc",
            self.metric.compute()["accuracy"],
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            logger=False,
        )

        self.log(
            "val_loss",
            outputs.loss,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            logger=False,
        )


class MetricTracker(Callback):
    def __init__(self):
        self.collection = {
            "train_loss": [],
            "val_loss": [],
            "train_acc": [],
            "val_acc": [],
        }

    def _log_metrics(self, trainer, stage: str = "train"):
        for key in (f"{stage}_acc", f"{stage}_loss"):
            self.collection[key].append(trainer.callback_metrics[key].item())

    def on_validation_epoch_end(self, trainer, module):
        self._log_metrics(trainer, "val")

    def on_train_epoch_end(self, trainer, module):
        self._log_metrics(trainer, "train")

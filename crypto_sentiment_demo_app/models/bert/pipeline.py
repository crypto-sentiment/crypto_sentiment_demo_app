from typing import Any, Dict

import pytorch_lightning as pl
import torch
from datasets import load_metric
from pytorch_lightning import Callback
from torch import Tensor
from transformers import get_scheduler

from .utils import build_object


class SentimentPipeline(pl.LightningModule):
    """Sentiment classification pipeline.

    :param cfg: model config.
    """

    def __init__(self, cfg: Dict[str, Any]):
        """Init pipeline."""
        super().__init__()

        self.cfg = cfg
        self.model = build_object(cfg["model"], is_hugging_face=True)
        self.metric = load_metric("accuracy")

        self.metrics = []

    def configure_optimizers(self):
        """Setup optimizers and schedulers."""
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
        """Forward pass."""
        return self.model(**batch)

    def training_step(self, batch: Dict[str, Tensor], batch_idx: int) -> Tensor:
        """Train step.

        :param batch: dict with data and labels
        :param batch_idx: batch index
        :return: batch loss
        """
        outputs = self.model(**batch)

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
        """Validation step.

        :param batch: dict with data and labels
        :param batch_idx: batch index
        """
        with torch.no_grad():
            outputs = self.model(**batch)

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
    """Callback to keep losses and metrics."""

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

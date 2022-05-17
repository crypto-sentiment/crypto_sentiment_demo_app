import os
import subprocess
from pathlib import Path
from typing import Any, Dict, cast

import numpy as np
import torch
import transformers
from pytorch_lightning import Trainer, seed_everything
from pytorch_lightning.callbacks import ModelCheckpoint
from transformers.modeling_utils import PreTrainedModel

from crypto_sentiment_demo_app.models.train.base import IModelTrain, TrainRegistry

from .dataset import build_dataloaders, split_train_val
from .pipeline import MetricTracker, SentimentPipeline

transformers.logging.set_verbosity_error()

os.environ["TOKENIZERS_PARALLELISM"] = "false"


@TrainRegistry.register("bert")
class Bert(IModelTrain):
    """Bert model. Wrapper for hugging face models.

    :param cfg: model config
    """

    def __init__(self, cfg: Dict[str, Any]):
        """Init model."""
        super().__init__(cfg)

        self.model_cfg = self.cfg["model"]
        self.class_names = self.cfg["data"]["class_names"]

        if self.model_cfg["device"] == "gpu" and not torch.cuda.is_available():
            self.device = torch.device("cpu")
        else:
            self.device = torch.device(self.model_cfg["device"])

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit model.

        :param X: train data
        :param y: train labels
        """
        seed_everything(self.model_cfg["seed"])

        train_data, val_data, train_labels, val_labels = split_train_val(X, y)

        train_dataloader, val_dataloader = build_dataloaders(
            self.model_cfg, train_data, train_labels, val_data, val_labels
        )

        self.model = SentimentPipeline(self.model_cfg)

        metric_tracker = MetricTracker()

        checkpoint_path = Path(self.model_cfg["checkpoint_path"]).parent
        checkpoint_filename = Path(self.model_cfg["checkpoint_path"]).stem

        checkpoint_callback = ModelCheckpoint(
            save_top_k=1,
            monitor="val_acc",
            mode="max",
            dirpath=checkpoint_path,
            filename=checkpoint_filename,
        )

        gpus = 1 if self.device.type == "cuda" and torch.cuda.is_available() else 0

        self.trainer = Trainer(
            max_epochs=self.model_cfg["epochs"],
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

    def save(self) -> None:
        """Save model."""
        save_dir = Path(self.model_cfg["path_to_model"]).parent
        filename = Path(self.model_cfg["path_to_model"]).stem

        pt_path = save_dir / f"{filename}.pt"
        onnx_path = save_dir / f"{filename}.onnx"
        onnx_path.touch(exist_ok=True)

        self.model = SentimentPipeline.load_from_checkpoint(self.model_cfg["checkpoint_path"], cfg=self.model_cfg)
        cast(PreTrainedModel, self.model.model).eval()
        cast(PreTrainedModel, self.model.tokenizer).save_pretrained(pt_path)
        cast(PreTrainedModel, self.model.model).save_pretrained(pt_path)

        # That hack is applied because there is no easy way to export huggingface model from the code
        subprocess.call(
            [
                "python3",
                "-m",
                "transformers.onnx",
                "--feature",
                "sequence-classification",
                "--model",
                pt_path,
                onnx_path,
            ]
        )

    def load(self) -> None:
        """Load model checkpoint."""
        self.model = SentimentPipeline.load_from_checkpoint(self.model_cfg["checkpoint_path"], cfg=self.model_cfg)

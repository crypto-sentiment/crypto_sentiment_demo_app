from typing import Any, Dict, Iterable, List, Tuple

import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset

from .utils import build_object


class FinNewsDataset(Dataset):
    """Pytorch dataset for the news data.

    :param encodings: titles encodings
    :param labels: sentiment labels
    """

    def __init__(self, encodings: Dict[str, Any], labels: List[int]):
        """Init dataset."""
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """Get sample.

        :param idx: sample index
        :return: dict with data and labels
        """
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])

        return item

    def __len__(self) -> int:
        """Return length of the dataset.

        :return: length of the dataset
        """
        return len(self.labels)


def prepare_dataset(cfg: Dict[str, Any], data: List[str], labels: List[int]) -> Dataset:
    """Preprocess titles.

    :param cfg: model/preporcess config
    :param data: list with titles
    :param labels: list with labels
    :return: pytorch dataset
    """
    tokenizer = build_object(cfg["tokenizer"], is_hugging_face=True)

    encodings = tokenizer(data, **cfg["tokenizer"]["call_params"])

    return FinNewsDataset(encodings, labels)


def split_train_val(X: pd.Series, y: pd.Series, test_size: float = 0.2) -> Tuple[list, ...]:
    """Split data on train and validation.

    :param X: series with titles
    :param y: series with labels
    :param test_size: val size, defaults to 0.2
    :return: tuple: (train_data, val_data, train_labels, val_labels)
    """
    labels_mapping: Dict[str, int] = {"Negative": 0, "Positive": 2, "Neutral": 1}
    y = y.map(labels_mapping)

    train_data, val_data, train_labels, val_labels = train_test_split(X, y, test_size=test_size)

    return (
        train_data.tolist(),
        val_data.tolist(),
        train_labels.tolist(),
        val_labels.tolist(),
    )


def build_dataloaders(
    cfg: Dict[str, Any],
    train_data: Iterable,
    train_labels: Iterable,
    val_data: Iterable,
    val_labels: Iterable,
) -> Tuple[DataLoader, DataLoader]:
    """Build dataloaders from train data and labels.

    :param cfg: model/preporcess config
    :param train_data: train data
    :param train_labels: train_labels
    :param val_data: val_data
    :param val_labels: val_labels
    :return: (train_dataloader, val_dataloader)
    """
    train_dataset = prepare_dataset(cfg, train_data, train_labels)
    val_dataset = prepare_dataset(cfg, val_data, val_labels)

    train_dataloader = DataLoader(train_dataset, batch_size=cfg["train_batch_size"], shuffle=True)
    val_dataloader = DataLoader(val_dataset, batch_size=cfg["val_batch_size"], shuffle=False)

    return train_dataloader, val_dataloader

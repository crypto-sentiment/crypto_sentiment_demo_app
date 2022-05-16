from typing import Any, Dict, Tuple

import numpy as np
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset


class FinNewsDataset(Dataset):
    def __init__(self, news: list, labels: list):
        self.news = news
        self.labels = labels

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        item = {"news": self.news[idx], "labels": torch.tensor(self.labels[idx])}

        return item

    def __len__(self) -> int:
        return len(self.labels)


def split_train_val(X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> Tuple[list, ...]:
    """Split data on train and validation.

    :param X: array with titles
    :param y: array with labels
    :param test_size: val size, defaults to 0.2
    :return: tuple: (train_data, val_data, train_labels, val_labels)
    """
    labels_mapping: Dict[str, int] = {"Negative": 0, "Positive": 2, "Neutral": 1}
    mapped_labels = list(map(lambda x: labels_mapping[x], y))

    train_data, val_data, train_labels, val_labels = train_test_split(X, mapped_labels, test_size=test_size)

    return (
        train_data.tolist(),
        val_data.tolist(),
        train_labels,
        val_labels,
    )


def build_dataloaders(
    cfg: Dict[str, Any],
    train_data: list,
    train_labels: list,
    val_data: list,
    val_labels: list,
) -> Tuple[DataLoader, DataLoader]:
    """Build dataloaders from train data and labels.

    :param cfg: model/preporcess config
    :param train_data: train data
    :param train_labels: train_labels
    :param val_data: val_data
    :param val_labels: val_labels
    :return: (train_dataloader, val_dataloader)
    """
    train_dataset = FinNewsDataset(train_data, train_labels)
    val_dataset = FinNewsDataset(val_data, val_labels)

    train_dataloader = DataLoader(
        train_dataset, batch_size=cfg["train_batch_size"], shuffle=True, num_workers=cfg["num_workers"]
    )
    val_dataloader = DataLoader(
        val_dataset, batch_size=cfg["val_batch_size"], shuffle=False, num_workers=cfg["num_workers"]
    )

    return train_dataloader, val_dataloader

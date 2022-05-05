import torch
from typing import Dict, Any, Tuple, Iterable

from torch.utils.data import Dataset, DataLoader
from .utils import build_object
from sklearn.model_selection import train_test_split
import pandas as pd


class FinNewsDataset(Dataset):
    def __init__(self, encodings: Dict[str, Any], labels: list):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])

        return item

    def __len__(self) -> int:
        return len(self.labels)


def prepare_dataset(cfg: Dict[str, Any], data: Iterable, labels: Iterable) -> Dataset:

    tokenizer = build_object(cfg["tokenizer"], is_hugging_face=True)

    encodings = tokenizer(data, **cfg["tokenizer"]["call_params"])

    return FinNewsDataset(encodings, labels)


def split_train_val(
    X: pd.Series, y: pd.Series, test_size: float = 0.2
) -> Tuple[list, ...]:

    labels_mapping: Dict[str, int] = {"Negative": 0, "Positive": 2, "Neutral": 1}
    y = y.map(labels_mapping)

    train_data, val_data, train_labels, val_labels = train_test_split(
        X, y, test_size=test_size
    )

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

    train_dataset = prepare_dataset(cfg, train_data, train_labels)
    val_dataset = prepare_dataset(cfg, val_data, val_labels)

    train_dataloader = DataLoader(
        train_dataset, batch_size=cfg["train_batch_size"], shuffle=True
    )
    val_dataloader = DataLoader(
        val_dataset, batch_size=cfg["val_batch_size"], shuffle=False
    )

    return train_dataloader, val_dataloader

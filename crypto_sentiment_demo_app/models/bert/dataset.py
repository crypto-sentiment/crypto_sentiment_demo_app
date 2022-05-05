import torch
from typing import Dict, Any, Tuple

from torch.utils.data import Dataset, DataLoader
from .utils import build_object
import pandas as pd
from sklearn.model_selection import train_test_split


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


def prepare_dataset(cfg: Dict[str, Any], data: list, labels: list) -> Dataset:

    tokenizer = build_object(cfg["tokenizer"], is_hugging_face=True)

    encodings = tokenizer(data, **cfg["tokenizer"]["call_params"])

    return FinNewsDataset(encodings, labels)


def split_train_val(
    dataset: pd.DataFrame, test_size: float = 0.2
) -> Tuple[pd.DataFrame, ...]:
    train_data, val_data, train_labels, val_labels = train_test_split(
        dataset["title"],
        dataset["label"],
        test_size=test_size,
        stratify=dataset["label"],
    )

    return train_data, val_data, train_labels, val_labels


def build_dataloaders(
    cfg: Dict[str, Any],
    train_data: pd.DataFrame,
    train_labels: pd.DataFrame,
    val_data: pd.DataFrame,
    val_labels: pd.DataFrame,
) -> Tuple[DataLoader, DataLoader]:

    train_dataset = prepare_dataset(cfg, train_data.tolist(), train_labels.tolist())
    val_dataset = prepare_dataset(cfg, val_data.tolist(), val_labels.tolist())

    train_dataloader = DataLoader(
        train_dataset, batch_size=cfg["train_batch_size"], shuffle=True
    )
    val_dataloader = DataLoader(
        val_dataset, batch_size=cfg["val_batch_size"], shuffle=False
    )

    return train_dataloader, val_dataloader

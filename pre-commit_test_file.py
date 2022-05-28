import numpy as np


def entropy(probs: np.ndarray) -> float:
    """very long docstring violating flake8 max line ------------------------------------------------------------------"""
    return (-probs * np.log2(probs)).sum()

from copy import deepcopy
from typing import Callable, Dict, cast

import pandas as pd

from crypto_sentiment_demo_app.utils import entropy


class Sampler:
    """Least confidence sampling strategy.

    :param num_samples: number of items to sample, defaults to 0
    """

    def __init__(self, num_samples: int = 0) -> None:
        """Init sampler."""
        self.num_samples = num_samples

    def get_samples(self, data: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError


class LeastConfidenceSampler(Sampler):
    """Least confidence sampling strategy.

    :param num_samples: number of items to sample, defaults to 0
    """

    def get_samples(self, data: pd.DataFrame) -> pd.DataFrame:
        """Select samples to pass for annotation.

        New samples are least confident predictions.

        :param data: data from where new chunk will be sampled
        :return: selected samples
        """
        # [num_samples, 1]
        predicted_label_prob = data[["positive", "negative", "neutral"]].max(axis=1)

        data_copy = deepcopy(data)
        data_copy["predicted_label_prob"] = predicted_label_prob

        new_samples = data_copy.sort_values("predicted_label_prob", ascending=True).head(self.num_samples)

        new_samples = new_samples.drop(columns=["predicted_label_prob"])

        return new_samples


class EntropySampler(Sampler):
    """Entropy based sampling strategy."""

    def get_samples(self, data: pd.DataFrame) -> pd.DataFrame:
        """Select samples to pass for annotation.

        New samples are the ones with the highest predictive entropy.

        :param data: data from where new chunk will be sampled
        :return: selected samples
        """

        prediction_probs = data[["positive", "negative", "neutral"]]
        # [num_samples, 1]
        pred_entropy = entropy(prediction_probs.squeeze())

        data_copy = deepcopy(data)
        data_copy["pred_entropy"] = pred_entropy

        new_samples = data_copy.sort_values("pred_entropy", ascending=False).head(self.num_samples)

        new_samples = new_samples.drop(columns=["pred_entropy"])

        return new_samples


SAMPLERS: Dict[str, object] = {"least_confidence": LeastConfidenceSampler, "entropy": EntropySampler}


def get_sampler(sampler_name: str, num_samples: int) -> Sampler:
    """Build selected sampler.

    :param sampler_name: sampler name
    :param num_samples: number of items to sample
    :return: selected sampler
    """
    if sampler_name in SAMPLERS:
        return cast(Callable, SAMPLERS[sampler_name])(num_samples=num_samples)
    else:
        raise ValueError(f"sampler name: {sampler_name} not found, {SAMPLERS.keys()} are available")

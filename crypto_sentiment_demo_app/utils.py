import datetime
import logging
import logging.config
import os
import re
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, cast

import numpy as np
import pytz
from dateutil import parser as dateutil_parser
from delorean import parse as delorean_date_parse
from dotenv import load_dotenv
from hydra import compose
from omegaconf import OmegaConf
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine

load_dotenv()


def get_project_root() -> Path:
    """
    Return a Path object pointing to the project root directory.

    :return: Path
    """
    return Path(__file__).parent.parent


def load_config_params(return_hydra_config: bool = False) -> Dict[str, Any]:
    """
    Loads global project configuration params defined in the `config.yaml` file.

    :return: a nested dictionary corresponding to the `config.yaml` file.
    """
    cfg = compose(config_name="config", return_hydra_config=return_hydra_config)

    return cast(Dict[str, Any], OmegaConf.to_container(cfg))


def get_logger(name) -> logging.Logger:
    """

    :param name: name – any string
    :return: Python logging.Logger object
    """

    params = load_config_params()
    log_config = params["logger"]
    logging.config.dictConfig(config=log_config)

    return logging.getLogger(name)


@contextmanager
def timer(name, logger):
    """
    A context manager to report running times.
    Example usage:
        ```
        with timer("Any comment here"):
            pass
        ```
    :param name: any string
    :param logger: logging object
    :return: None
    """
    t0 = time.time()
    yield
    logger.info(f"[{name}] done in {time.time() - t0:.0f} s")


def get_db_connection_engine(
    user: str = os.getenv("POSTGRES_USER"),
    pwd: str = os.getenv("POSTGRES_PASSWORD"),
    database: str = os.getenv("POSTGRES_DB"),
    host: str = os.getenv("POSTGRES_HOST"),
) -> Engine:
    conn_string = f"postgresql://{user}:{pwd}@{host}/{database}"

    engine = create_engine(conn_string)

    return engine


def get_model_inference_api_endpoint() -> str:
    params = load_config_params()

    inference_api_params = params["inference_api"]

    # hostname = inference_api_params["host_name"]
    hostname = os.getenv("HOST")
    port = inference_api_params["port"]
    endpoint_name = inference_api_params["endpoint_name"]

    return f"{hostname}:{port}/{endpoint_name}"


def get_label_studio_endpoint(endpoint_name: str) -> str:
    params = load_config_params()

    label_studio_params = params["label_studio_api"]

    hostname = label_studio_params["host_name"]
    port = label_studio_params["port"]

    return f"http://{hostname}:{port}/{endpoint_name}"


def entropy(probs: np.ndarray) -> float:
    """
    Calculates classic entropy given a vector of probabilities.
    :param probs: an array of probabilities
    :return: float
    """

    axis = 1 if probs.ndim == 2 else 0

    return (-probs * np.log2(probs)).sum(axis=axis)


def parse_time(ts: str, named_timezones=("EST", "GMT", "UTC")) -> datetime.datetime:
    """
    Parses a time string with either offsets like +0000 of timezones like EST, GMT, UTC.
    :param ts: a string formatted like 'Mon, 25 Apr 2022 13:47:46 +0000' or with time zone in the end
    :param named_timezones: a fixed tuple of timezones to map to those known to PyTZ
    :return: a timezone-aware datetime.datetime object
    """
    # if one of EST, GMT, UTC is specified as a timezone, parse it with dateutils
    tzinfos = {tz: pytz.timezone(tz) for tz in named_timezones}
    if ts[-3:] in named_timezones:
        return dateutil_parser.parse(ts, tzinfos=tzinfos)

    # if instead an offset is specified like +0100, we use the delorean parser
    elif re.match(pattern=r"[\+\-]\d{4}", string=ts[-5:]):
        return delorean_date_parse(ts).datetime

    # otherwise we return UTC time
    else:
        return delorean_date_parse(ts).datetime

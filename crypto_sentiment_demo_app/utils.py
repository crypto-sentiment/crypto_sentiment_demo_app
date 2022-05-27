import logging
import logging.config
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, cast

import numpy as np
from dotenv import load_dotenv
from hydra import compose
from omegaconf import OmegaConf
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import insert
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


def tag_question_mark(string):
    if "?" not in string:
        return True
    else:
        return False


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

    hostname = inference_api_params["host_name"]
    port = inference_api_params["port"]
    endpoint_name = inference_api_params["endpoint_name"]

    return f"http://{hostname}:{port}/{endpoint_name}"


def entropy(probs: np.ndarray) -> float:
    """
    Calculates classic entropy given a vector of probabilities.
    :param probs: an array of probabilities
    :return: float
    """
    return (-probs * np.log2(probs)).sum()


def insert_on_duplicate(table, conn, keys, data_iter):
    insert_stmt = insert(table.table).values(list(data_iter))
    on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(insert_stmt.inserted)
    conn.execute(on_duplicate_key_stmt)


if __name__ == "__main__":
    print(get_project_root().absolute())
    params = load_config_params()
    print(params)

import logging
import logging.config
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict

import yaml
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine


def get_project_root() -> Path:
    """
    Return a Path object pointing to the project root directory.

    :return: Path
    """
    return Path(__file__).parent.parent


def load_config_params() -> Dict[str, Any]:
    """
    Loads global project configuration params defined in the `config.yaml` file.

    :return: a nested dictionary corresponding to the `config.yaml` file.
    """
    project_root: Path = get_project_root()
    with open(project_root / "config.yml") as f:
        params: Dict[str, Any] = yaml.load(f, Loader=yaml.FullLoader)
    return params


def get_logger(name) -> logging.Logger:
    """

    :param name: name – any string
    :return: Python logging.Logger object
    """

    params = load_config_params()
    log_config = params["logging"]
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


def get_db_connection_engine() -> Engine:

    params = load_config_params()
    with open(params["database"]["path_to_connection_param_file"]) as f:
        conn_string = f.read().strip()
        engine = create_engine(conn_string)

    return engine


def get_model_inference_api_endpoint() -> str:

    params = load_config_params()
    hostname = params["model"]["inference_api_host_name"]
    port = params["model"]["inference_api_port"]
    endpoint_name = params["model"]["inference_api_endpoint_name"]

    return f"http://{hostname}:{port}/{endpoint_name}"


if __name__ == "__main__":
    print(get_project_root().absolute())
    params = load_config_params()
    print(params)

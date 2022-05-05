from typing import Any, Dict

from fastapi import FastAPI, HTTPException, status
from crypto_sentiment_demo_app.utils import load_config_params
from crypto_sentiment_demo_app.models import ModelsRegistry, ModelEngine
from .news import News
from copy import deepcopy
from crypto_sentiment_demo_app.utils import get_logger
from pathlib import Path

logger = get_logger(Path(__file__).name)


def load_model(params: Dict[str, Any]) -> ModelEngine:

    model_params = deepcopy(params)
    model_choice = model_params["hydra"]["runtime"]["choices"]["model"]
    del model_params["hydra"]

    model = ModelsRegistry.get_model(model_choice, model_params)

    model.load()

    logger.info("model_loaded")

    return model


params = load_config_params(return_hydra_config=True)

model: ModelEngine = load_model(params)


# initializing the API, see https://fastapi.tiangolo.com/tutorial/first-steps/
app = FastAPI()


# check if model is loaded correctly
@app.get("/health", status_code=status.HTTP_200_OK)
def is_model_loaded() -> bool:
    return model is not None


@app.get("/")
def get_classifier_details() -> Dict[str, Any]:
    """
    Gets classifier's name and model version by reading it from the config file.
    :return: Classifier's name and model version
    """

    logger.info(f"model_params: {params.keys()}")
    return {
        "name": params["model"]["name"],
        "model_version": params["model"]["version"],
    }


@app.post("/classify", status_code=200)
def classify_content(input_data: News) -> Dict[str, str]:
    """
    Gets a JSON with text fields, processes them, runs model prediction
    and returns the resulting predicted probabilities for each class.

    :param input_json: input JSON structured as {text_field_name: text_field_value},
                       e.g. {"title": "BTC drops by 10% this Friday"}

    :return: a Response with a dictionary mapping class names to predicted probabilities
    """

    text_field_name: str = params["data"]["text_field_name"]

    data_dict = input_data.dict()
    # logger.info(f"data_dict: {data_dict}")

    if text_field_name not in data_dict:
        raise HTTPException(
            status_code=404,
            detail=f"Item {text_field_name} not found, input items: {data_dict.keys()}",
        )

    response_dict = model.predict(data_dict.get(text_field_name, ""))

    # logger.info(f"response_dict: {response_dict}")

    return response_dict

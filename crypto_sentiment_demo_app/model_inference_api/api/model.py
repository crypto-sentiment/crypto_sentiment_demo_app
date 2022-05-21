from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, status

from crypto_sentiment_demo_app.models.inference import (
    IModelInference,
    InferenceRegistry,
)
from crypto_sentiment_demo_app.utils import get_logger, load_config_params

from .news import News

logger = get_logger(Path(__file__).name)


def load_model(params: Dict[str, Any]) -> IModelInference:
    """Load model from models registry based on the passed params.

    :param params: config
    :return: model with ModelEngine interface
    """
    model_params = deepcopy(params)
    model_choice = model_params["hydra"]["runtime"]["choices"]["model"]
    del model_params["hydra"]

    model = InferenceRegistry.get_model(model_choice, model_params)

    return model


params = load_config_params(return_hydra_config=True)

model: IModelInference = load_model(params)

app = FastAPI()


@app.get("/health", status_code=status.HTTP_200_OK)
def is_model_loaded() -> bool:
    """Check whether model was loaded.

    Need this to force other services wait until model will be loaded.
    """
    return model is not None


@app.get("/")
def get_classifier_details() -> Dict[str, Any]:
    """Gets classifier's name and model version by reading it from the config file.

    :return: Classifier's name and model version
    """
    logger.info(f"model_params: {params.keys()}")
    return {
        "name": params["model"]["name"],
        "model_version": params["model"]["version"],
    }


@app.post("/classify", status_code=200)
def classify_content(input_data: News) -> Dict[str, str]:
    """Get the input data and return model prediction.

    :param input_data: input News object structured as {text_field_name: text_field_value},
        e.g. {"title": "BTC drops by 10% this Friday"}
    :return: a Response with a dictionary mapping class names to predicted probabilities
    """
    text_field_name: str = params["data"]["text_field_name"]

    data_dict = input_data.dict()

    if text_field_name not in data_dict:
        raise HTTPException(
            status_code=404,
            detail=f"Item {text_field_name} not found, input items: {data_dict.keys()}",
        )

    response_dict = model.predict(data_dict.get(text_field_name, ""))

    return response_dict

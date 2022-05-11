import pickle
from typing import Any, Dict, List

from fastapi import FastAPI
from fastapi_health import health
from sklearn.pipeline import Pipeline

from crypto_sentiment_demo_app.utils import load_config_params

from .inference import model_inference

# loading project-wide configuration params
params: Dict[str, Any] = load_config_params()


# TODO move the following two methods to the model wrapper to be defined in model.py
# loading the model into memory
def load_model(model_path) -> Pipeline:
    with open(model_path, "rb") as f:
        model: Pipeline = pickle.load(f)
    return model


model: Pipeline = load_model(params["model"]["path_to_model"])


# check if model is loaded correctly
def is_model_loaded() -> bool:
    return model is not None


# initializing the API, see https://fastapi.tiangolo.com/tutorial/first-steps/
app = FastAPI()
app.add_api_route("/health", health([is_model_loaded]))


@app.get("/")
def get_classifier_details() -> Dict[str, Any]:
    """
    Gets classifier's name and model version by reading it from the config file.
    :return: Classifier's name and model version
    """

    return {
        "name": params["model"]["name"],
        "model_version": params["model"]["version"],
    }


@app.post("/classify", status_code=200)
def classify_content(input_json: Dict[str, str]) -> Dict[str, str]:
    """
    Gets a JSON with text fields, processes them, runs model prediction
    and returns the resulting predicted probabilities for each class.

    :param input_json: input JSON structured as {text_field_name: text_field_value},
                       e.g. {"title": "BTC drops by 10% this Friday"}

    :return: a Response with a dictionary mapping class names to predicted probabilities
    """

    # passing this both as arguments to the current function didn't work for me
    text_field_name: str = params["data"]["text_field_name"]
    class_names: List[str] = params["data"]["class_names"]

    # TODO implement error handling, see https://fastapi.tiangolo.com/tutorial/handling-errors/
    assert text_field_name in input_json

    response_dict = model_inference(
        model=model,
        input_text=input_json.get(text_field_name, ""),
        class_names=class_names,
    )

    return response_dict

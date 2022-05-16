from typing import Dict, List

import numpy as np
from sklearn.pipeline import Pipeline


def model_inference(model: Pipeline, input_text: str, class_names: List[str]) -> Dict[str, str]:

    """
    Run model inference with the given model

    :param model: Sklearn Pipeline defined in model.py
    :param input_text: any string
    :param class_names: a list of strings defining class names in the classification task
    :return: a dictionary with class names as keys and predicted scores as values.
    """

    # TODO apply processing, e.g. trimming up to `max_text_length_words` param
    pred_probs: np.array = model.predict_proba([input_text]).squeeze().round(4)
    response_dict: Dict[str, str] = dict(zip(class_names, map(str, pred_probs.tolist())))

    return response_dict

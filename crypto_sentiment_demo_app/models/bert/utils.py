from importlib import import_module
from typing import Any, Callable, Dict


def build_object(object_cfg: Dict[str, Any], is_hugging_face: bool = False, **kwargs: Dict[str, Any]) -> Callable:
    """Build object from config.

    Config schould have the following construction:

    class: <class name>
    params:
        <param name>: val

    params - constructor parameters.
    Also if kwargs is passed they will be added as constructor parameters.

    :param object_cfg: object config
    :param is_hugging_face: whether object is hugging face model, defaults to False
    :raises ValueError: if config doesn't contain class key
    :return: created object
    """
    if "class" not in object_cfg.keys():
        raise ValueError("class key schould be in config")

    if "params" in object_cfg.keys():
        params = object_cfg["params"]

        for key, val in params.items():
            kwargs[key] = val
    else:
        params = {}

    if is_hugging_face:
        return get_instance(object_cfg["class"]).from_pretrained(**kwargs)

    return get_instance(object_cfg["class"])(**kwargs)


def get_instance(object_path: str) -> Callable:
    """Return object instance.

    :param object_path: instance name, for example transformers.DistilBertTokenizerFast
    :return: object instance
    """
    module_path, class_name = object_path.rsplit(".", 1)
    module = import_module(module_path)

    return getattr(module, class_name)

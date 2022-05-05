from typing import Any, Dict, Callable
from importlib import import_module


def build_object(
    object_cfg: Dict[str, Any], is_hugging_face: bool = False, **kwargs: Dict[str, Any]
) -> Callable:
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

    module_path, class_name = object_path.rsplit(".", 1)
    module = import_module(module_path)

    return getattr(module, class_name)

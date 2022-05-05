from omegaconf import OmegaConf
from crypto_sentiment_demo_app.models.base import ModelsRegistry, ModelEngine
from typing import cast, Dict, Any
from hydra import compose
from crypto_sentiment_demo_app.train.read_data import read_train_data
from crypto_sentiment_demo_app.utils import get_project_root


def main():
    """Read config, train model and save checkpoint."""
    cfg = compose(config_name="config", return_hydra_config=True)
    model_choice = cfg.hydra.runtime.choices.model
    dict_cfg = cast(Dict[str, Any], OmegaConf.to_container(cfg))
    del dict_cfg["hydra"]

    model: ModelEngine = ModelsRegistry.get_model(model_choice, dict_cfg)

    project_root = get_project_root()
    cfg_data = dict_cfg["data"]
    path_to_data = project_root / cfg_data["path_to_data"] / cfg_data["train_filename"]

    train_df = read_train_data(path_to_data=path_to_data)
    train_texts = train_df[cfg_data["text_field_name"]]
    train_targets = train_df[cfg_data["label_field_name"]]

    model.fit(train_texts, train_targets)

    model.save(project_root / dict_cfg["model"]["path_to_model"])


if __name__ == "__main__":
    main()

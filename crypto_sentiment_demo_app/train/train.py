from typing import Any, Dict, cast

from hydra import compose
from omegaconf import OmegaConf
import mlflow

from crypto_sentiment_demo_app.models.train import IModelTrain, TrainRegistry
from crypto_sentiment_demo_app.train.read_data import read_train_data
from crypto_sentiment_demo_app.utils import get_project_root


def main():
    """Read config, train model and save checkpoint."""
    cfg = compose(config_name="config", return_hydra_config=True)
    model_choice = cfg.hydra.runtime.choices.model
    dict_cfg = cast(Dict[str, Any], OmegaConf.to_container(cfg))
    del dict_cfg["hydra"]

    model: IModelTrain = TrainRegistry.get_model(model_choice, dict_cfg)

    project_root = get_project_root()
    cfg_data = dict_cfg["data"]
    path_to_data = project_root / cfg_data["path_to_data"] / cfg_data["train_filename"]

    train_df = read_train_data(path_to_data=path_to_data)
    train_texts = train_df[cfg_data["text_field_name"]].values
    train_targets = train_df[cfg_data["label_field_name"]].values

    model.enable_mlflow_logging()
    with mlflow.start_run():
        model.fit(train_texts, train_targets)
        model.save()


if __name__ == "__main__":
    main()

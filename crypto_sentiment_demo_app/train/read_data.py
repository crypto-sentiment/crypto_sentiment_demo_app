from pathlib import Path

import pandas as pd


def read_train_data(path_to_data: Path) -> pd.DataFrame:
    """A custom function that reads training data from CSV files into Pandas DataFrames.

    Schould be replaced with finctuion that reads from db.

    :param path_to_data: path to a CSV file with training data
    :return: Dataframe with training data
    """

    # read the training set
    df = pd.read_csv(path_to_data)

    return df

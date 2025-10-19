import pandas as pd
import kagglehub
import os

# defining path for data import
path = kagglehub.dataset_download("max-mind/world-cities-database")

def import_data(path: str) -> pd.DataFrame:
    """Imports the world cities dataset from the specified directory.

    This function reads the 'worldcitiespop.csv' file from the given path
    and returns its content as a pandas DataFrame.

    Args:
        path (str): The directory path where the dataset is located.

    Returns:
        pd.DataFrame: A DataFrame containing the world cities data.
    """
    return pd.read_csv(os.path.join(path, 'worldcitiespop.csv'))
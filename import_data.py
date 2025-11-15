import pandas as pd
import kagglehub
import os

import ids

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
    return pd.read_csv(os.path.join(path, 'worldcitiespop.csv'), dtype={'Region': str})

raw_data = import_data(path)
# data cleaning
# drop obs with NA value in 'Population' or 'City'
cities_data: pd.DataFrame = raw_data.dropna(subset=["Population", "City"])
# since multiples cities have the same name create a new variable 'City_Country'
cities_data.insert(2,
                   "City_Country",
                   cities_data["AccentCity"] + " " + cities_data["Country"].str.upper())

cities_data = cities_data.loc[cities_data.groupby(ids.PLACE)["Population"].idxmax()].reset_index(drop=True)
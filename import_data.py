import pandas as pd
import kagglehub
import os

import ids

# defining path for data import
path1 = kagglehub.dataset_download("max-mind/world-cities-database")
path2 = kagglehub.dataset_download("juanumusic/countries-iso-codes")

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

raw_data = import_data(path1)
# data cleaning
# drop obs with NA value in 'Population' or 'City'
cities_data: pd.DataFrame = raw_data.dropna(subset=["Population", "City"])
# since multiples cities have the same name create a new variable 'City_Country'
cities_data.insert(2,
                   "City_Country",
                   cities_data["AccentCity"] + " " + cities_data["Country"].str.upper())

cities_data = cities_data.loc[cities_data.groupby(ids.PLACE)["Population"].idxmax()].reset_index(drop=True)

# importing a dataset with full country names with associated Alpha-2 code
cntry_names = pd.read_csv(os.path.join(path2, 'wikipedia-iso-country-codes.csv'))
# changing the column name with a shorter one
cntry_names = cntry_names.rename(columns={"English short name lower case": 'Country name'})
# creating a temporary column for merging
cities_data['Country_upper'] = cities_data['Country'].str.upper()
# merging the datasets
cities_data = cities_data.merge(cntry_names, left_on='Country_upper', right_on='Alpha-2 code', how='left')
# deleting unnecessary columns
cities_data = cities_data.drop(columns=['Country_upper', 'Alpha-2 code', 'Alpha-3 code', 'Numeric code', 'ISO 3166-2'])
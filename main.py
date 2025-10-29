"""
main.py
--------

Main script for the "Around the World" project.

Modules:
    import_data: Handles dataset import.
    utils: Provides utility functions
"""

from import_data import *

# importing raw data from kuggle
raw_data: pd.DataFrame = import_data(path)

# data cleaning
# drop obs with NA value in 'Population' or 'City'
data: pd.DataFrame = raw_data.dropna(subset=["Population","City"])
# if two cities have the same name it drop the one with the lowest population
data = data.loc[data.groupby("City")["Population"].idxmax()].reset_index(drop=True)
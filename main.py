"""
main.py
--------

Main script for the "Around the World" project.

Modules:
    import_data: Handles dataset import.
    utils: Provides utility functions
"""

from import_data import *
from utils import *

# importing raw data from kaggle
raw_data: pd.DataFrame = import_data(path)

# data cleaning
# drop obs with NA value in 'Population' or 'City'
data: pd.DataFrame = raw_data.dropna(subset=["Population","City"])
# if two cities have the same name it drop the one with the lowest population
data = data.loc[data.groupby("City")["Population"].idxmax()].reset_index(drop=True)

# initialization
start_point: pd.DataFrame = data[data["City"] == "london"]

# calculate neighboring cities to London
neighbors: pd.DataFrame = calculate_neighbors(start_point, data, delta=1)

# Extract three nearest city
near3 = get_top3(neighbors)

# calculate travel time
near3["Time"] = (near3.apply(lambda row:
                             calculate_time(row, start_point["Country"].iloc[0]), axis = 1)) #FIXME cambiare start_point con current quando si fa il ciclo
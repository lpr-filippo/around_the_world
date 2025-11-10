"""
main.py
--------

Main script for the "Around the World" project.

Modules:
    import_data: Handles dataset import.
    utils: Provides utility functions.
"""

from import_data import *
from utils import calculate_neighbors, calc_neighbors_home, calculate_time, get_top3, create_move, fastest_long, go_home

# importing raw data from kaggle
raw_data: pd.DataFrame = import_data(path)

# data cleaning
# drop obs with NA value in 'Population' or 'City'
data: pd.DataFrame = raw_data.dropna(subset=["Population","City"])
# if two cities have the same name it drop the one with the lowest population
data = data.loc[data.groupby("City")["Population"].idxmax()].reset_index(drop=True)

# initialization
start_point: pd.DataFrame = data[data["City"] == "london"]
index = 0
current_point = start_point.copy()

# creating a dataframe with visited cities
trip = start_point.copy()
# Initialize the trip DataFrame with additional numeric columns
# to ensure consistent structure when concatenating next cities
trip[["Dist_long", "Distance_km", "Time", "Speed"]] = 0.0

old_point = pd.DataFrame()

while True:

    print(f"Current city: {current_point['City'].iloc[0]}")

    if start_point["Longitude"].iloc[0] - 10.0 <= current_point["Longitude"].iloc[0] < start_point["Longitude"].iloc[0]:
        # Use calc_neighbors_home when is near home
        neighbors: pd.DataFrame = calc_neighbors_home(current_point, data, start_point, old_point, delta=1, verbose=True)
        # Exclude already visited cities except home
        neighbors = neighbors[~neighbors["City"].isin(trip["City"].iloc[1:])]
        # Extract three nearest city
        near3 = get_top3(neighbors)
        # calculate travel time
        near3["Time"] = near3.apply(lambda row: calculate_time(row, current_point["Country"].iloc[0]), axis=1)
        # Select next city prioritizing movement toward home
        next_point = create_move(near3, lambda df: go_home(df, "london"))
    else:
        # Normal eastward travel
        neighbors: pd.DataFrame = calculate_neighbors(current_point, data, delta=1, verbose=True)
        # Exclude already visited cities except home
        neighbors = neighbors[~neighbors["City"].isin(trip["City"].iloc[1:])]
        # Extract three nearest city
        near3 = get_top3(neighbors)
        # calculate travel time
        near3["Time"] = near3.apply(lambda row: calculate_time(row, current_point["Country"].iloc[0]), axis=1)
        # Select next city with fastest_long logic
        next_point = create_move(near3, fastest_long)

    # convert pd.Series to single-row pd.DataFrame for concatenation with 'trip'
    next_point = next_point.to_frame().T
    # add 'next_point' to trip
    trip = pd.concat([trip, next_point], ignore_index=True)

    old_point = current_point.copy()
    current_point = next_point.copy()
    index += 1

    # Stop conditions
    if current_point["City"].iloc[0].lower() == "london" and index > 0:
        print("Returned to London!")
        break

    if index > 10000:
        print("Too many iterations, stopping.")
        break
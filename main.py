"""
main.py
--------

Main script for the "Around the World" project.

Modules:
    import_data: Handles dataset import.
    utils: Provides utility functions.
    ids: Defines variables for easy modification.
    app_render: Code for the web app using Dash.
    map_creator: Functions to generate maps and render them in app_render.
    stats: Functions to calculate statistics about the data and render them in app_render.
"""
import pandas as pd
from dash import Output, Input, callback

from utils import calculate_neighbors, calc_neighbors_home, calculate_time, get_top3, create_move, fastest_long, go_home
import ids
# importing the clean dataset with the cities
from import_data import cities_data

@callback(
    Output('trip', 'data'),
    Input('dropdown', 'value')
)
def move_atw(str_city: str) -> list[dict]:

    # initialization
    start_point: pd.DataFrame = cities_data[cities_data[ids.PLACE] == str_city]
    index = 0
    current_point = start_point.copy()

    # creating a dataframe with visited cities
    trip = start_point.copy()
    # Initialize the trip DataFrame with additional numeric columns
    # to ensure consistent structure when concatenating next cities
    trip[["Dist_long", "Distance_km", "Time", "Speed"]] = 0.0

    while True:

        if (start_point["Longitude"].iloc[0] - ids.DELTA_HOME <= current_point["Longitude"].iloc[0] <= start_point["Longitude"].iloc[0])\
                and index != 0:
            # Use calc_neighbors_home when is near home
            neighbors: pd.DataFrame = calc_neighbors_home(current_point, cities_data, start_point, trip, delta=1, verbose=False)
            # Extract three nearest city
            near3 = get_top3(neighbors)
            if near3.shape[0] == 0:
                return trip
            # calculate travel time
            near3["Time"] = near3.apply(lambda row: calculate_time(row, current_point["Country"].iloc[0]), axis=1)
            # Select next city prioritizing movement toward home
            next_point = create_move(near3, lambda df: go_home(df, str_city))
        else:
            # Normal eastward travel
            neighbors: pd.DataFrame = calculate_neighbors(current_point, cities_data, trip, delta=1, verbose=False)
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

        current_point = next_point.copy()
        index += 1

        # Stop conditions
        if current_point[ids.PLACE].iloc[0] == str_city and index > 0:
            print(f"Returned to {str_city}!")
            break

        if index > 10000:
            print("Too many iterations, stopping.")
            break

    return trip.to_dict('records')

def main():
    move_atw("London GB")

if __name__ == "__main__":
    main()

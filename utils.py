from math import radians, asin, sin, cos, sqrt
from collections.abc import Callable
import pandas as pd

class Distance:
    R = 6371.0  # Earth's arithmetic mean radius

    def __init__(self, current):
        self.latitude = current["Latitude"]
        self.longitude = current["Longitude"]

        # Ensure latitude and longitude are always floats.
        # If passed a single-row Series (from a DataFrame), take the first element.
        self.latitude = float(current["Latitude"].iloc[0]) if isinstance(current["Latitude"], pd.Series) else (
            float(current["Latitude"]))
        self.longitude = float(current["Longitude"].iloc[0]) if isinstance(current["Longitude"], pd.Series) else (
            float(current["Longitude"]))

    @staticmethod
    def delta_radians(start: float, end: float) -> float:
        """Convert the angular difference between two coordinates from degrees to radians.

        Args:
            start (float): The starting coordinate in degrees.
            end (float): The ending coordinate in degrees.

        Returns:
            float: The angular difference in radians.
        """
        return radians(end - start)

    def lat_distance(self, other) -> float:
        """Compute the latitude difference in radians between two points.

        Args:
            other (Distance): Another `Distance` instance to compare with.

        Returns:
            float: The latitude difference in radians.
        """
        return self.delta_radians(self.latitude, other.latitude)

    def long_distance(self, other) -> float:
        """Compute the longitude difference in radians between two points.

        Args:
            other (Distance): Another `Distance` instance to compare with.

        Returns:
            float: The longitude difference in radians.
        """
        return self.delta_radians(self.longitude, other.longitude)

    def distance_to(self, other) -> float:
        """Compute the distance between two geographic points using the Haversine formula.

        Args:
            other (Distance): Another `Distance` instance representing the destination point.

        Returns:
            float: The distance between the two points in kilometers.
        """
        dist_lat = self.lat_distance(other)
        dist_lon = self.long_distance(other)

        # convert both latitudes to radians (for the cosine term)
        lat1 = radians(self.latitude)
        lat2 = radians(other.latitude)

        a = (sin(dist_lat / 2) ** 2
             + cos(lat1) * cos(lat2) * sin(dist_lon / 2) ** 2)

        c = 2 * asin(sqrt(a))
        return self.R * c


def calculate_neighbors(current, data: pd.DataFrame, delta: float = 1, delta_max: float = 90, verbose: bool = False) -> pd.DataFrame:
    """Identify neighboring cities located eastward within a specified angular range.

        This function selects all cities from the `data` DataFrame whose longitude lies
        within `delta` degrees east of the reference city's longitude and whose latitude
        lies within ±`delta` degrees of the reference city's latitude.

        Args:
            current (pd.DataFrame): A single-row DataFrame containing the reference city's
                coordinates, with columns "Latitude" and "Longitude".
            data (pd.DataFrame): The full dataset of cities, containing the same columns.
            delta (float, optional): Initial angular threshold (degrees) for both longitude and latitude. Defaults to 1.
            delta_max (float, optional): Maximum threshold (degrees). Defaults to 90.
            verbose (bool, optional): If True, print each expansion step.

        Returns:
            pd.DataFrame: A subset of `data` containing the neighboring cities that satisfy
            the specified angular constraints.
        """
    dist = Distance(current)
    start_long = dist.longitude
    start_lat = dist.latitude
    delta_long = (data["Longitude"] - start_long + 180) % 360 - 180

    while delta <= delta_max:

        # Compute eastward longitudinal difference (0°–360° range)
        # It correctly handles the 180° meridian crossing, but requires delta < 180° to avoid including westward points
        mask = (
                (delta_long <= delta) &
                (delta_long > 0) &
                (data["Latitude"] >= (start_lat - delta)) &
                (data["Latitude"] <= (start_lat + delta))
        )

        neighbors = data.loc[mask].copy()

        if not neighbors.empty:
            neighbors["Dist_long"] = abs(delta_long[mask])

            neighbors["Distance_km"] = neighbors.apply(
                lambda row: dist.distance_to(Distance({"Latitude": row["Latitude"], "Longitude": row["Longitude"]})),
                axis=1)

            # exclude rows where distance is zero
            neighbors = neighbors[neighbors["Distance_km"] != 0].copy()

            # stop expanding if we have 3 or more neighbors
            if len(neighbors) >= 3 or delta == delta_max:
                return neighbors

        # expand the search area
        delta *= 2
        if verbose:
            print(f"No nearby cities found within ±{delta / 2}°, expanding to ±{delta}°")

    # if no cities found even at max_delta
    print("No neighboring cities found within the maximum search range.")
    return pd.DataFrame()


def calc_neighbors_home(current: pd.DataFrame, data: pd.DataFrame, home: pd.DataFrame, delta: float = 1,
    delta_max: float = 90, verbose: bool = False) -> pd.DataFrame:
    """
    Identify neighboring cities when approaching the home city.

    This function finds nearby cities west of the home longitude (within [home_long - 10, home_long]),
    expanding the latitude search range progressively until at least 3 neighbors are found or delta
    exceeds delta_max.

    Args:
        current (pd.DataFrame): A single-row DataFrame containing the reference city's
                coordinates, with columns "Latitude" and "Longitude".
        data (pd.DataFrame): The full dataset of cities, containing the same columns.
        home (pd.DataFrame): Single-row DataFrame representing the home city.
        delta (float, optional): Initial angular threshold (degrees) for latitude. Defaults to 1.
        delta_max (float, optional): Maximum threshold (degrees). Defaults to 90.
        verbose (bool, optional): If True, print each expansion step.

    Returns:
            pd.DataFrame: A subset of `data` containing the neighboring cities that satisfy
            the specified angular constraints.
    """
    dist = Distance(current)
    home_dist = Distance(home)

    start_long = dist.longitude
    start_lat = dist.latitude
    home_long = home_dist.longitude
    delta_long = (data["Longitude"] - start_long + 180) % 360 - 180

    while delta <= delta_max:

        mask = (
                (data["Longitude"] >= home_long - 10) &
                (data["Longitude"] <= home_long) &
                (data["Latitude"] >= (start_lat - delta)) &
                (data["Latitude"] <= (start_lat + delta))
        )

        neighbors = data.loc[mask].copy()

        if not neighbors.empty:
            neighbors["Dist_long"] = abs(delta_long[mask])

            neighbors["Distance_km"] = neighbors.apply(
                lambda row: dist.distance_to(
                    Distance({"Latitude": row["Latitude"], "Longitude": row["Longitude"]})
                ), axis=1
            )

            neighbors["Dist_from_home"] = neighbors.apply(
                lambda row: home_dist.distance_to(
                    Distance({"Latitude": row["Latitude"], "Longitude": row["Longitude"]})
                ), axis=1
            )

            neighbors = neighbors[neighbors["Distance_km"] != 0].copy()

            if len(neighbors) >= 3 or delta == delta_max:
                return neighbors

        delta *= 2
        if verbose:
            print(f"No nearby cities found within ±{delta / 2}°, expanding to ±{delta}°")

    print("No cities found even at maximum search range.")
    return pd.DataFrame()


def get_top3(df: pd.DataFrame, n: int = 3, sort_by: str = "Distance_km") -> pd.DataFrame:
    """Return up to `n` nearest cities sorted by `sort_by` (default: 'Distance_km').

    If fewer than `n` cities are available, return all of them.
    Prints a message if the DataFrame is empty.

    Args:
        df (pd.DataFrame): DataFrame of cities with a distance column.
        n (int, optional): Max number of cities to return. Defaults to 3.
        sort_by (str, optional): Column used for sorting. Defaults to 'Distance_km'.

    Returns:
        pd.DataFrame: Subset of up to `n` nearest cities.
    """
    if df.empty:
        print("No cities found.")
        return df

    # takes the minimum between integer 'n' and length of 'df'
    # it manages the case when we have less than 3 cities near our current one
    nearest = df.nsmallest(min(len(df),n), sort_by)
    return nearest.reset_index(drop=True)


def calculate_time(row: pd.Series, country: str) -> int:
    """Compute travel time for a city based on its distance from current point and other properties.

    Args:
        row (pd.Series): A row from the DataFrame.
        country (str): The reference country.

    Returns:
        int: The computed travel time.
    """
    index = int(str(row.name))
    t = 2 ** (index + 1)
    if row["Country"] != country:
        t += 2
    if row["Population"] > 200000:
        t += 2
    return t


def create_move(df: pd.DataFrame, method: Callable[[pd.DataFrame], pd.Series]) -> pd.Series:
    """
    Apply a given selection strategy to choose the next city.

    Args:
        df (pd.DataFrame): DataFrame containing nearby cities and travel metrics (e.g. distances, times).
        method (Callable[[pd.DataFrame], pd.Series]):
            Function defining how to select the next city, such as `fastest_long` or a custom rule.

    Returns:
        pd.Series: The selected city's row, representing the next destination.
    """
    return method(df)

def fastest_long(df: pd.DataFrame) -> pd.Series:
    """
    Select the city with the highest longitudinal speed (Dist_long / Time).

    Args:
        df (pd.DataFrame): Inherited from `create_move`

    Returns:
        pd.Series: The row corresponding to the city that maximizes Dist_long / Time.
    """
    df = df.copy() # to avoid warnings
    df["Speed"] = df["Dist_long"] / df["Time"]
    return df.loc[df["Speed"].idxmax()]

def closest_to_home(df: pd.DataFrame) -> pd.Series:
    """
    Return the city closest to the home city based on 'Dist_from_home'.

    Args:
        df (pd.DataFrame): Inherited from `create_move`

    Returns:
        pd.Series: The row corresponding to the city with the minimum distance to the home city.
    """
    df = df.copy()  # to avoid warnings
    return df.loc[df["Dist_from_home"].idxmin()]

def go_home(df: pd.DataFrame, start_city: str) -> pd.Series:
    """
        Select the next city when returning toward the starting point.

        If the starting city (e.g., London) is among the nearby cities, it is immediately chosen.
        Otherwise, the function selects the city closest to the home city based on `Dist_from_home`,
        ensuring movement stays directed toward the destination.

        Args:
            df (pd.DataFrame): Inherited from `create_move`
            start_city (str): Name of the starting city (used to detect when it's reachable).

        Returns:
            pd.Series: The selected city's row, representing the next move toward home.
    """
    df = df.copy() # to avoid warnings
    if start_city in df["City"].values:
        df["Speed"] = df["Dist_long"] / df["Time"]
        return df[df["City"] == start_city].iloc[0, :] # to get a pd.Series and not a pd.DataFame
    return closest_to_home(df)
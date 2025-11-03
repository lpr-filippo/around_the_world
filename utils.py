from math import radians, asin, sin, cos, sqrt
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


def calculate_neighbors(current, data, delta: float) -> pd.DataFrame:
    """Identify neighboring cities located eastward within a specified angular range.

        This function selects all cities from the `data` DataFrame whose longitude lies
        within `delta` degrees east of the reference city's longitude and whose latitude
        lies within ±`delta` degrees of the reference city's latitude.

        Args:
            current (pd.DataFrame): A single-row DataFrame containing the reference city's
                coordinates, with columns "Latitude" and "Longitude".
            data (pd.DataFrame): The full dataset of cities, containing the same columns.
            delta (float): The angular threshold (in degrees) for both longitude and latitude.

        Returns:
            pd.DataFrame: A subset of `data` containing the neighboring cities that satisfy
            the specified angular constraints.
        """
    dist = Distance(current)
    start_long = dist.longitude
    start_lat = dist.latitude

    delta_long = (data["Longitude"] - start_long + 180) % 360 - 180

    mask = (
            (abs(delta_long) <= delta) &
            (data["Latitude"] >= (start_lat - delta)) &
            (data["Latitude"] <= (start_lat + delta))
    )

    neighbors = data.loc[mask].copy()

    neighbors["Distance_km"] = neighbors.apply(
        lambda row: dist.distance_to(Distance({"Latitude": row["Latitude"], "Longitude": row["Longitude"]})),
        axis=1)

    # exclude rows where distance is zero
    return neighbors[neighbors["Distance_km"] != 0].copy()

def get_top3(df: pd.DataFrame, n: int = 3, sort_by: str = "Distance_km") -> pd.DataFrame:
    """Return up to `n` nearest cities sorted by `sort_by` (default: 'Distance_km').

    If fewer than `n` cities are available, return all of them.
    Prints a message if the DataFrame is empty.

    Args:
        df (pd.DataFrame): DataFrame of cities with a distance column.
        n (int, optional): Max number of cities to return. Defaults to 3.
        sort_by (str, optional): Column used for sorting. Defaults to 'Distance_km'.

    Returns:
        pd.DataFrame: Subset of up to `n` closest cities.
    """
    if df.empty:
        print("No cities found.")
        return df

    # takes the minimum between integer 'n' and length of 'df'
    # it manages the case when we have less than 3 cities near our current one
    return df.nsmallest(min(len(df),n), sort_by)
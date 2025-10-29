from math import radians, asin, sin, cos, sqrt

class Distance:
    R = 6371.0  # Earth's arithmetic mean radius

    def __init__(self, current):
        self.latitude = current["Latitude"]
        self.longitude = current["Longitude"]

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



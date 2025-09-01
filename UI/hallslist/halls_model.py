"""
Model: Responsible for data access (DB calls for halls)
"""
from server.database.read_api import get_halls, get_halls_filtered


class HallsModel:
    def fetch_all_halls(self):
        """
        Returns list of halls from DB.
        Each hall is a dict with keys:
        HallName, HallType, Capacity, Region, Latitude, Longitude,
        Description, PricePerHour, PricePerDay, PricePerPerson,
        ParkingAvailable, WheelchairAccessible,
        ContactPhone, ContactEmail, WebsiteUrl, PhotoUrl
        """
        return get_halls()

    def fetch_filtered_halls(self, region=None, hall_type=None, search=None):
        """
        Fetch halls from the database with optional filtering.

        Args:
            region (str, optional): Region filter. If None or "All regions", no filter is applied.
            hall_type (str, optional): Hall type filter. If None or "All types", no filter is applied.
            search (str, optional): Free-text search term. Matches hall name or description.

        Returns:
            list[dict]: A list of halls matching the filter criteria.
        """
        return get_halls_filtered(region, hall_type, search)

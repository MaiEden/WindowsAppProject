"""
Model: Responsible for data access (DB calls for halls)
"""
from server.database.read_api import get_halls


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

    def get_all_halls(self):
        return get_halls()


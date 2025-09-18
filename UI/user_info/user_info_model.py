# user_info_model.py — minimal docs
# Thin API wrapper around ServerAPI endpoints related to users and their usage.

from typing import List, Dict, Optional
from urllib.parse import quote
from UI import server_access

class UserInfoModel:
    """Lightweight service to fetch a user and their related usage (decor/services/halls/owned)."""

    def __init__(self):
        """Initialize the model (no internal state for now)."""
        pass

    def get_user(self, username: str) -> Optional[Dict]:
        """
        Fetch a user by username.
        """
        return server_access.request(f"/DB/users/get_user_by_name/{quote(username)}")

    def get_decor_used(self, user_id: int) -> List[Dict]:
        """
        Fetch decors used by the given user.
        """
        return server_access.request(f"/DB/users/{user_id}/decor/used")

    def get_services_used(self, user_id: int) -> List[Dict]:
        """
        Fetch services used by the given user.
        """
        return server_access.request(f"/DB/users/{user_id}/services/used")

    def get_halls_used(self, user_id: int) -> List[Dict]:
        """
        Fetch halls used by the given user.
        """
        return server_access.request(f"/DB/users/{user_id}/halls/used")

    def get_owned_items(self, user_id: int) -> List[Dict]:
        """
        Fetch items owned by the given user.
        """
        return server_access.request(f"/DB/users/{user_id}/owned")

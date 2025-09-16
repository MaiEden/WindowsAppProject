# user_info_model.py (גרסת API)
from typing import List, Dict, Optional
from urllib.parse import quote
from UI import server_access

class UserInfoModel:
    def __init__(self):
        pass

    def get_user(self, username: str) -> Optional[Dict]:
        # קיים כבר endpoint כזה בשרת
        return server_access.request(f"/DB/users/get_user_by_name/{quote(username)}")

    def get_decor_used(self, user_id: int) -> List[Dict]:
        return server_access.request(f"/DB/users/{user_id}/decor/used")

    def get_services_used(self, user_id: int) -> List[Dict]:
        return server_access.request(f"/DB/users/{user_id}/services/used")

    def get_halls_used(self, user_id: int) -> List[Dict]:
        return server_access.request(f"/DB/users/{user_id}/halls/used")

    def get_owned_items(self, user_id: int) -> List[Dict]:
        return server_access.request(f"/DB/users/{user_id}/owned")

"""
AddDecorModel
Responsibilities:
- Look up (or create) the default OWNER user.
- Create a decor option via the server API.
- Link the caller user <-> decor using RelationType.
"""
from typing import Optional, Dict, Any
import requests
from UI import server_access

class AddDecorModel:
    def __init__(self, default_owner_username: str = "Noa Hadad"):
        self.default_owner_username = default_owner_username

    # -------- Users --------
    def get_user_by_name(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Uses /DB/users/get_user_by_name/{username} to get the user
        """
        path = f"/DB/users/get_user_by_name/{requests.utils.quote(username)}"
        return server_access.request(path)

    def ensure_user(self, phone: str, username: str, password_hash: str, region: str) -> int:
        """
        Best-effort creation:
        - If user exists -> return its UserId
        - Else -> create user using your demo insert endpoint (GET based)
        """
        u = self.get_user_by_name(username)
        if u and isinstance(u, dict) and u.get("UserId"):
            return int(u["UserId"])

        path = (
            f"/DB/users/insert_user/"
            f"{requests.utils.quote(phone)}/"
            f"{requests.utils.quote(username)}/"
            f"{requests.utils.quote(password_hash)}/"
            f"{requests.utils.quote(region)}"
        )
        return int(server_access.request(path))

    # -------- Decor --------
    def create_decor(self, payload: Dict[str, Any]) -> int:
        """
        POST /DB/decors/create -> returns DecorId (either plain int or { "DecorId": int })
        """
        res = server_access.post("/DB/decors/create", json=payload)
        if isinstance(res, int):
            return int(res)
        if isinstance(res, dict) and "DecorId" in res:
            return int(res["DecorId"])
        # Some servers return raw text for ints; try to coerce
        try:
            return int(str(res).strip())
        except Exception:
            raise TypeError("Unexpected response from /DB/decors/create")

    def link_owner(self, user_id: int, decor_id: int, relation: str = "OWNER") -> None:
        """
        POST /DB/user_decor/link -> inserts relation row.
        """
        server_access.post("/DB/user_decor/link", json={
            "UserId": int(user_id),
            "DecorId": int(decor_id),
            "RelationType": relation
        })
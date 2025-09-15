from typing import Optional, Dict, Any
from UI import server_access

class HallDetailsModel:
    def fetch(self, hall_id: int, resolve_address: bool = True) -> Optional[Dict[str, Any]]:
        # השרת כבר מחזיר את הכתובת אם resolveAddress=True
        flag = "true" if resolve_address else "false"
        return server_access.request(f"/DB/halls/get/{hall_id}?resolveAddress={flag}")

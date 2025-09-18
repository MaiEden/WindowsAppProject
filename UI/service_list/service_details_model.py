from typing import Optional, Dict, Any
from UI import server_access

class ServiceDetailsModel:
    def fetch(self, service_id: int) -> Optional[Dict[str, Any]]:
        return server_access.request(f"/DB/services/get/{service_id}")
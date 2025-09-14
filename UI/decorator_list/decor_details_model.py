from typing import Optional, Dict, Any
from UI import server_access

class DecorDetailsModel:
    def fetch(self, decor_id: int) -> Optional[Dict[str, Any]]:
        # מחזיר שורה מלאה מטבלת dbo.DecorOption
        return server_access.request(f"/DB/decors/get/{decor_id}")

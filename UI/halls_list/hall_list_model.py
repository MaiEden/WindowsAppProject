"""
Model: Fetches halls catalog from the server (no local fallbacks).
Expected response: list[dict] with keys aligned to dbo.Hall columns.
"""
from typing import List, Dict, Any, Optional
from UI import server_access
from server.database.image_loader import IMAGE_LOADER
from PySide6.QtCore import Qt

class HallListModel:
    def __init__(self) -> None:
        self._items: List[Dict[str, Any]] = []

    # --- data fetch ---
    def load(self) -> None:
        """Fetch data from server (raise on failure so the presenter can show a message if needed)."""
        data = server_access.request("/DB/halls/list")
        if not isinstance(data, list):
            raise TypeError("Halls list endpoint must return a list of objects.")
        self._items = data

    # --- queries on fetched data ---
    def all(self) -> List[Dict[str, Any]]:
        return list(self._items)

    def query(
        self,
        text: str = "",
        hall_type: Optional[str] = None,
        accessible_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """Client-side search & filter on already-fetched items."""
        t = (text or "").strip().lower()
        ht = (hall_type or "").strip()

        def match(item: Dict[str, Any]) -> bool:
            if accessible_only and not bool(item.get("WheelchairAccessible")):
                return False
            if ht and ht != "All" and item.get("HallType") != ht:
                return False
            if not t:
                return True
            hay = " ".join(
                [
                    str(item.get("HallName", "")),
                    str(item.get("Description", "")),
                    str(item.get("HallType", "")),
                    str(item.get("Region", "")),
                ]
            ).lower()
            return t in hay

        return [x for x in self._items if match(x)]
"""
Model: Fetches Services (dbo.ServiceOption) from the server (no local fallbacks).
"""
from typing import List, Dict, Any, Optional
from UI import server_access
from server.database.image_loader import IMAGE_LOADER
from PySide6.QtCore import Qt


class ServiceListModel:
    def __init__(self) -> None:
        self._items: List[Dict[str, Any]] = []

    def load(self) -> None:
        """Fetch data from server (raise on failure so the presenter can show a message if needed)."""
        data = server_access.request("/DB/services/list")
        if not isinstance(data, list):
            raise TypeError("Services list endpoint must return a list of objects.")
        self._items = data

    def all(self) -> List[Dict[str, Any]]:
        return list(self._items)

    def query(self, text: str = "", category: Optional[str] = None, available_only: bool = False) -> List[Dict[str, Any]]:
        """Client-side search & filter on already-fetched items."""
        t = (text or "").strip().lower()
        cat = (category or "").strip()

        def match(item: Dict[str, Any]) -> bool:
            if available_only and not bool(item.get("Available")):
                return False
            if cat and cat != "All" and item.get("Category") != cat:
                return False
            if not t:
                return True
            hay = " ".join([
                str(item.get("ServiceName", "")),
                str(item.get("Description", "")),
                str(item.get("ShortDescription", "")),
                str(item.get("Subcategory", "")),
            ]).lower()
            return t in hay

        return [x for x in self._items if match(x)]
"""
Model: Fetches decor catalog from the server (no local fallbacks).
Expected response: list[dict] with keys aligned to dbo.DecorOption columns.
"""
from typing import List, Dict, Any, Optional
from UI import server_access  # זהה ללוגין
from server.database.image_loader import IMAGE_LOADER
from PySide6.QtCore import Qt   #


class DecorListModel:
    def __init__(self) -> None:
        self._items: List[Dict[str, Any]] = []

    def load(self) -> None:
        """Fetch data from server (raise on failure so the presenter can show a message if needed)."""
        data = server_access.request("/DB/decors/list")
        if not isinstance(data, list):
            raise TypeError("Decor list endpoint must return a list of objects.")
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
                str(item.get("DecorName", "")),
                str(item.get("Description", "")),
                str(item.get("Theme", "")),
            ]).lower()
            return t in hay

        return [x for x in self._items if match(x)]

    def get_pic(self, imageName: str):
        self._image_url = f"/decor/{imageName}.jpg"
        IMAGE_LOADER.pixmapReady.connect(self._on_pixmap_ready, type=Qt.UniqueConnection)
        IMAGE_LOADER.fetch(self._image_url)
"""
Presenter: ties View <-> Model (MVP)
- Wires search, category, availability, refresh
"""
from typing import Dict, Any
from PySide6.QtCore import QObject
from service_list_model import ServiceListModel

class ServiceListPresenter(QObject):
    def __init__(self, model: ServiceListModel, view) -> None:
        super().__init__()
        self.model = model
        self.view = view
        self._connect()

    def _connect(self) -> None:
        self.view.searchChanged.connect(self.on_filters_changed)
        self.view.categoryChanged.connect(self.on_filters_changed)
        self.view.availableChanged.connect(self.on_filters_changed)
        self.view.refreshRequested.connect(self.on_refresh)

    # --- lifecycle ---
    def start(self) -> None:
        self.view.set_busy(True)
        try:
            self.model.load()
        except Exception as e:
            self.view.show_error(str(e))
            self.view.set_busy(False)
            return

        # categories (distinct from data)
        cats = sorted({r.get("Category") for r in self.model.all() if r.get("Category")})
        self.view.populate_categories(["All"] + cats)
        self._apply_filters()
        self.view.set_busy(False)

    # --- actions ---
    def on_refresh(self) -> None:
        self.start()

    def on_filters_changed(self, *_args) -> None:
        self._apply_filters()

    # --- helpers ---
    def _apply_filters(self) -> None:
        q = self.view.get_search_text()
        cat = self.view.get_selected_category()
        only = self.view.get_available_only()
        rows = self.model.query(q, cat, only)
        cards = [self._to_card(r) for r in rows]
        self.view.show_cards(cards)

    def _to_card(self, r: Dict[str, Any]) -> Dict[str, Any]:
        subtitle = f'{r.get("Category","")}'
        if r.get("Subcategory"):
            subtitle += f' · {r.get("Subcategory")}'

        return {
            "id": r.get("ServiceId"),
            "title": r.get("ServiceName") or "",
            "subtitle": subtitle,
            "region": r.get("Region") or "",
            "available": bool(r.get("Available")),
            "photo": r.get("PhotoUrl") or "",
        }
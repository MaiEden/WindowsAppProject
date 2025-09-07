"""
Presenter: ties View <-> Model (MVP)
- Wires search, category, availability, refresh
- Maps data rows to card view models (subset only)
"""
from typing import List, Dict, Any
from PySide6.QtCore import QObject
from decor_list_model import DecorListModel

class DecorListPresenter(QObject):
    def __init__(self, model: DecorListModel, view) -> None:
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
        prices = [p for p in (r.get("PriceSmall"), r.get("PriceMedium"), r.get("PriceLarge")) if p not in (None, "")]
        price_txt = f"From ₪{min(prices):.0f}" if prices else ""
        subtitle = f'{r.get("Category","")}'
        if r.get("Theme"):
            subtitle += f' · {r.get("Theme")}'
        return {
            "id": r.get("DecorId"),
            "title": r.get("DecorName") or "",
            "subtitle": subtitle,
            "price": price_txt,
            "region": r.get("Region") or "",
            "available": bool(r.get("Available")),
            "photo": r.get("PhotoUrl") or "",
        }

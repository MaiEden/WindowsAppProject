"""
Presenter: ties View <-> Model (MVP)
- Wires search, hall_type, accessibility, refresh
- Maps data rows to card view models (subset only)
"""
from typing import List, Dict, Any
from PySide6.QtCore import QObject
from hall_list_model import HallListModel

class HallListPresenter(QObject):
    def __init__(self, model: HallListModel, view) -> None:
        super().__init__()
        self.model = model
        self.view = view
        self._connect()

    def _connect(self) -> None:
        self.view.searchChanged.connect(self.on_filters_changed)
        self.view.typeChanged.connect(self.on_filters_changed)
        self.view.accessibleChanged.connect(self.on_filters_changed)
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

        # hall types (distinct from data)
        types = sorted({r.get("HallType") for r in self.model.all() if r.get("HallType")})
        self.view.populate_types(["All"] + types)
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
        ht = self.view.get_selected_type()
        acc = self.view.get_accessible_only()
        rows = self.model.query(q, ht, acc)
        cards = [self._to_card(r) for r in rows]
        self.view.show_cards(cards)

    def _fmt_price(self, r: Dict[str, Any]) -> str:
        # Choose the lowest non-empty price among person/hour/day for a simple "From ₪X"
        candidates = []
        for k in ("PricePerPerson", "PricePerHour", "PricePerDay"):
            v = r.get(k)
            if v not in (None, ""):
                try:
                    candidates.append(float(v))
                except Exception:
                    pass
        return f"From ₪{min(candidates):.0f}" if candidates else ""

    def _to_card(self, r: Dict[str, Any]) -> Dict[str, Any]:
        subtitle = f'{r.get("HallType","")}'
        cap = r.get("Capacity")
        if cap not in (None, ""):
            subtitle += f' · {int(cap)} ppl'
        return {
            "id": r.get("HallId"),
            "title": r.get("HallName") or "",
            "subtitle": subtitle,
            "price": self._fmt_price(r),
            "region": r.get("Region") or "",
            # Reuse the pill to indicate accessibility
            "accessible": bool(r.get("WheelchairAccessible")),
            "photo": r.get("PhotoUrl") or "",
        }

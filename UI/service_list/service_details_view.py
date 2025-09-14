# ============================
# File: service_list/service_details_view.py
# ============================
from pathlib import Path
from typing import Dict, Any
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
    QGridLayout, QMessageBox
)
from server.database.image_loader import load_into

BASE_DIR = Path(__file__).resolve().parent

def _title(t):  lbl=QLabel(t); lbl.setStyleSheet("font-size:22px;font-weight:700;"); return lbl
def _sub(t):    lbl=QLabel(t); lbl.setStyleSheet("color:#666;"); return lbl
def _pill(t):   lbl=QLabel(t); lbl.setStyleSheet("padding:4px 8px;border-radius:12px;background:rgba(0,0,0,.06);"); return lbl
def _kv(k,v):
    w=QFrame(); r=QHBoxLayout(w)
    k_lbl=QLabel(k); k_lbl.setStyleSheet("color:#666;")
    v_lbl=QLabel(v if (v not in (None, "")) else "—"); v_lbl.setWordWrap(True)
    r.addWidget(k_lbl,1); r.addWidget(v_lbl,3)
    return w

class ServiceDetailsView(QWidget):
    """
    Nice, modern details page for ServiceOption.
    Shows image, title, subtitle, tags (availability, logistics), pricing, meta.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Service – Details")
        self._build()

    # ---------- UI skeleton ----------
    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(10,10,10,10); root.setSpacing(10)

        # scroll container
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        wrap = QFrame(); scroll.setWidget(wrap)
        root.addWidget(scroll, 1)

        lay = QVBoxLayout(wrap); lay.setSpacing(12)

        # Top card: image + titles + tags
        top = QFrame(objectName="Card"); top_l = QHBoxLayout(top); top_l.setSpacing(14)
        self.photo = QLabel(); self.photo.setFixedSize(420,260); self.photo.setAlignment(Qt.AlignCenter)

        info = QVBoxLayout()
        self.title = _title("Service name")
        self.subtitle = _sub("Category · Subcategory")
        self.tags = QHBoxLayout(); self.tags.setSpacing(6)

        info.addWidget(self.title)
        info.addWidget(self.subtitle)
        info.addLayout(self.tags)
        info.addStretch(1)

        top_l.addWidget(self.photo)
        top_l.addLayout(info, 1)
        lay.addWidget(top)

        # Pricing card
        price = QFrame(objectName="Card"); p = QGridLayout(price); p.setHorizontalSpacing(18)
        self.base_price    = QLabel("—")
        self.price_person  = QLabel("—")
        self.travel_base   = QLabel("—")
        self.travel_per_km = QLabel("—")
        for w in (self.base_price, self.price_person, self.travel_base, self.travel_per_km):
            w.setStyleSheet("font-weight:600;")
        p.addWidget(QLabel("Base price"),       0,0); p.addWidget(self.base_price,    0,1)
        p.addWidget(QLabel("Price per person"), 1,0); p.addWidget(self.price_person,  1,1)
        p.addWidget(QLabel("Travel fee (base)"),2,0); p.addWidget(self.travel_base,   2,1)
        p.addWidget(QLabel("Travel fee per km"),3,0); p.addWidget(self.travel_per_km, 3,1)
        lay.addWidget(price)

        # Meta / Policy / Constraints card
        meta = QFrame(objectName="Card"); self.meta_lay = QVBoxLayout(meta); self.meta_lay.setSpacing(6)
        lay.addWidget(meta)

        # styling to match other cards
        self.setStyleSheet("""
            QFrame#Card{
                background:#fff;
                border:1px solid rgba(0,0,0,.07);
                border-radius:12px;
                padding:12px;
            }
        """)

    # ---------- Presenter API ----------
    def set_busy(self, busy: bool): self.setDisabled(busy)
    def show_error(self, msg: str): QMessageBox.critical(self, "Error", msg)

    # ---------- Populate with data from API (ServiceOption row) ----------
    def populate(self, r: Dict[str, Any]):
        # Image
        url = r.get("PhotoUrl") or "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/download.jpg"
        load_into(self.photo, url, placeholder=BASE_DIR / "placeholder_card.png", size=QSize(420,260))

        # Titles
        name = r.get("ServiceName") or ""
        cat  = r.get("Category") or ""
        sub  = r.get("Subcategory")
        self.title.setText(name)
        self.subtitle.setText(f"{cat}" + (f" · {sub}" if sub else ""))

        # Tags (compact logistics/availability overview)
        self._clear(self.tags)
        region = r.get("Region")
        if region: self.tags.addWidget(_pill(region))

        # Indoor/Outdoor
        is_outdoor = bool(r.get("IsOutdoor"))  # 0=Indoor, 1=Outdoor
        self.tags.addWidget(_pill("Outdoor" if is_outdoor else "Indoor"))

        # Stage / Electricity
        if bool(r.get("StageRequired")):        self.tags.addWidget(_pill("Stage required"))
        if bool(r.get("RequiresElectricity")):  self.tags.addWidget(_pill("Electricity"))

        # Noise
        noise = r.get("NoiseLevel")
        if noise: self.tags.addWidget(_pill(f"Noise: {noise}"))

        # Age & Participants ranges
        age_min = r.get("MinAge"); age_max = r.get("MaxAge")
        if age_min is not None or age_max is not None:
            self.tags.addWidget(_pill(f"Age {self._range_str(age_min, age_max)}"))
        part_min = r.get("MinParticipants"); part_max = r.get("MaxParticipants")
        if part_min is not None or part_max is not None:
            self.tags.addWidget(_pill(f"Participants {self._range_str(part_min, part_max)}"))

        # Lead time & Availability
        if r.get("LeadTimeDays") not in (None, ""):
            self.tags.addWidget(_pill(f"Lead {int(r['LeadTimeDays'])}d"))
        if r.get("Available") is not None:
            self.tags.addWidget(_pill("Available" if r["Available"] else "Unavailable"))

        # Pricing
        self.base_price.setText(self._money(r.get("BasePrice")))
        self.price_person.setText(self._money(r.get("PricePerPerson")))
        self.travel_base.setText(self._money(r.get("TravelFeeBase")))
        self.travel_per_km.setText(self._money(r.get("TravelFeePerKm"), suffix="/km"))

        # Meta & policy
        self._clear(self.meta_lay)
        self.meta_lay.addWidget(_kv("Short description", r.get("ShortDescription") or "—"))
        self.meta_lay.addWidget(_kv("Description",       r.get("Description") or "—"))
        self.meta_lay.addWidget(_kv("Vendor",            r.get("VendorName") or "—"))
        self.meta_lay.addWidget(_kv("Phone",             r.get("ContactPhone") or "—"))
        self.meta_lay.addWidget(_kv("Email",             r.get("ContactEmail") or "—"))
        self.meta_lay.addWidget(_kv("Region",            r.get("Region") or "—"))
        self.meta_lay.addWidget(_kv("Travel limit (km)", str(r.get("TravelLimitKm") if r.get("TravelLimitKm") not in (None, "") else "—")))
        self.meta_lay.addWidget(_kv("Cancellation policy", r.get("CancellationPolicy") or "—"))

    # ---------- Helpers ----------
    def _money(self, v, suffix: str = "") -> str:
        try:
            return (f"₪{float(v):.0f}{(' ' + suffix) if suffix else ''}") if v not in (None, "") else "—"
        except Exception:
            return str(v) if v not in (None, "") else "—"

    def _range_str(self, lo, hi) -> str:
        has_lo = lo not in (None, "")
        has_hi = hi not in (None, "")
        if has_lo and has_hi: return f"{lo}-{hi}"
        if has_lo:            return f"{lo}+"
        if has_hi:            return f"≤{hi}"
        return "—"

    def _clear(self, layout):
        while layout.count():
            it = layout.takeAt(0)
            w = it.widget()
            if w: w.setParent(None)

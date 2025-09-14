from pathlib import Path
from typing import Dict, Any
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
    QGridLayout, QMessageBox
)
from server.database.image_loader import load_into

BASE_DIR = Path(__file__).resolve().parent

def _title(text):
    lbl = QLabel(text); lbl.setStyleSheet("font-size:22px; font-weight:700;"); return lbl
def _sub(text):
    lbl = QLabel(text); lbl.setStyleSheet("color:#666;"); return lbl
def _pill(text):
    lbl = QLabel(text)
    lbl.setStyleSheet("padding:4px 8px; border-radius:12px; background:rgba(0,0,0,.06);")
    return lbl
def _kv(k, v):
    k_lbl = QLabel(k); k_lbl.setStyleSheet("color:#666;")
    v_lbl = QLabel(v or "—"); v_lbl.setWordWrap(True)
    row = QHBoxLayout(); w = QFrame(); w.setLayout(row)
    row.addWidget(k_lbl, 1); row.addWidget(v_lbl, 3)
    return w

class DecorDetailsView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Decoration – Details")
        self._build()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(10,10,10,10); root.setSpacing(10)

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        wrap = QFrame(); scroll.setWidget(wrap)
        root.addWidget(scroll, 1)

        lay = QVBoxLayout(wrap); lay.setSpacing(12)

        # Top card: image + titles
        top = QFrame(objectName="Card"); top_l = QHBoxLayout(top); top_l.setSpacing(14)
        self.photo = QLabel(); self.photo.setFixedSize(420, 260); self.photo.setAlignment(Qt.AlignCenter)
        info = QVBoxLayout()
        self.title = _title("Decor name")
        self.subtitle = _sub("Category · Theme")
        self.tags = QHBoxLayout(); self.tags.setSpacing(6)
        info.addWidget(self.title); info.addWidget(self.subtitle); info.addLayout(self.tags); info.addStretch(1)
        top_l.addWidget(self.photo); top_l.addLayout(info, 1)
        lay.addWidget(top)

        # Pricing card
        price = QFrame(objectName="Card"); p = QGridLayout(price); p.setHorizontalSpacing(18)
        self.p_small  = QLabel("—"); self.p_medium = QLabel("—"); self.p_large = QLabel("—"); self.delivery = QLabel("—")
        for w in (self.p_small, self.p_medium, self.p_large, self.delivery): w.setStyleSheet("font-weight:600;")
        p.addWidget(QLabel("Small venue"), 0,0); p.addWidget(self.p_small, 0,1)
        p.addWidget(QLabel("Medium venue"),1,0); p.addWidget(self.p_medium,1,1)
        p.addWidget(QLabel("Large venue"), 2,0); p.addWidget(self.p_large, 2,1)
        p.addWidget(QLabel("Delivery fee"),3,0); p.addWidget(self.delivery,3,1)
        lay.addWidget(price)

        # Meta/Policy card
        meta = QFrame(objectName="Card"); m = QVBoxLayout(meta); m.setSpacing(8)
        self.kv = QVBoxLayout(); self.kv.setSpacing(6)
        m.addLayout(self.kv)
        lay.addWidget(meta)

        self.setStyleSheet("""
            QFrame#Card { background:#fff; border:1px solid rgba(0,0,0,.07); border-radius:12px; padding:12px; }
        """)

    # Presenter API
    def set_busy(self, busy: bool): self.setDisabled(busy)
    def show_error(self, msg: str): QMessageBox.critical(self, "Error", msg)

    def populate(self, r: Dict[str, Any]):
        url = r.get("PhotoUrl") or "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/download.jpg"
        load_into(self.photo, url, placeholder=BASE_DIR / "placeholder_card.png", size=QSize(420,260))

        name = r.get("DecorName") or ""
        cat  = r.get("Category") or ""
        theme= r.get("Theme")
        self.title.setText(name)
        self.subtitle.setText(f"{cat}" + (f" · {theme}" if theme else ""))

        # tags
        self._clear(self.tags)
        if r.get("Region"): self.tags.addWidget(_pill(r["Region"]))
        self.tags.addWidget(_pill("Indoor" if r.get("Indoor") else "Outdoor/Indoor"))
        if r.get("RequiresElectricity"): self.tags.addWidget(_pill("Electricity"))
        if r.get("Available") is not None: self.tags.addWidget(_pill("Available" if r["Available"] else "Unavailable"))

        # pricing
        self.p_small.setText(self._fmt(r.get("PriceSmall")))
        self.p_medium.setText(self._fmt(r.get("PriceMedium")))
        self.p_large.setText(self._fmt(r.get("PriceLarge")))
        self.delivery.setText(self._fmt(r.get("DeliveryFee")))

        # meta/policy
        self._clear(self.kv)
        self.kv.addWidget(_kv("Description", r.get("Description") or "—"))
        self.kv.addWidget(_kv("Vendor", r.get("VendorName") or "—"))
        self.kv.addWidget(_kv("Phone", r.get("ContactPhone") or "—"))
        self.kv.addWidget(_kv("Email", r.get("ContactEmail") or "—"))
        self.kv.addWidget(_kv("Lead time (days)", str(r.get("LeadTimeDays") or "—")))
        self.kv.addWidget(_kv("Cancellation policy", r.get("CancellationPolicy") or "—"))

    def _fmt(self, v): return f"₪{float(v):.0f}" if v not in (None, "") else "—"
    def _clear(self, layout):
        while layout.count():
            it = layout.takeAt(0)
            w = it.widget()
            if w: w.setParent(None)

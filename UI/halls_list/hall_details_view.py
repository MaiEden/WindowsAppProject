from pathlib import Path
from typing import Dict, Any
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
    QGridLayout, QMessageBox, QPushButton
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

class HallDetailsView(QWidget):
    """
    Modern details page for Hall:
    - Image, title, subtitle (type · region · capacity)
    - Tags (parking, accessible)
    - Pricing block (per hour/day/person)
    - Location block (reverse geocoded address + quick links)
    - Contact & website
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hall – Details")
        self._build()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(10,10,10,10); root.setSpacing(10)

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        wrap = QFrame(); scroll.setWidget(wrap)
        root.addWidget(scroll, 1)

        lay = QVBoxLayout(wrap); lay.setSpacing(12)

        # Top card: image + titles + tags
        top = QFrame(objectName="Card"); top_l = QHBoxLayout(top); top_l.setSpacing(14)
        self.photo = QLabel(); self.photo.setFixedSize(420,260); self.photo.setAlignment(Qt.AlignCenter)

        info = QVBoxLayout()
        self.title = _title("Hall name")
        self.subtitle = _sub("Type · Region · Capacity")
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
        self.pph = QLabel("—"); self.ppd = QLabel("—"); self.ppp = QLabel("—")
        for w in (self.pph, self.ppd, self.ppp): w.setStyleSheet("font-weight:600;")
        p.addWidget(QLabel("Price per hour"),   0,0); p.addWidget(self.pph, 0,1)
        p.addWidget(QLabel("Price per day"),    1,0); p.addWidget(self.ppd, 1,1)
        p.addWidget(QLabel("Price per person"), 2,0); p.addWidget(self.ppp, 2,1)
        lay.addWidget(price)

        # Location card (address + map)
        loc = QFrame(objectName="Card"); L = QVBoxLayout(loc); L.setSpacing(8)
        self.addr_line = QLabel("—"); self.addr_line.setWordWrap(True)
        self.latlon_line = QLabel("—")
        self.buttons_row = QHBoxLayout(); self.buttons_row.setSpacing(8)
        self.btn_open_map = QPushButton("Open in Maps")
        self.btn_open_map.clicked.connect(self._open_maps)
        self.btn_copy_addr = QPushButton("Copy address")
        self.btn_copy_addr.clicked.connect(self._copy_address)
        self.buttons_row.addWidget(self.btn_open_map); self.buttons_row.addWidget(self.btn_copy_addr); self.buttons_row.addStretch(1)
        L.addWidget(QLabel("Location")); L.addWidget(self.addr_line); L.addWidget(self.latlon_line); L.addLayout(self.buttons_row)
        lay.addWidget(loc)

        # Contact / Website card
        meta = QFrame(objectName="Card"); M = QVBoxLayout(meta); M.setSpacing(6)
        self.meta_lay = M
        lay.addWidget(meta)

        self.setStyleSheet("""
            QFrame#Card{
                background:#fff;
                border:1px solid rgba(0,0,0,.07);
                border-radius:12px;
                padding:12px;
            }
        """)

        # state
        self._current_coords = None
        self._current_addr_str = None
        self._website_url = None

    # Presenter API
    def set_busy(self, busy: bool): self.setDisabled(busy)
    def show_error(self, msg: str): QMessageBox.critical(self, "Error", msg)

    def populate(self, r: Dict[str, Any]):
        # Image
        url = r.get("PhotoUrl") or "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/dfault.png"
        load_into(self.photo, url, size=QSize(420,260))

        # Titles
        name = r.get("HallName") or ""
        typ  = r.get("HallType") or ""
        region = r.get("Region") or ""
        cap = r.get("Capacity")
        cap_str = f"{cap} ppl" if cap not in (None, "") else "—"
        self.title.setText(name)
        self.subtitle.setText(f"{typ} · {region} · {cap_str}")

        # Tags
        self._clear(self.tags)
        if bool(r.get("ParkingAvailable")):     self.tags.addWidget(_pill("Parking"))
        if bool(r.get("WheelchairAccessible")): self.tags.addWidget(_pill("Accessible"))

        # Pricing
        self.pph.setText(self._money(r.get("PricePerHour")))
        self.ppd.setText(self._money(r.get("PricePerDay")))
        self.ppp.setText(self._money(r.get("PricePerPerson")))

        # Location (server may add Address dict)
        lat = r.get("Latitude"); lon = r.get("Longitude")
        self._current_coords = (lat, lon) if (lat not in (None,"") and lon not in (None,"")) else None

        addr = r.get("Address") or {}
        addr_str = addr.get("formatted_address") or addr.get("display_name")
        self._current_addr_str = addr_str
        self.addr_line.setText(addr_str or "—")

        if self._current_coords:
            self.latlon_line.setText(f"({float(lat):.6f}, {float(lon):.6f})")
            self.btn_open_map.setEnabled(True)
            self.btn_copy_addr.setEnabled(bool(addr_str))
        else:
            self.latlon_line.setText("—")
            self.btn_open_map.setEnabled(False)
            self.btn_copy_addr.setEnabled(False)

        # Contact / website
        self._clear(self.meta_lay)
        self.meta_lay.addWidget(_kv("Phone",   r.get("ContactPhone") or "—"))
        self.meta_lay.addWidget(_kv("Email",   r.get("ContactEmail") or "—"))
        self._website_url = r.get("WebsiteUrl")
        self.meta_lay.addWidget(_kv("Website", self._website_url or "—"))

    # Actions
    def _open_maps(self):
        if not self._current_coords: return
        lat, lon = self._current_coords
        url = QUrl(f"https://www.google.com/maps?q={lat},{lon}")
        QDesktopServices.openUrl(url)

    def _copy_address(self):
        if not self._current_addr_str: return
        cb = self.clipboard() if hasattr(self, "clipboard") else None
        try:
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(self._current_addr_str)
        except Exception:
            pass  # לא נכשיל את המסך על העתקה

    # Helpers
    def _money(self, v) -> str:
        try:
            return f"₪{float(v):.0f}" if v not in (None, "") else "—"
        except Exception:
            return str(v) if v not in (None, "") else "—"

    def _clear(self, layout):
        while layout.count():
            it = layout.takeAt(0)
            w = it.widget()
            if w: w.setParent(None)

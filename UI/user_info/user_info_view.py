# user_info_view.py
from pathlib import Path
from typing import List, Dict, Optional

from PySide6.QtCore import Qt, QSize, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
    QSizePolicy, QToolButton, QSpacerItem, QGraphicsDropShadowEffect
)

# טעינת תמונות – כמו בשאר ה־Views
from server.database.image_loader import load_into

BASE_DIR = Path(__file__).resolve().parent
STYLE_DIR = BASE_DIR.parent / "style&icons"

def _shadow(w, radius=18, x_offset=0, y_offset=6):
    eff = QGraphicsDropShadowEffect(w); eff.setBlurRadius(radius); eff.setOffset(x_offset, y_offset)
    w.setGraphicsEffect(eff)

class MiniCard(QFrame):
    clicked = Signal(int)  # id

    def __init__(self, vm: Dict):
        super().__init__(objectName="Card")
        self.vm = vm
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        _shadow(self, 18, 0, 6)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10); lay.setSpacing(10)

        # Image
        img = QLabel(objectName="CardImage"); img.setFixedSize(96, 64); img.setAlignment(Qt.AlignCenter)
        url = vm.get("photo") or "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/download.jpg"
        load_into(img, url, placeholder=STYLE_DIR / "placeholder_card.png", size=QSize(160, 96))

        # Texts
        text_box = QVBoxLayout(); text_box.setSpacing(2)
        title = QLabel(vm.get("title",""), objectName="CardTitle")
        subtitle = QLabel(vm.get("subtitle",""), objectName="CardSubtitle")

        meta = QHBoxLayout()
        region = QLabel(vm.get("region") or "", objectName="Region")
        pill = QLabel(vm.get("pill",""), objectName="Pill"); pill.setProperty("ok", True)
        meta.addWidget(region); meta.addWidget(pill)

        text_box.addWidget(title); text_box.addWidget(subtitle); text_box.addLayout(meta)

        lay.addWidget(img, 0)
        lay.addLayout(text_box, 1)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(int(self.vm.get("id") or -1))
        super().mouseReleaseEvent(e)


class CollapsibleSection(QWidget):
    def __init__(self, title: str, count: int = 0, start_open: bool = True):
        super().__init__()
        self._open = start_open
        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(6)

        header = QFrame(objectName="Card")
        _shadow(header, 14, 0, 4)
        h = QHBoxLayout(header); h.setContentsMargins(10,8,10,8); h.setSpacing(8)

        self.btn = QToolButton(text=("▼" if start_open else "►"))
        self.btn.setCursor(Qt.PointingHandCursor); self.btn.setAutoRaise(True)
        self.btn.clicked.connect(self.toggle)

        self.title = QLabel(f"{title}  ·  {count}", objectName="CardTitle")
        h.addWidget(self.btn, 0); h.addWidget(self.title, 0); h.addStretch(1)

        self.body = QWidget(); b = QVBoxLayout(self.body)
        b.setContentsMargins(8,8,8,8); b.setSpacing(10)

        root.addWidget(header); root.addWidget(self.body)

    def set_count(self, n: int):
        txt = self.title.text().split("·")[0].strip()
        self.title.setText(f"{txt}  ·  {n}")

    def set_content(self, cards: List[Dict]):
        # clear
        lay: QVBoxLayout = self.body.layout()  # type: ignore
        while lay.count():
            it = lay.takeAt(0)
            w = it.widget()
            if w: w.setParent(None)

        if not cards:
            empty = QLabel("No items", alignment=Qt.AlignCenter)
            laid = QVBoxLayout(); self.body.setLayout(laid) if lay is None else None
            lay.addWidget(empty)
            return

        for vm in cards:
            card = MiniCard(vm)
            lay.addWidget(card)

        lay.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.set_count(len(cards))
        self.body.setVisible(self._open)

    def toggle(self):
        self._open = not self._open
        self.btn.setText("▼" if self._open else "►")
        self.body.setVisible(self._open)


class UserInfoView(QWidget):
    # אפשר להוסיף אותות קליקים בהמשך (לדפדוף לפרטי דקור/שירות/אולם), כרגע תצוגה בלבד
    refreshRequested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Info")
        self._build()
        self._load_qss()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12,12,12,12); root.setSpacing(10)

        # Top card with avatar + basics
        top = QFrame(objectName="Card"); _shadow(top, 18, 0, 6)
        tl = QHBoxLayout(top); tl.setContentsMargins(12,12,12,12); tl.setSpacing(12)

        self.avatar = QLabel("👤", alignment=Qt.AlignCenter)
        self.avatar.setFixedSize(96, 96)
        self.avatar.setStyleSheet("""
            QLabel { border-radius: 48px; background: #f5f5f5; font-size:42px; }
        """)

        info = QVBoxLayout(); info.setSpacing(2)
        self.name  = QLabel("", objectName="CardTitle")
        self.phone = QLabel("", objectName="CardSubtitle")
        self.region = QLabel("", objectName="Region")

        info.addWidget(self.name); info.addWidget(self.phone); info.addWidget(self.region)
        tl.addWidget(self.avatar, 0); tl.addLayout(info, 1)

        # Scrollable content
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        wrap = QWidget(); body = QVBoxLayout(wrap); body.setContentsMargins(0,0,0,0); body.setSpacing(12)

        self.sec_decors   = CollapsibleSection("Decorations used", start_open=True)
        self.sec_services = CollapsibleSection("Services used",   start_open=True)
        self.sec_halls    = CollapsibleSection("Halls used",      start_open=True)

        body.addWidget(self.sec_decors)
        body.addWidget(self.sec_services)
        body.addWidget(self.sec_halls)
        body.addItem(QSpacerItem(0,0,QSizePolicy.Minimum, QSizePolicy.Expanding))
        scroll.setWidget(wrap)

        root.addWidget(top, 0)
        root.addWidget(scroll, 1)

    def _load_qss(self):
        # להשתמש באותו QSS כדי לשמור אחידות
        qss_path = STYLE_DIR / "list_style.qss"
        if qss_path.exists():
            self.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    # ----- Presenter API -----
    def set_user_header(self, name: str, phone: str, region: str, avatar_url: Optional[str] = None):
        self.name.setText(name or "")
        self.phone.setText(phone or "")
        self.region.setText(region or "")
        if avatar_url:
            # ננסה לטעון תמונת פרופיל אם תספקי בהמשך
            load_into(self.avatar, avatar_url, placeholder=STYLE_DIR / "avatar_placeholder.png", size=QSize(96,96))

    def show_decor_cards(self, items: List[Dict]):   self.sec_decors.set_content(items)
    def show_service_cards(self, items: List[Dict]): self.sec_services.set_content(items)
    def show_hall_cards(self, items: List[Dict]):    self.sec_halls.set_content(items)

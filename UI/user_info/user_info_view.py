from pathlib import Path
from typing import List, Dict, Optional

from PySide6.QtCore import Qt, QSize, Signal, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
    QSizePolicy, QToolButton, QSpacerItem, QGraphicsDropShadowEffect, QGridLayout
)

# Image loading (same helper you already use)
from server.database.image_loader import load_into

BASE_DIR = Path(__file__).resolve().parent
STYLE_DIR = BASE_DIR.parent / "style&icons"

def _shadow(w, radius=18, x_offset=0, y_offset=6):
    eff = QGraphicsDropShadowEffect(w); eff.setBlurRadius(radius); eff.setOffset(x_offset, y_offset)
    w.setGraphicsEffect(eff)

def _section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("SectionLabel")
    lbl.setStyleSheet("""
        QLabel {
            color: #374151;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.3px;
            padding: 2px 0;
            margin-left: 2px;
        }
    """)
    return lbl


class CompactCard(QFrame):
    """Compact tile card used in grids."""
    clicked = Signal(int)

    def __init__(self, vm: Dict):
        super().__init__(objectName="Card")
        self.vm = vm
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)
        self.setMinimumSize(220, 180)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        _shadow(self, radius=12, y_offset=4)

        # Hover animation
        self._base_geom: Optional[QRect] = None
        self._anim = QPropertyAnimation(self, b"geometry", self)
        self._anim.setDuration(140)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._grow_px = 6

        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 10)
        lay.setSpacing(6)

        # Image
        img = QLabel(objectName="CardImage")
        img.setFixedHeight(100)
        img.setAlignment(Qt.AlignCenter)

        url = self.vm.get("photo") or "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/download.jpg"
        load_into(img, url, placeholder=STYLE_DIR / "placeholder_card.png", size=QSize(280, 100))

        # Title
        title = QLabel(self.vm.get("title", ""), objectName="CardTitle")
        title.setWordWrap(True)

        # Subtitle
        subtitle = QLabel(self.vm.get("subtitle", ""), objectName="CardSubtitle")
        subtitle.setWordWrap(True)

        # Bottom meta - region + pill
        meta = QHBoxLayout()
        region = QLabel(self.vm.get("region") or "", objectName="Region")
        pill = QLabel(self.vm.get("pill", ""), objectName="Pill")
        pill.setProperty("ok", True)

        meta.addWidget(region)
        meta.addStretch(1)
        meta.addWidget(pill)

        lay.addWidget(img)
        lay.addWidget(title)
        lay.addWidget(subtitle)
        lay.addLayout(meta)

    # Hover effects
    def enterEvent(self, e):
        if self._base_geom is None:
            self._base_geom = self.geometry()
        g = self._base_geom
        grow = self._grow_px
        target = QRect(g.x() - grow // 2, g.y() - grow // 2, g.width() + grow, g.height() + grow)
        self._anim.stop()
        self._anim.setStartValue(self.geometry())
        self._anim.setEndValue(target)
        self._anim.start()
        super().enterEvent(e)

    def leaveEvent(self, e):
        if self._base_geom is not None:
            self._anim.stop()
            self._anim.setStartValue(self.geometry())
            self._anim.setEndValue(self._base_geom)
            self._anim.start()
        super().leaveEvent(e)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(int(self.vm.get("id") or -1))
        super().mouseReleaseEvent(e)


class AddNewCard(QFrame):
    clicked = Signal()
    """A 'plus' card placeholder for future 'add new owned item' screen."""
    def __init__(self):
        super().__init__(objectName="Card")
        self.setMinimumSize(220, 180)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        _shadow(self, radius=12, y_offset=4)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 10)
        lay.setSpacing(6)

        icon = QLabel("+", alignment=Qt.AlignCenter)
        icon.setFixedHeight(100)
        icon.setStyleSheet("""
            QLabel {
                font-size: 40px;
                color: #6b7280;
                border: 2px dashed #d1d5db;
                border-radius: 12px;
                background: #fafafa;
            }
        """)

        title = QLabel("Add new", objectName="CardTitle")
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("Owned item shortcut", objectName="CardSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        lay.addWidget(icon)
        lay.addWidget(title)
        lay.addWidget(subtitle)
        lay.addStretch(1)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(e)


class MinimalSection(QWidget):
    """Collapsible section with a clean grid of cards."""
    addNewRequested = Signal()

    def __init__(self, title: str, count: int = 0, start_open: bool = True):
        super().__init__()
        self._open = start_open
        self._cards_cache: List[Dict] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        # Header bar
        header = QFrame()
        header.setFixedHeight(36)
        header.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
            QFrame:hover {
                border-color: #d1d5db;
                background: #f9fafb;
            }
        """)

        h = QHBoxLayout(header)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(8)

        self.btn = QToolButton(text=("∨" if start_open else ">"))
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.setAutoRaise(True)
        self.btn.setFixedSize(20, 20)
        self.btn.setStyleSheet("""
            QToolButton {
                border: none;
                background: transparent;
                color: #6b7280;
                font-size: 12px;
                font-weight: bold;
            }
            QToolButton:hover {
                color: #374151;
                background: #f3f4f6;
                border-radius: 4px;
            }
        """)
        self.btn.clicked.connect(self.toggle)

        self.title = QLabel(f"{title} · {count}")
        self.title.setStyleSheet("""
            QLabel {
                color: #374151;
                font-size: 14px;
                font-weight: 600;
                border: none;
                background: transparent;
            }
        """)

        h.addWidget(self.btn, 0)
        h.addWidget(self.title, 0)
        h.addStretch(1)

        # Body grid (no inner scroll)
        self.body = QWidget()
        self.grid = QGridLayout(self.body)
        self.grid.setContentsMargins(0, 8, 0, 0)
        self.grid.setHorizontalSpacing(12)
        self.grid.setVerticalSpacing(12)

        root.addWidget(header)
        root.addWidget(self.body)

        self.body.setVisible(self._open)

    def set_count(self, n: int):
        txt = self.title.text().split("·")[0].strip()
        self.title.setText(f"{txt} · {n}")
        self.title.setStyleSheet("""
            QLabel {
                color: #374151;
                font-size: 14px;
                font-weight: 600;
                border: none;
                background: transparent;
            }
        """)

    def set_content(self, cards: List[Dict], *, include_add_card: bool = False):
        self._cards_cache = cards.copy()
        if include_add_card:
            # Append a special marker dict; handled in _rebuild_grid
            self._cards_cache.append({"__add_card__": True})
        self._rebuild_grid()

    def _rebuild_grid(self):
        # Clear existing
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        cards = self._cards_cache
        if not cards:
            empty = QLabel("No items", alignment=Qt.AlignCenter)
            empty.setStyleSheet("color: #999; font-style: italic; padding: 20px;")
            self.grid.addWidget(empty, 0, 0)
            self.set_count(0)
            return

        # Columns based on parent width
        parent_width = self.width() if self.width() > 0 else 800
        card_width = 240
        cols = max(1, (parent_width - 40) // card_width)

        row = col = 0
        for vm in cards:
            if vm.get("__add_card__"):
                card = AddNewCard()
                # NEW: route the click of the '+' card to the section signal
                card.clicked.connect(self.addNewRequested)
            else:
                card = CompactCard(vm)
            self.grid.addWidget(card, row, col)
            col += 1
            if col >= cols:
                row += 1
                col = 0

        # Spacer to push cards up
        self.grid.addItem(
            QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding),
            row + 1, 0, 1, cols
        )

        # Do not count the add-card in the total
        logical_count = len([c for c in cards if not c.get("__add_card__")])
        self.set_count(logical_count)

    def toggle(self):
        self._open = not self._open
        self.btn.setText("∨" if self._open else ">")
        self.body.setVisible(self._open)

        if self._open and self._cards_cache:
            QTimer.singleShot(50, self._rebuild_grid)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._open and self._cards_cache:
            QTimer.singleShot(50, self._rebuild_grid)


class UserInfoView(QWidget):
    refreshRequested = Signal()
    addDecorClicked = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Info")
        self.resize(1000, 700)
        self._build()
        self._load_qss()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # Top card
        top = QFrame(objectName="Card")
        top.setFixedHeight(100)
        _shadow(top, 12, 0, 4)

        tl = QHBoxLayout(top)
        tl.setContentsMargins(16, 12, 16, 12)
        tl.setSpacing(16)

        # Avatar
        self.avatar = QLabel("👤", alignment=Qt.AlignCenter)
        self.avatar.setFixedSize(64, 64)
        self.avatar.setStyleSheet("""
            QLabel { 
                border-radius: 32px; 
                background: #f5f5f5; 
                font-size: 28px; 
                border: 2px solid #e0e0e0;
            }
        """)

        # User info (name + single meta line: phone · region)
        info = QVBoxLayout()
        info.setSpacing(2)
        self.name = QLabel("", objectName="CardTitle")
        # 'meta' shows phone and region on the same line
        self.meta = QLabel("", objectName="CardSubtitle")

        info.addWidget(self.name)
        info.addWidget(self.meta)

        tl.addWidget(self.avatar, 0)
        tl.addLayout(info, 1)

        # Main scroll area
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        # Recently used section label
        content_layout.addWidget(_section_label("Recently used"))

        # Recently used sections
        self.sec_decors = MinimalSection("Decorations", start_open=True)
        self.sec_services = MinimalSection("Services", start_open=True)
        self.sec_halls = MinimalSection("Halls", start_open=True)

        content_layout.addWidget(self.sec_decors)
        content_layout.addWidget(self.sec_services)
        content_layout.addWidget(self.sec_halls)

        # Owned by me section label
        content_layout.addWidget(_section_label("Owned by me"))

        # Owned items (same card design). Includes a '+' add-new card at the end.
        self.sec_owned = MinimalSection("Owned items", start_open=True)
        content_layout.addWidget(self.sec_owned)

        content_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_scroll.setWidget(content_widget)

        root.addWidget(top, 0)
        root.addWidget(main_scroll, 1)

        # NEW: click on the '+' card in Owned -> bubble up to the view signal
        self.sec_owned.addNewRequested.connect(self.addDecorClicked)

    def _load_qss(self):
        qss_path = STYLE_DIR / "list_style.qss"
        if qss_path.exists():
            self.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    # ----- Presenter API -----
    def set_user_header(self, name: str, phone: str, region: str, avatar_url: Optional[str] = None):
        self.name.setText(name or "")
        # Build 'phone · region' line (hide dot when one side is missing)
        parts = [p for p in [phone.strip() if phone else "", region.strip() if region else ""] if p]
        self.meta.setText(" · ".join(parts))
        if avatar_url:
            load_into(self.avatar, avatar_url, placeholder=STYLE_DIR / "avatar_placeholder.png", size=QSize(64, 64))

    def show_decor_cards(self, items: List[Dict]):
        self.sec_decors.set_content(items)

    def show_service_cards(self, items: List[Dict]):
        self.sec_services.set_content(items)

    def show_hall_cards(self, items: List[Dict]):
        self.sec_halls.set_content(items)

    def show_owned_cards(self, items: List[Dict]):
        # Include a static add-new card at the end and keep it clickable
        self.sec_owned.set_content(items, include_add_card=True)

"""
View: Modern card grid + search/type/accessibility filters for Halls
- Loads QSS from 'list_style.qss'
- Card shows subset: image, title, subtitle, price, region, accessibility pill
"""
from pathlib import Path
from typing import Optional, List, Dict

from PySide6.QtCore import Qt, QSize, Signal, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox,
    QPushButton, QScrollArea, QFrame, QGridLayout, QSizePolicy, QSpacerItem,
    QMessageBox, QGraphicsDropShadowEffect
)

# שימוש בפונקציה החיצונית לטעינת תמונות
from server.database.image_loader import load_into

BASE_DIR = Path(__file__).resolve().parent


def _apply_shadow(widget, radius=18, x_offset=0, y_offset=6):
    eff = QGraphicsDropShadowEffect(widget)
    eff.setBlurRadius(radius)
    eff.setOffset(x_offset, y_offset)
    widget.setGraphicsEffect(eff)


class HallCard(QFrame):
    clicked = Signal(int)

    def __init__(self, vm: Dict):
        super().__init__(objectName="Card")
        self.vm = vm
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)
        self.setMinimumSize(300, 270)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        _apply_shadow(self, radius=18, y_offset=6)

        # Hover animation
        self._base_geom: Optional[QRect] = None
        self._anim = QPropertyAnimation(self, b"geometry", self)
        self._anim.setDuration(140)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._grow_px = 8

        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 12)
        lay.setSpacing(8)

        # Image
        img = QLabel(objectName="CardImage")
        img.setFixedHeight(160)
        img.setAlignment(Qt.AlignCenter)
        self._img = img

        # URL from VM or default
        url = self.vm.get("photo") or "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/dfault.png"
        load_into(img, url, size=QSize(420, 160))

        title = QLabel(self.vm.get("title", ""), objectName="CardTitle")
        subtitle = QLabel(self.vm.get("subtitle", ""), objectName="CardSubtitle")

        meta = QHBoxLayout()
        price = QLabel(self.vm.get("price", ""), objectName="Price")
        region = QLabel(self.vm.get("region") or "", objectName="Region")
        pill = QLabel("Accessible" if self.vm.get("accessible") else "Not accessible", objectName="Pill")
        pill.setProperty("ok", bool(self.vm.get("accessible")))
        meta.addWidget(price)
        meta.addStretch(1)
        meta.addWidget(region)
        meta.addWidget(pill)

        lay.addWidget(img)
        lay.addSpacing(6)
        lay.addWidget(title)
        lay.addWidget(subtitle)
        lay.addLayout(meta)

    # --- Hover grow/shrink ---
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

    # --- Click handling ---
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(int(self.vm.get("id") or -1))
        super().mouseReleaseEvent(e)


class HallListView(QWidget):
    # View -> Presenter
    searchChanged = Signal(str)
    typeChanged = Signal(str)
    accessibleChanged = Signal(bool)
    refreshRequested = Signal()
    cardClicked = Signal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Halls Catalog")
        self.resize(1120, 720)
        self._cards_cache: List[Dict] = []
        self._build()
        self._load_qss()

    def showEvent(self, e):
        super().showEvent(e)
        QTimer.singleShot(0, self._rebuild_grid)

    # ---------- UI ----------
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # Toolbar
        bar = QHBoxLayout()
        self.search = QLineEdit(placeholderText="Search by name, type or region…")
        self.search.textChanged.connect(lambda s: self.searchChanged.emit(s))

        self.hall_type = QComboBox()
        self.hall_type.currentTextChanged.connect(lambda s: self.typeChanged.emit(s))

        self.accessible = QCheckBox("Accessible only")
        self.accessible.toggled.connect(lambda b: self.accessibleChanged.emit(b))

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refreshRequested.emit)

        bar.addWidget(self.search, 3)
        bar.addWidget(self.hall_type, 0)
        bar.addWidget(self.accessible, 0)
        bar.addStretch(1)
        bar.addWidget(self.refresh_btn, 0)
        root.addLayout(bar)

        # Scrollable responsive grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        wrap = QWidget()
        self.grid = QGridLayout(wrap)
        self.grid.setContentsMargins(4, 4, 4, 4)
        self.grid.setHorizontalSpacing(16)
        self.grid.setVerticalSpacing(16)
        self.scroll.setWidget(wrap)
        root.addWidget(self.scroll)

        self.empty = QLabel("No results", alignment=Qt.AlignCenter)
        self.empty.setVisible(False)
        root.addWidget(self.empty)

    # set stylesheet from external QSS file
    def _load_qss(self):
        from pathlib import Path
        qss_path = Path(__file__).resolve().parent.parent / "style&icons" / "list_style.qss"
        if qss_path.exists():
            self.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    # ---------- Presenter API ----------
    def set_busy(self, busy: bool):
        self.setDisabled(busy)

    def show_error(self, msg: str):
        QMessageBox.critical(self, "Error", msg)

    def populate_types(self, types: List[str]):
        self.hall_type.blockSignals(True)
        self.hall_type.clear()
        self.hall_type.addItems(types)
        self.hall_type.blockSignals(False)

    def get_search_text(self) -> str:
        return self.search.text()

    def get_selected_type(self) -> str:
        return self.hall_type.currentText()

    def get_accessible_only(self) -> bool:
        return self.accessible.isChecked()

    def show_cards(self, cards: List[Dict]):
        self._cards_cache = cards
        self._rebuild_grid()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self._cards_cache:
            self._rebuild_grid()

    # Responsive grid: number of columns based on viewport width
    def _rebuild_grid(self):
        # clear
        while self.grid.count():
            it = self.grid.takeAt(0)
            w = it.widget()
            if w:
                w.setParent(None)

        if not self._cards_cache:
            self.empty.setVisible(True)
            return
        self.empty.setVisible(False)

        viewport_w = self.scroll.viewport().contentsRect().width()
        card_w = 340
        cols = max(1, viewport_w // card_w)

        r = c = 0
        for vm in self._cards_cache:
            card = HallCard(vm)
            card.clicked.connect(lambda _id, v=vm: self.cardClicked.emit(int(v.get("id") or -1)))
            self.grid.addWidget(card, r, c)
            c += 1
            if c >= cols:
                r += 1
                c = 0

        # vertical spacer to pin cards to top
        self.grid.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), r + 1, 0, 1, cols)
        self.grid.setRowStretch(r + 1, 1)

"""
View: Modern card grid + search/category/availability filters
"""
from typing import Optional, List, Dict
from PySide6.QtCore import (Qt, QSize, Signal,
                            QPropertyAnimation, QEasingCurve, QRect, QTimer)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox,
    QPushButton, QScrollArea, QFrame, QGridLayout, QSizePolicy, QSpacerItem,
    QMessageBox, QGraphicsDropShadowEffect)
from server.database.image_loader import load_into

def _apply_shadow(widget, radius=18, x_offset=0, y_offset=6):
    """Apply a soft drop-shadow to visually elevate the card from the background."""
    eff = QGraphicsDropShadowEffect(widget)
    eff.setBlurRadius(radius)
    eff.setOffset(x_offset, y_offset)
    widget.setGraphicsEffect(eff)

class ServiceCard(QFrame):
    """A single service card"""
    clicked = Signal(int)

    def __init__(self, vm: Dict):
        """
        vm (view-model dict) is expected to include:
          id, photo, title, subtitle, region, available
        """
        super().__init__(objectName="Card")
        self.vm = vm
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)
        self.setMinimumSize(300, 270)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        _apply_shadow(self, radius=18, y_offset=6)

        # Hover animation (gentle grow/shrink by a few pixels)
        self._base_geom: Optional[QRect] = None
        self._anim = QPropertyAnimation(self, b"geometry", self)
        self._anim.setDuration(140)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._grow_px = 8

        self._build()

    def _build(self):
        """Assemble the card layout and start the async image load."""
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 12)
        lay.setSpacing(8)

        # Image area
        img = QLabel(objectName="CardImage")
        img.setFixedHeight(160)
        img.setAlignment(Qt.AlignCenter)
        self._img = img

        # Use provided image or a CDN placeholder
        url = self.vm.get("photo") or "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/dfault.png"
        load_into(img, url, size=QSize(420, 160))

        # Text fields
        title = QLabel(self.vm.get("title", ""), objectName="CardTitle")
        subtitle = QLabel(self.vm.get("subtitle", ""), objectName="CardSubtitle")

        # Meta row: region + availability pill (styled via QSS using 'ok' property)
        meta = QHBoxLayout()
        region = QLabel(self.vm.get("region") or "", objectName="Region")
        pill = QLabel("Available" if self.vm.get("available") else "Unavailable", objectName="Pill")
        pill.setProperty("ok", bool(self.vm.get("available")))
        meta.addWidget(region)
        meta.addWidget(pill)

        # Compose
        lay.addWidget(img)
        lay.addSpacing(6)
        lay.addWidget(title)
        lay.addWidget(subtitle)
        lay.addLayout(meta)

    # --- Hover grow/shrink ---
    def enterEvent(self, e):
        """Animate a slight grow on hover based on the initial geometry."""
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
        """Return to the base geometry when the cursor leaves the card."""
        if self._base_geom is not None:
            self._anim.stop()
            self._anim.setStartValue(self.geometry())
            self._anim.setEndValue(self._base_geom)
            self._anim.start()
        super().leaveEvent(e)

    def mouseReleaseEvent(self, e):
        """Emit the card id on left-button release (click)."""
        if e.button() == Qt.LeftButton:
            self.clicked.emit(int(self.vm.get("id") or -1))
        super().mouseReleaseEvent(e)


class ServiceListView(QWidget):
    """
    Main list view for Services.
    """
    # View -> Presenter signals
    searchChanged = Signal(str)
    categoryChanged = Signal(str)
    availableChanged = Signal(bool)
    refreshRequested = Signal()
    cardClicked = Signal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Services Catalog")
        self.resize(1120, 720)
        self._cards_cache: List[Dict] = []
        self._build()
        self._load_qss()

    def showEvent(self, e):
        super().showEvent(e)
        QTimer.singleShot(0, self._rebuild_grid)

    def _build(self):
        """Construct toolbar (search/filters), scroll area, grid, and empty-state label."""
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # --- Toolbar ----------------------------------------------------------
        bar = QHBoxLayout()
        self.search = QLineEdit(placeholderText="Search services by name, description or subcategory…")
        self.search.textChanged.connect(lambda s: self.searchChanged.emit(s))

        self.category = QComboBox()
        self.category.currentTextChanged.connect(lambda s: self.categoryChanged.emit(s))

        self.available = QCheckBox("Available only")
        self.available.toggled.connect(lambda b: self.availableChanged.emit(b))

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refreshRequested.emit)

        bar.addWidget(self.search, 3)
        bar.addWidget(self.category, 0)
        bar.addWidget(self.available, 0)
        bar.addStretch(1)
        bar.addWidget(self.refresh_btn, 0)
        root.addLayout(bar)

        # --- Scrollable responsive grid --------------------------------------
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

        # Empty-state label (shown when there are no cards)
        self.empty = QLabel("No results", alignment=Qt.AlignCenter)
        self.empty.setVisible(False)
        root.addWidget(self.empty)

    def _load_qss(self):
        """Load and apply external QSS (keeps most styling out of the code)."""
        from pathlib import Path
        qss_path = Path(__file__).resolve().parent.parent / "style&icons" / "list_style.qss"
        if qss_path.exists():
            self.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    # --- Presenter API --------------------------------------------------------
    def set_busy(self, busy: bool):
        """Enable/disable the whole view (useful while fetching data)."""
        self.setDisabled(busy)

    def show_error(self, msg: str):
        """Show a blocking error dialog."""
        QMessageBox.critical(self, "Error", msg)

    def populate_categories(self, cats: List[str]):
        """Fill the category combo without emitting change events during the update."""
        self.category.blockSignals(True)
        self.category.clear()
        self.category.addItems(cats)
        self.category.blockSignals(False)

    def get_search_text(self) -> str:
        """Return the current search text."""
        return self.search.text()

    def get_selected_category(self) -> str:
        """Return the selected category."""
        return self.category.currentText()

    def get_available_only(self) -> bool:
        """Return True when 'Available only' is checked."""
        return self.available.isChecked()

    def show_cards(self, cards: List[Dict]):
        """Receive cards from the presenter and rebuild the grid."""
        self._cards_cache = cards
        self._rebuild_grid()

    def resizeEvent(self, e):
        """Recompute layout on resize to keep the grid responsive."""
        super().resizeEvent(e)
        if self._cards_cache:
            self._rebuild_grid()

    def _rebuild_grid(self):
        """
        Populate the grid with ServiceCard widgets.

        The number of columns is derived from the viewport width to achieve a
        responsive layout. We also clear previous widgets safely to avoid leaks.
        """
        # Clear existing items/widgets
        while self.grid.count():
            it = self.grid.takeAt(0)
            w = it.widget()
            if w:
                w.setParent(None)

        # Handle empty state
        if not self._cards_cache:
            self.empty.setVisible(True)
            return
        self.empty.setVisible(False)

        # Determine column count from viewport width
        viewport_w = self.scroll.viewport().contentsRect().width()
        card_w = 340  # nominal card width for column calculation
        cols = max(1, viewport_w // card_w)

        # Add cards row-by-row
        r = c = 0
        for vm in self._cards_cache:
            card = ServiceCard(vm)
            card.clicked.connect(lambda _id, v=vm: self.cardClicked.emit(int(v.get("id") or -1)))
            self.grid.addWidget(card, r, c)
            c += 1
            if c >= cols:
                r += 1
                c = 0

        # Add a vertical spacer to keep cards pinned to the top
        self.grid.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), r + 1, 0, 1, cols)
        self.grid.setRowStretch(r + 1, 1)
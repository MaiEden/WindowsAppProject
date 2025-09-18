# UI/user_info/user_info_view.py
"""
Qt view for the "User Info" page.

- Header with avatar/name/meta.
- Sections rendered as responsive grids of compact cards.
- "Owned items" supports a graph button per card and an "Add new" card.
- Styles loaded from a local QSS file.
"""

from pathlib import Path
from typing import List, Dict, Optional

from PySide6.QtCore import Qt, QSize, Signal, QTimer
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
    QSizePolicy, QToolButton, QSpacerItem, QGridLayout, QAbstractScrollArea
)

# Image loading helper
from server.database.image_loader import load_into

BASE_DIR = Path(__file__).resolve().parent
STYLE_DIR = BASE_DIR.parent / "style&icons"
LOCAL_QSS = BASE_DIR / "user_info_view.qss"


# ------------------------------
# Helpers
# ------------------------------

def _section_label(text: str) -> QLabel:
    """Create a section header label (styled via QSS)."""
    lbl = QLabel(text); lbl.setObjectName("SectionLabel")
    return lbl


def _render_svg_to_icon(svg_data: bytes, size: int = 22) -> QIcon:
    """
    Render crisp SVG to an icon (graph) of the given size (DPI aware, anti-aliased).
    """
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform, True)
    ren = QSvgRenderer(svg_data)
    ren.render(p)
    p.end()
    return QIcon(pix)


GRAPH_SVG = b"""
<svg width="22" height="22" viewBox="0 0 24 24" fill="none"
     xmlns="http://www.w3.org/2000/svg">
  <rect x="4" y="13" width="3.5" height="7" rx="1.2" fill="#2563EB"/>
  <rect x="10.25" y="9" width="3.5" height="11" rx="1.2" fill="#2563EB"/>
  <rect x="16.5" y="5" width="3.5" height="15" rx="1.2" fill="#2563EB"/>
</svg>
"""


# ------------------------------
# Cards
# ------------------------------

class CompactCard(QFrame):
    """
    Compact card used in grids.
    Signals:
        clicked(int): Emitted on left-click with item id.
        graphClicked(int): Emitted when the graph button is clicked (owned section only).
    VM keys typically used: id, photo, title/name, subtitle, region, pill.
    """
    clicked = Signal(int)
    graphClicked = Signal(int)

    CARD_W = 360
    CARD_H = 300

    def __init__(self, vm: Dict, show_graph: bool = False):
        """
        Args:
            vm: View-model dict with fields used to render the card.
            show_graph: Whether to show the small graph button (owned items).
        """
        super().__init__(objectName="Card")
        self.vm = vm
        self.show_graph = show_graph

        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)
        self.setFixedSize(self.CARD_W, self.CARD_H)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._build()

    def _build(self):
        """Build the internal layout: image, title/subtitle, and bottom meta row."""
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 10)
        lay.setSpacing(6)

        # Image
        img = QLabel(objectName="CardImage")
        img.setFixedHeight(180)
        img.setAlignment(Qt.AlignCenter)
        url = self.vm.get("photo") or "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/download.jpg"
        load_into(img, url, placeholder=STYLE_DIR / "placeholder_card.png", size=QSize(340, 180))

        # Title + subtitle
        title = QLabel(self.vm.get("title") or self.vm.get("name") or "", objectName="CardTitle")
        title.setWordWrap(True)
        subtitle = QLabel(self.vm.get("subtitle", ""), objectName="CardSubtitle")
        subtitle.setWordWrap(True)

        # Bottom meta — region + pill + (graph button at the left of the pill)
        meta = QHBoxLayout(); meta.setSpacing(8)
        region = QLabel(self.vm.get("region") or "", objectName="Region")

        # graph button (owned only)
        graph_btn = None
        if self.show_graph:
            graph_btn = QToolButton()
            graph_btn.setIcon(_render_svg_to_icon(GRAPH_SVG, 22))
            graph_btn.setIconSize(QSize(22, 22))
            graph_btn.setCursor(Qt.PointingHandCursor)
            graph_btn.setToolTip("Open price chart")
            graph_btn.setAutoRaise(True)
            graph_btn.clicked.connect(lambda: self.graphClicked.emit(int(self.vm.get("id") or -1)))

        pill = QLabel(self.vm.get("pill", ""), objectName="Pill")
        if self.vm.get("pill"):
            pill.setProperty("ok", True)

        meta.addWidget(region, 0)
        if graph_btn:
            meta.addSpacing(4)
            meta.addWidget(graph_btn, 0)
        meta.addStretch(1)
        meta.addWidget(pill, 0)

        lay.addWidget(img)
        lay.addWidget(title)
        lay.addWidget(subtitle)
        lay.addLayout(meta)

    def mouseReleaseEvent(self, e):
        """Left-click release → emits clicked(int) carrying the card's id."""
        if e.button() == Qt.LeftButton:
            self.clicked.emit(int(self.vm.get("id") or -1))
        super().mouseReleaseEvent(e)


class AddNewCard(QFrame):
    """Card-sized '+' shortcut. Emits 'clicked()' when pressed."""
    clicked = Signal()
    CARD_W = CompactCard.CARD_W
    CARD_H = CompactCard.CARD_H

    def __init__(self):
        """Create a centered '+' card used at the end of the 'Owned items' section."""
        super().__init__(objectName="Card")
        self.setFixedSize(self.CARD_W, self.CARD_H)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 10)
        lay.setSpacing(6)

        # Icon
        icon = QLabel("+", alignment=Qt.AlignCenter)
        icon.setFixedHeight(180)
        icon.setObjectName("AddIcon")

        # Title + subtitle
        title = QLabel("Add new", objectName="CardTitle"); title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("Owned item shortcut", objectName="CardSubtitle"); subtitle.setAlignment(Qt.AlignCenter)

        lay.addWidget(icon)
        lay.addWidget(title)
        lay.addWidget(subtitle)
        lay.addStretch(1)

    def mouseReleaseEvent(self, e):
        """Left-click release → emits clicked(int) carrying the card's id."""
        if e.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(e)


# ------------------------------
# MinimalSection – responsive grid
# ------------------------------

class MinimalSection(QWidget):
    """
    Collapsible section with a responsive card grid.

    Signals:
        addNewRequested(): Request to create/add a new owned item.
        cardGraphRequested(int): Ask to open a price chart for a given decorId.

    Public API:
        set_content(cards: List[Dict], include_add_card: bool = False)
        set_count(n: int)
    """
    addNewRequested = Signal()
    cardGraphRequested = Signal(int)  # decorId

    def __init__(self, title: str, *, start_open: bool = True, show_graph: bool = False):
        """
        Args:
            title: Section title (will display as "Title · N").
            start_open: Whether the section body starts expanded.
            show_graph: Whether to display the small graph button in cards.
        """
        super().__init__()
        self._open = start_open
        self._cards_cache: List[Dict] = []
        self._last_cols: Optional[int] = None
        self._show_graph = show_graph

        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(8)

        # Header with toggle button and title+count
        header = QFrame()
        header.setFixedHeight(36)
        h = QHBoxLayout(header); h.setContentsMargins(12, 8, 12, 8); h.setSpacing(8)

        # Toggle button
        self.btn = QToolButton(text=("∨" if start_open else ">"))
        self.btn.setCursor(Qt.PointingHandCursor); self.btn.setAutoRaise(True)
        self.btn.setFixedSize(24, 24)
        self.btn.clicked.connect(self.toggle)

        # Title label
        self.title = QLabel(f"{title} · 0")
        h.addWidget(self.btn, 0); h.addWidget(self.title, 0); h.addStretch(1)

        # Body with grid layout
        self.body = QWidget()
        self.grid = QGridLayout(self.body)
        self.grid.setContentsMargins(0, 8, 0, 0)
        self.grid.setHorizontalSpacing(12)
        self.grid.setVerticalSpacing(12)
        self.grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        root.addWidget(header)
        root.addWidget(self.body)
        self.body.setVisible(self._open)

    def set_count(self, n: int):
        """Update the number displayed in the header (e.g., 'Decorations · 7')."""
        base = self.title.text().split("·")[0].strip()
        self.title.setText(f"{base} · {n}")

    def set_content(self, cards: List[Dict], *, include_add_card: bool = False):
        """
        Replace the section content with a new list of card view-models.
        """
        self._cards_cache = cards.copy() if cards else []
        if include_add_card:
            self._cards_cache.append({"__add_card__": True})
        self._rebuild_grid(force=True)

    def _calc_cols(self) -> int:
        """Compute the number of columns based on current width and card width."""
        parent_width = self.body.width() or self.width() or 800
        card_width = CompactCard.CARD_W
        return max(1, (parent_width - 40) // card_width)

    def _find_scroll_area(self) -> Optional[QAbstractScrollArea]:
        """Find the nearest parent QScrollArea (to preserve vertical scroll position)."""
        p = self.parent()
        while p is not None and not isinstance(p, QAbstractScrollArea):
            p = p.parent()
        return p

    def _clear_grid(self) -> None:
        """Remove all widgets from the grid and delete them."""
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None); w.deleteLater()

    def _rebuild_grid(self, force: bool = False):
        """
        Rebuild the grid when content/geometry changes.

        - Calculates columns; skips a rebuild if not needed.
        - Preserves vertical scroll position.
        - Populates with CompactCard/AddNewCard widgets.
        """
        cols = self._calc_cols()
        if not force and self._last_cols == cols:
            logical = len([c for c in self._cards_cache if not c.get("__add_card__")])
            self.set_count(logical)
            return
        self._last_cols = cols

        # Preserve vertical scroll position
        sa = self._find_scroll_area()
        vbar = sa.verticalScrollBar() if sa else None
        old_pos = vbar.value() if vbar else None

        self.body.setUpdatesEnabled(False)
        self._clear_grid()

        # Populate grid
        row = col = 0
        logical = 0
        for vm in self._cards_cache:
            if vm.get("__add_card__"):
                card = AddNewCard()
                card.clicked.connect(self.addNewRequested)
            else:
                card = CompactCard(vm, show_graph=self._show_graph)
                card.graphClicked.connect(self.cardGraphRequested)
                logical += 1

            self.grid.addWidget(card, row, col)
            col += 1
            if col >= cols:
                row += 1; col = 0

        self.set_count(logical)
        self.body.setUpdatesEnabled(True)
        if vbar is not None and old_pos is not None:
            QTimer.singleShot(0, lambda: vbar.setValue(old_pos))  # restore scroll

    def toggle(self):
        """Expand/collapse the section body, forcing a small rebuild after expansion."""
        self._open = not self._open
        self.btn.setText("∨" if self._open else ">")
        self.body.setVisible(self._open)
        if self._open and self._cards_cache:
            QTimer.singleShot(50, lambda: self._rebuild_grid(force=True))

    def resizeEvent(self, e):
        """On resize: schedule a delayed rebuild when open and content exists."""
        super().resizeEvent(e)
        if self._open and self._cards_cache:
            QTimer.singleShot(50, self._rebuild_grid)


# ------------------------------
# UserInfoView – whole page
# ------------------------------

class UserInfoView(QWidget):
    """
    Top-level view for the User Info page.

    Signals:
        refreshRequested
        addDecorClicked
        ownedGraphClicked(int)

    Presenter-facing API:
        set_user_header(name, phone, region, avatar_url=None)
        show_decor_cards(items)
        show_service_cards(items)
        show_hall_cards(items)
        show_owned_cards(items)
    """
    refreshRequested = Signal()
    addDecorClicked = Signal()
    ownedGraphClicked = Signal(int)  # decorId

    def __init__(self):
        """Set up the window, build the UI, and load the local stylesheet."""
        super().__init__()
        self.setWindowTitle("User Info")
        self.resize(1000, 700)
        self._build()
        self._load_qss()

    # API from presenter
    def set_user_header(self, name: str, phone: str, region: str, avatar_url: Optional[str] = None):
        """
        Set the header (name + 'phone · region') and optionally load an avatar image.

        Args:
            name: Display name.
            phone: User phone number (optional).
            region: User region (optional).
            avatar_url: Optional image URL to load into the avatar.
        """
        self.name.setText(name or "")
        parts = [p for p in [phone.strip() if phone else "", region.strip() if region else ""] if p]
        self.meta.setText(" · ".join(parts))
        if avatar_url:
            load_into(self.avatar, avatar_url, placeholder=STYLE_DIR / "avatar_placeholder.png", size=QSize(64, 64))

    def show_decor_cards(self, items: List[Dict]):   self.sec_decors.set_content(items)
    def show_service_cards(self, items: List[Dict]): self.sec_services.set_content(items)
    def show_hall_cards(self, items: List[Dict]):    self.sec_halls.set_content(items)
    def show_owned_cards(self, items: List[Dict]):   self.sec_owned.set_content(items, include_add_card=True)

    # Build
    def _build(self) -> None:
        """Create the full page layout: header, sections (recently used + owned), and wire signals."""
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget(); scroll.setWidget(content)

        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0); root.addWidget(scroll)
        lay = QVBoxLayout(content); lay.setContentsMargins(16, 16, 16, 16); lay.setSpacing(16)

        # Header
        top = QFrame(objectName="TopHeader")
        tl = QHBoxLayout(top); tl.setContentsMargins(16, 12, 16, 12); tl.setSpacing(16)

        # Avatar
        self.avatar = QLabel("👤", alignment=Qt.AlignCenter)
        self.avatar.setFixedSize(64, 64)
        self.avatar.setStyleSheet("border-radius:32px; background:#e5e7eb; font-size:28px;")

        # Name + meta
        info = QVBoxLayout(); info.setSpacing(2)
        self.name = QLabel("", objectName="HeaderName")
        self.meta = QLabel("", objectName="HeaderMeta")
        info.addWidget(self.name); info.addWidget(self.meta)

        tl.addWidget(self.avatar, 0); tl.addLayout(info, 1)
        lay.addWidget(top)

        # Sections order: Decorations used → Halls → Services → Owned items
        lay.addWidget(_section_label("Recently used"))
        self.sec_decors  = MinimalSection("Decorations", start_open=True, show_graph=False)
        self.sec_halls   = MinimalSection("Halls",        start_open=True, show_graph=False)
        self.sec_services= MinimalSection("Services",     start_open=True, show_graph=False)
        lay.addWidget(self.sec_decors)
        lay.addWidget(self.sec_halls)
        lay.addWidget(self.sec_services)

        lay.addWidget(_section_label("Owned by me"))
        self.sec_owned   = MinimalSection("Owned items",  start_open=True, show_graph=True)
        lay.addWidget(self.sec_owned)

        # expose signals outward
        self.sec_owned.cardGraphRequested.connect(self.ownedGraphClicked)
        self.sec_owned.addNewRequested.connect(self.addDecorClicked.emit)

        lay.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _load_qss(self):
        """Load local stylesheet (user_info_view.qss) if present."""
        if LOCAL_QSS.exists():
            self.setStyleSheet(LOCAL_QSS.read_text(encoding="utf-8"))

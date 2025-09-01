"""
View: Modern halls page using Cards layout.
Responsible only for UI rendering and user interactions.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
    QGridLayout, QLineEdit, QComboBox, QHBoxLayout
)
from PySide6.QtGui import QPixmap
import requests


class HallsView(QWidget):
    """
    UI class for displaying event halls as card-based layout.

    Provides:
        - Filters (region, type, search box)
        - Scrollable grid of hall cards
        - Signal when filters are changed
    """

    # Signal emitted whenever filters are changed
    filter_changed = Signal()

    def __init__(self):
        """
        Initialize the halls view.

        - Creates header, filter bar, and scrollable grid.
        - Loads style sheet from `halls_style.qss`.
        """
        super().__init__()
        self.setWindowTitle("Event Halls")
        self.resize(1100, 750)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        # ---- Header / Filters ----
        title = QLabel("Browse Halls")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 12px;")
        root.addWidget(title)

        self.filter_region = QComboBox()
        self.filter_region.addItem("All regions")
        self.filter_type = QComboBox()
        self.filter_type.addItem("All types")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by name...")

        filter_bar = QHBoxLayout()
        filter_bar.addWidget(self.filter_region)
        filter_bar.addWidget(self.filter_type)
        filter_bar.addWidget(self.search_box)
        root.addLayout(filter_bar)

        # Emit signal when filters are changed
        self.filter_region.currentIndexChanged.connect(lambda _: self.filter_changed.emit())
        self.filter_type.currentIndexChanged.connect(lambda _: self.filter_changed.emit())
        self.search_box.returnPressed.connect(lambda: self.filter_changed.emit())

        # ---- Scroll area for cards ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.cards_container = QWidget()
        self.grid = QGridLayout(self.cards_container)
        self.grid.setSpacing(15)
        scroll.setWidget(self.cards_container)
        root.addWidget(scroll)

        # Load QSS style
        import os
        style_path = os.path.join(os.path.dirname(__file__), "halls_style.qss")
        with open(style_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def populate_filters(self, halls):
        """
        Populate the region and type dropdown filters based on hall data.

        Args:
            halls (list[dict]): List of halls with keys "Region" and "HallType".
        """
        regions = sorted({h["Region"] for h in halls if h.get("Region")})
        types = sorted({h["HallType"] for h in halls if h.get("HallType")})

        self.filter_region.clear()
        self.filter_region.addItem("All regions")
        self.filter_region.addItems(regions)

        self.filter_type.clear()
        self.filter_type.addItem("All types")
        self.filter_type.addItems(types)

    def render_halls(self, halls):
        """
        Render hall cards into the grid.

        Args:
            halls (list[dict]): List of hall dictionaries, each representing one hall.
        """
        # Clear old cards
        for i in reversed(range(self.grid.count())):
            item = self.grid.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)

        # Add new cards (4 per row)
        for i, hall in enumerate(halls):
            card = self._make_card(hall)
            self.grid.addWidget(card, i // 4, i % 4)

    def _make_card(self, hall: dict):
        """
        Create a single hall card widget.

        Args:
            hall (dict): Hall data with keys such as
                         "HallName", "HallType", "Region", "Description", "PhotoUrl".

        Returns:
            QFrame: A styled card containing hall information.
        """
        card = QFrame()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(4, 4, 4, 4)

        # Image
        img_label = QLabel()
        img_label.setFixedHeight(100)
        img_label.setAlignment(Qt.AlignCenter)
        if hall.get("PhotoUrl"):
            try:
                print("Loading image from:", hall["PhotoUrl"])
                r = requests.get(hall["PhotoUrl"], timeout=5)
                pixmap = QPixmap()
                if pixmap.loadFromData(r.content):
                    img_label.setPixmap(
                        pixmap.scaled(160, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    )
                else:
                    img_label.setText("No image")
            except Exception as e:
                print("Image load failed:", e)
                img_label.setText("No image")
        layout.addWidget(img_label)

        # Name
        name = QLabel(hall.get("HallName", "Unknown"))
        name.setObjectName("HallName")
        layout.addWidget(name)

        # Type + Region
        meta = QLabel(f"{hall.get('HallType','')} · {hall.get('Region','')}")
        meta.setObjectName("Meta")
        layout.addWidget(meta)

        # Short description (first 2 lines)
        desc = hall.get("Description", "")
        desc_short = " ".join(desc.split()[:25]) + ("..." if len(desc.split()) > 25 else "")
        desc_label = QLabel(desc_short)
        desc_label.setWordWrap(True)
        desc_label.setObjectName("Description")
        desc_label.setFixedHeight(32)
        layout.addWidget(desc_label)

        return card

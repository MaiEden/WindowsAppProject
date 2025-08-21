"""
View: Modern halls page using Cards layout
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
    QGridLayout, QLineEdit, QComboBox, QHBoxLayout
)

from PySide6.QtGui import QPixmap
import requests


class HallsView(QWidget):
    # Signals -> Presenter
    filter_changed = Signal()

    def __init__(self):
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

        # ✅ תיקון – מנטרלים את הפרמטרים שהסיגנלים שולחים
        self.filter_region.currentIndexChanged.connect(lambda _: self.filter_changed.emit())
        self.filter_type.currentIndexChanged.connect(lambda _: self.filter_changed.emit())
        self.search_box.textChanged.connect(lambda _: self.filter_changed.emit())

        # ---- Scroll area for cards ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.cards_container = QWidget()
        self.grid = QGridLayout(self.cards_container)
        self.grid.setSpacing(15)
        scroll.setWidget(self.cards_container)
        root.addWidget(scroll)

        # load qss
        import os
        style_path = os.path.join(os.path.dirname(__file__), "halls_style.qss")
        with open(style_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def populate_filters(self, halls):
        """Fill region/type filters based on data."""
        regions = sorted({h["Region"] for h in halls if h.get("Region")})
        types = sorted({h["HallType"] for h in halls if h.get("HallType")})

        self.filter_region.clear()
        self.filter_region.addItem("All regions")
        self.filter_region.addItems(regions)

        self.filter_type.clear()
        self.filter_type.addItem("All types")
        self.filter_type.addItems(types)

    def render_halls(self, halls):
        """Render hall cards into grid."""
        # Clear old
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
        desc_label.setFixedHeight(32)  # בערך שתי שורות
        layout.addWidget(desc_label)

        return card

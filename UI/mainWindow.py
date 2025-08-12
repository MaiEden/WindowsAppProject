import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFrame, QLabel, QLineEdit, QComboBox, QDateEdit, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt, QDate

from hallslist.halls_view import HallsView
from atraction.attractions_view import AttractionsView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern App")
        self.resize(1100, 700)

        # ===== יצירת Layout ראשי =====
        main_layout = QHBoxLayout()
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # ===== Sidebar =====
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)

        btn_profile = QPushButton("📄 View Profile")
        btn_profile.setObjectName("sidebarButton")

        btn_event = QPushButton("➕ Add Event")
        btn_event.setObjectName("sidebarButton")

        btn_service = QPushButton("🛠 Add Service")
        btn_service.setObjectName("sidebarButton")

        btn_halls = QPushButton("🏛 Halls Event")
        btn_halls.setObjectName("sidebarButton")
        btn_halls.clicked.connect(lambda: self.replace_center_view(HallsView()))

        btn_attractions = QPushButton("🎉 Attractions List")
        btn_attractions.setObjectName("sidebarButton")
        btn_attractions.clicked.connect(lambda: self.replace_center_view(AttractionsView()))

        sidebar_layout.addWidget(btn_profile)
        sidebar_layout.addWidget(btn_event)
        sidebar_layout.addWidget(btn_service)
        sidebar_layout.addWidget(btn_halls)
        sidebar_layout.addWidget(btn_attractions)
        sidebar_layout.addStretch()

        # ===== Main Content =====
        self.main_content = QVBoxLayout()

        # --- Top Bar עם פילטרים ---
        self.topbar = QFrame()
        self.topbar.setObjectName("topbar")
        topbar_layout = QHBoxLayout(self.topbar)

        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Enter symbol")

        self.start_date = QDateEdit(QDate.currentDate())
        self.end_date = QDateEdit(QDate.currentDate())

        self.type_combo = QComboBox()
        self.type_combo.addItems(["All", "Buy", "Sell"])

        filter_btn = QPushButton("Apply Filters")
        filter_btn.setObjectName("filterButton")

        topbar_layout.addWidget(self.symbol_input)
        topbar_layout.addWidget(self.start_date)
        topbar_layout.addWidget(self.end_date)
        topbar_layout.addWidget(self.type_combo)
        topbar_layout.addWidget(filter_btn)
        topbar_layout.addStretch()

        # --- טבלה ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Symbol", "Type", "Price", "Total"])
        self.table.setRowCount(3)
        self.table.setItem(0, 0, QTableWidgetItem("2024-03-20"))
        self.table.setItem(0, 1, QTableWidgetItem("AAPL"))
        buy_item = QTableWidgetItem("Buy")
        buy_item.setBackground(Qt.green)
        self.table.setItem(0, 2, buy_item)
        self.table.setItem(0, 3, QTableWidgetItem("$150"))
        self.table.setItem(0, 4, QTableWidgetItem("$1500"))

        # ===== הוספה ל-Layout =====
        self.main_content.addWidget(self.topbar)
        self.main_content.addWidget(self.table)

        main_layout.addWidget(self.sidebar)
        main_layout.addLayout(self.main_content)

    def replace_center_view(self, new_view: QWidget):
        # החלפה פשוטה של ה-view המרכזי
        while self.main_content.count() > 1:
            item = self.main_content.takeAt(1)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.main_content.addWidget(new_view)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # טעינת ה-QSS
    with open("style.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

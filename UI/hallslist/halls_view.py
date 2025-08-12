from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
from PySide6.QtCore import Qt
from server.ServerAPI import *
from server.gateway.gateway import *

class HallsView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # כותרת
        title = QLabel("רשימת אולמות")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # טבלה
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)  # פסים
        self.table.setStyleSheet("border: none;")
        self.table.horizontalHeader().setStretchLastSection(True)  # עמודה אחרונה מותחת
        self.table.verticalHeader().setVisible(False)  # הסתרת מספרי שורות
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # בחירה של שורה שלמה

        layout.addWidget(self.table)

        # קריאת הנתונים מהשרת
        self.load_data()

    def load_data(self):
        try:
            halls = get_events()
            if not halls:
                self.table.clear()
                self.table.setRowCount(0)
                self.table.setColumnCount(1)
                self.table.setHorizontalHeaderLabels(["No data"])
                return

            # בניית כותרות
            keys = []
            for row in halls:
                for k in row.keys():
                    if k not in keys:
                        keys.append(k)

            self.table.clear()
            self.table.setColumnCount(len(keys))
            self.table.setHorizontalHeaderLabels(keys)

            # מילוי הנתונים
            self.table.setRowCount(len(halls))
            for r, hall in enumerate(halls):
                for c, key in enumerate(keys):
                    val = hall.get(key, "")
                    item = QTableWidgetItem("" if val is None else str(val))
                    self.table.setItem(r, c, item)

            self.table.resizeColumnsToContents()

        except Exception as e:
            print("Failed to load halls:", e)
            self.table.clear()
            self.table.setRowCount(0)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["Error"])

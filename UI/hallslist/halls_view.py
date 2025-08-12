# import httpx
# from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
# from PySide6.QtCore import Qt
# from server.gateway.gateway import *
#
# class HallsView(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         layout = QVBoxLayout()
#         self.setLayout(layout)
#
#         title = QLabel("רשימת אולמות")
#         title.setAlignment(Qt.AlignCenter)
#         title.setStyleSheet("font-size: 18px; font-weight: bold;")
#         layout.addWidget(title)
#
#         self.table = QTableWidget()
#         self.table.setColumnCount(3)
#         self.table.setHorizontalHeaderLabels(["Name", "Capacity", "Location"])
#         layout.addWidget(self.table)
#
#         # קריאת הנתונים מהשרת
#         self.load_data()
#
#     def load_data(self):
#         try:
#            halls = get_all_halls()
#             if response.status_code == 200:
#                 halls = response.json()
#                 self.table.setRowCount(len(halls))
#                 for row, hall in enumerate(halls):
#                     self.table.setItem(row, 0, QTableWidgetItem(hall["name"]))
#                     self.table.setItem(row, 1, QTableWidgetItem(str(hall["capacity"])))
#                     self.table.setItem(row, 2, QTableWidgetItem(hall["location"]))
#             else:
#                 print("Error:", response.status_code)
#         except Exception as e:
#             print("Failed to load halls:", e)

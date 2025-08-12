import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout
)

from hallslist.halls_view import HallsView
from atraction.attractions_view import AttractionsView  # ← ייבוא חדש


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.resize(800, 600)

        # ---- מרכז החלון ----
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout ראשי - Grid
        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)

        # ---- פאנל שמאל ----
        left_panel = QVBoxLayout()
        btn_view_profile = QPushButton("View Profile")
        btn_add_event = QPushButton("Add Event")
        btn_add_service = QPushButton("Add Service")

        btn_view_profile.clicked.connect(self.view_profile_clicked)
        btn_add_event.clicked.connect(self.add_event_clicked)
        btn_add_service.clicked.connect(self.add_service_clicked)

        left_panel.addWidget(btn_view_profile)
        left_panel.addWidget(btn_add_event)
        left_panel.addWidget(btn_add_service)
        left_panel.addStretch()

        # ---- פאנל עליון ----
        top_panel = QHBoxLayout()
        btn_photographers = QPushButton("Photographers List")
        btn_halls = QPushButton("Halls Event")
        btn_attractions = QPushButton("Attractions List")

        btn_photographers.clicked.connect(self.photographers_list_clicked)
        btn_halls.clicked.connect(self.halls_event_clicked)
        btn_attractions.clicked.connect(self.attractions_list_clicked)

        top_panel.addWidget(btn_photographers)
        top_panel.addWidget(btn_halls)
        top_panel.addWidget(btn_attractions)
        top_panel.addStretch()

        # ---- View מרכזי ריק ----
        self.center_view = QWidget()
        self.center_view.setStyleSheet("background-color: #f0f0f0;")

        # ---- הוספה ל־Grid ----
        self.layout.addLayout(top_panel, 0, 0, 1, 2)     # שורה עליונה
        self.layout.addLayout(left_panel, 1, 0)          # עמודה שמאל
        self.layout.addWidget(self.center_view, 1, 1)    # מרכז

        # הגדרות גודל
        self.layout.setColumnStretch(0, 0)
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(1, 1)

    # --- פונקציות לחיצת כפתורים ---
    def view_profile_clicked(self):
        print("כפתור View Profile לא ממומש")

    def add_event_clicked(self):
        print("כפתור Add Event לא ממומש")

    def add_service_clicked(self):
        print("כפתור Add Service לא ממומש")

    def photographers_list_clicked(self):
        print("כפתור Photographers List לא ממומש")

    def halls_event_clicked(self):
        print("מעבר לתצוגת Halls")
        self.replace_center_view(HallsView())

    def attractions_list_clicked(self):
        print("מעבר לתצוגת Attractions")
        self.replace_center_view(AttractionsView())

    def replace_center_view(self, new_view: QWidget):
        # מסיר את ה־View הישן מה־layout
        self.layout.removeWidget(self.center_view)
        self.center_view.deleteLater()
        # מוסיף את החדש
        self.center_view = new_view
        self.layout.addWidget(self.center_view, 1, 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

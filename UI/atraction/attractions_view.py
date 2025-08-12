from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class AttractionsView(QWidget):
    def __init__(self):
        super().__init__()

        # קביעת צבע רקע על כל ה־view
        self.setStyleSheet("background-color: #ff5733;")  # כתום-אדום

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # בלי רווחים פנימיים

        label = QLabel("רשימת אטרקציות - דמו")
        label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        label.setAlignment(Qt.AlignCenter)  # טקסט באמצע
        layout.addWidget(label)

        self.setLayout(layout)

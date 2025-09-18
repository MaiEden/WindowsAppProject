from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QComboBox, QGraphicsDropShadowEffect
)

BASE_DIR = Path(__file__).resolve().parents[1]

def apply_drop_shadow(widget, radius=18, x_offset=0, y_offset=6):
    """Apply a subtle, modern drop shadow to a widget."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(radius)
    shadow.setOffset(x_offset, y_offset)
    widget.setGraphicsEffect(shadow)

class SignUpView(QWidget):
    # View -> Presenter signals
    submit_clicked = Signal()
    cancel_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create an Account")

        # size when window opens and minimum size
        self.setMinimumSize(520, 640)

        self._build_ui()
        self._wire_events()
        self._center_on_screen()

    # ---------- UI ----------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 20, 16, 20)

        # Card container
        self.card = QFrame(objectName="Card")
        self.card.setFixedWidth(460)  # default card width
        apply_drop_shadow(self.card)

        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(26, 26, 26, 26)
        layout.setSpacing(18)

        # ----- Header: title+subtitle (left) and icon (right) -----
        header = QHBoxLayout()
        header.setSpacing(12)
        header.setContentsMargins(0, 0, 0, 0)

        # Left column: Title + Subtitle
        titles_col = QVBoxLayout()
        titles_col.setSpacing(4)

        # Titles
        self.title = QLabel("Sign Up", objectName="Title")
        self.subtitle = QLabel("Please fill in all fields", objectName="Subtitle")
        titles_col.addWidget(self.title)
        titles_col.addWidget(self.subtitle)

        # Right: icon
        self.icon_label = QLabel()
        icon_size = 120

        # Load icon from file
        icon_path = BASE_DIR / "style&icons" / "EventPlannerLogo.png"
        pix = QPixmap(icon_path)
        if not pix.isNull():
            self.icon_label.setPixmap(
                pix.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        self.icon_label.setFixedSize(icon_size, icon_size)
        self.icon_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        header.addLayout(titles_col, 1)  # left side gets stretch
        header.addWidget(self.icon_label, 0, Qt.AlignRight | Qt.AlignTop)

        # ----- Inputs -----
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Phone")
        self.region = QComboBox()
        self.region.addItems(["Center", "North", "South", "East", "West"])

        # ----- Message area (reserve space so layout doesn't jump) -----
        self.message = QLabel("", objectName="Message")
        self.message.setWordWrap(True)
        self.message.setProperty("status", "")
        self.message.setMinimumHeight(44)
        self.message.setVisible(True)      # visible to reserve space

        # ----- Buttons -----
        self.submit_btn = QPushButton("Create Account", objectName="Primary")
        self.cancel_btn = QPushButton("Cancel", objectName="Link")

        layout.addLayout(header)
        layout.addSpacing(10)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.phone)
        layout.addWidget(self.region)
        layout.addWidget(self.message)
        layout.addSpacing(10)
        layout.addWidget(self.submit_btn)
        layout.addWidget(self.cancel_btn)

        # Center the card in the window
        wrap = QVBoxLayout()
        wrap.addStretch(1)
        wrap.addWidget(self.card, alignment=Qt.AlignHCenter)
        wrap.addStretch(1)
        root.addLayout(wrap)

    def _wire_events(self):
        self.submit_btn.clicked.connect(self.submit_clicked.emit)
        self.cancel_btn.clicked.connect(self.cancel_clicked.emit)

    def _center_on_screen(self):
        frame = self.frameGeometry()
        screen_center = self.screen().availableGeometry().center() if self.screen() else None
        if screen_center:
            frame.moveCenter(screen_center)
            self.move(frame.topLeft())

    # ---------- View API ----------
    def get_phone(self) -> str:
        return self.phone.text()

    def get_username(self) -> str:
        return self.username.text()

    def get_password_hash(self) -> str:
        # demo only; should hash in real apps
        return self.password.text()

    def get_region(self) -> str:
        return self.region.currentText()

    def show_message(self, text: str, status: str):
        """Show inline success/error message styled via QSS."""
        self.message.setText(text)
        self.message.setProperty("status", status)  # 'ok' / 'error'
        # Short style refresh so [status="..."] selectors apply immediately
        self.message.setStyle(self.message.style())
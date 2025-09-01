"""
View: UI only (no business logic)
- Presenter connects handlers to these UI events
"""
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QHBoxLayout
)

BASE_DIR = Path(__file__).resolve().parents[1]   # .../UI

def apply_drop_shadow(widget, radius=18, x_offset=0, y_offset=6):
    """Set Subtle, modern shadow on a widget."""
    from PySide6.QtWidgets import QGraphicsDropShadowEffect
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(radius)
    shadow.setOffset(x_offset, y_offset)
    widget.setGraphicsEffect(shadow)

class LoginView(QWidget):
    """Login screen. Styling is in styles.qss."""

    # View -> Presenter communication
    # Signals the view sends to the presenter
    sign_in_clicked = Signal()
    demo_clicked = Signal()
    sign_up_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login Screen")

        # size when window opens and minimum size
        self.resize(520, 560)
        self.setMinimumSize(340, 480)

        self._build_ui()
        self._wire_events()
        self._center_on_screen()

    # ---------- UI ----------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)

        self.card = QFrame(objectName="Card")
        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(26, 26, 26, 26)
        layout.setSpacing(18)

        apply_drop_shadow(self.card)

        # ----- Header: title+subtitle (left) and icon (right) -----
        header = QHBoxLayout()
        header.setSpacing(12)
        header.setContentsMargins(0, 0, 0, 0)

        # Left column: Title + Subtitle
        titles_col = QVBoxLayout()
        titles_col.setSpacing(4)
        # Title and subtitle
        self.title = QLabel("Welcome back 👋", objectName="Title")
        self.subtitle = QLabel("Please sign in to continue", objectName="Subtitle")
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

        # Input fields
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setClearButtonEnabled(True)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setClearButtonEnabled(True)

        # Status message
        self.message = QLabel("", objectName="Message")
        self.message.setProperty("status", "")
        self.message.setVisible(False)

        self.sign_in_btn = QPushButton("Sign in", objectName="Primary")
        # Change the mouse cursor to a pointing hand when hovering over the button
        self.sign_in_btn.setCursor(Qt.PointingHandCursor)
        self.sign_in_btn.setMinimumHeight(44)

        self.sign_up_btn = QPushButton("Create account", objectName="Link")
        self.sign_up_btn.setCursor(Qt.PointingHandCursor)

        self.use_demo_btn = QPushButton("Use demo credentials", objectName="Link")
        # Change the mouse cursor to a pointing hand when hovering over the button
        self.use_demo_btn.setCursor(Qt.PointingHandCursor)

        layout.addLayout(header)
        layout.addSpacing(12)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.message)
        layout.addSpacing(6)
        layout.addWidget(self.sign_in_btn)
        layout.addWidget(self.sign_up_btn, alignment=Qt.AlignHCenter)
        layout.addWidget(self.use_demo_btn, alignment=Qt.AlignHCenter)

        layout.addSpacing(4)

        box = QVBoxLayout()
        box.addStretch(1)
        box.addWidget(self.card, alignment=Qt.AlignHCenter)
        box.addStretch(1)

        root.addLayout(box)
        self.username.setFocus()

    def _wire_events(self):
        # Buttons
        self.sign_in_btn.clicked.connect(self.sign_in_clicked.emit)
        self.sign_up_btn.clicked.connect(self.sign_up_clicked.emit)
        self.use_demo_btn.clicked.connect(self.demo_clicked.emit)
        # Enter to submit
        self.username.returnPressed.connect(self.sign_in_clicked.emit)
        self.password.returnPressed.connect(self.sign_in_clicked.emit)
        # Disable sign in when fields empty
        self.username.textChanged.connect(self._update_button_state)
        self.password.textChanged.connect(self._update_button_state)
        self._update_button_state()

    def _center_on_screen(self):
        frame = self.frameGeometry()
        screen = self.screen().availableGeometry().center() if self.screen() else None
        if screen:
            frame.moveCenter(screen)
            self.move(frame.topLeft())

    # ---------- View API used by Presenter ----------
    def get_username(self) -> str:
        return self.username.text()

    def get_password(self) -> str:
        return self.password.text()

    def set_demo_credentials(self, u: str, p: str):
        self.username.setText(u)
        self.password.setText(p)
        self._update_button_state()

    def show_message(self, text: str, status: str):
        """Show inline message with 'ok' or 'error' status (affects QSS)."""
        self.message.setText(text)
        self.message.setProperty("status", status) # Set status for styling
        self.message.setVisible(True)
        # Refresh style to apply [status="..."] selectors
        self.message.setStyle(self.message.style())

    # ---------- private helpers ----------
    def _update_button_state(self):
        # Enable sign in button only if both fields are filled
        can_submit = bool(self.get_username().strip()) and bool(self.get_password())
        self.sign_in_btn.setDisabled(not can_submit)
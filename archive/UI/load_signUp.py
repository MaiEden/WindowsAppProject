"""
Entry point to open the SignUp screen (MVP).
"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from UI.signup.signup_model import SignUpModel
from UI.signup.signup_view import SignUpView
from UI.signup.signup_presenter import SignUpPresenter

def load_stylesheet(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Failed to load stylesheet: {e}")
        return ""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    # View + Model + Presenter wiring
    view = SignUpView()
    model = SignUpModel()  # standalone demo store
    presenter = SignUpPresenter(model, view)  # noqa: F841

    # Load QSS
    qss = load_stylesheet("../../UI/style&icons/UIstyle.qss")
    if qss:
        app.setStyleSheet(qss)

    view.show()
    sys.exit(app.exec())
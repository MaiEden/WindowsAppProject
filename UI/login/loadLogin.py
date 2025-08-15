# -*- coding: utf-8 -*-
"""
App entry point (MVP wiring)
- Loads QSS from external file
- Wires Model, View, Presenter
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from login_model import AuthModel
from login_view import LoginView
from login_presenter import LoginPresenter


def load_stylesheet(path: str) -> str:
    """Read QSS stylesheet from a file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Failed to load stylesheet: {e}")
        return ""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))  # friendly default font

    # View
    view = LoginView()
    view.show()

    # Model
    model = AuthModel()

    # Presenter
    presenter = LoginPresenter(model, view)

    # Load external stylesheet
    qss = load_stylesheet("../style&icons/UIstyle.qss")
    if qss:
        app.setStyleSheet(qss)

    sys.exit(app.exec())

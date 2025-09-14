# ============================
# File: main.py
# ============================
# Entry point – Single window. Login -> (on success) MainShell.
# Loads global QSS; keeps presenters alive to preserve logic/signals.

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Make sure packages import cleanly when running from project root
BASE = Path(__file__).resolve().parent
for p in [
    BASE / "login",
    BASE / "signup",
    BASE / "halls_list",
    BASE / "service_list",
    BASE / "decorator_list",
    BASE / "style&icons",
]:
    sys.path.append(str(p))

from main_shell import AppWindow, MainShell

# ---- Auth views/presenters/models ----
from login.login_view import LoginView
from login.login_presenter import LoginPresenter
from login.login_model import AuthModel

from signup.signup_view import SignUpView
from signup.signup_presenter import SignUpPresenter
from signup.signup_model import SignUpModel


def load_global_qss(app):
    """Load app-wide styles."""
    qss_paths = [
        BASE / "style&icons" / "UIstyle.qss",
        BASE / "style&icons" / "list_style.qss",
    ]
    css = ""
    for p in qss_paths:
        if p.exists():
            css += p.read_text(encoding="utf-8") + "\n"
    app.setStyleSheet(css)


def build_auth_flow(app_window: AppWindow):
    """Create Login & SignUp pages and wire navigation + success route."""
    # Views
    login_view = LoginView()
    signup_view = SignUpView()

    # Presenters (QObject!) — must keep references to avoid GC
    login_presenter = LoginPresenter(AuthModel(), login_view)
    signup_presenter = SignUpPresenter(SignUpModel(), signup_view)

    # Keep them alive on the window
    app_window.keep(login_presenter, signup_presenter, login_view, signup_view)

    # Add pages
    app_window.add_page("login", login_view)
    app_window.add_page("signup", signup_view)

    # View-to-view navigation
    login_view.sign_up_clicked.connect(lambda: app_window.goto("signup"))
    signup_view.cancel_clicked.connect(lambda: app_window.goto("login"))

    # On successful auth -> build/open shell inside same window
    def open_shell(username: str):
        shell = MainShell(username=username)
        app_window.set_shell(shell)
        app_window.goto("shell")

    login_presenter.auth_ok.connect(open_shell)
    signup_presenter.auth_ok.connect(open_shell)


def main():
    app = QApplication(sys.argv)
    load_global_qss(app)

    win = AppWindow()
    build_auth_flow(win)

    win.goto("login")
    win.showMaximized()  # open full-screen by default (maximized)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

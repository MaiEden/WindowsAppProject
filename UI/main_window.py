# main_window.py
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QIcon

from UI.mainWindow import MainWindow
from login.login_model import AuthModel
from login.login_view import LoginView
from login.login_presenter import LoginPresenter

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

    # Load stylesheet
    qss = load_stylesheet("style&icons/UIstyle.qss")
    if qss:
        app.setStyleSheet(qss)
    # Set application icon
    app.setWindowIcon(QIcon("style&icons/no_words_icon.png"))

    # --- Login MVP ---
    login_view = LoginView()
    login_model = AuthModel()
    login_presenter = LoginPresenter(login_model, login_view)

    # --- SignUp MVP ---
    signup_view = SignUpView()
    signup_model = SignUpModel()
    signup_presenter = SignUpPresenter(signup_model, signup_view)

    # Functions to switch views
    # Switch to SignUp view
    def open_signup():
        login_view.hide()
        signup_view.show()
        signup_view.raise_()
        signup_view.activateWindow()

    # Switch to Login view
    def back_to_login():
        signup_view.hide()
        login_view.show()
        login_view.raise_()
        login_view.activateWindow()

    # Move to MainWindow after successful login/signup
    def open_main(_username: str = ""):
        # close the current views
        if login_view.isVisible():
            login_view.hide()
        if signup_view.isVisible():
            signup_view.hide()
        # open the main window
        main_win = MainWindow()
        main_win.show()
        main_win.raise_()
        main_win.activateWindow()

    # Login -> SignUp
    login_view.sign_up_clicked.connect(open_signup)
    # SignUp -> back to Login
    signup_view.cancel_clicked.connect(back_to_login)

    # Login/SignUp -> MainWindow
    login_presenter.auth_ok.connect(open_main)
    signup_presenter.auth_ok.connect(open_main)

    # Start at login
    login_view.show()
    sys.exit(app.exec())
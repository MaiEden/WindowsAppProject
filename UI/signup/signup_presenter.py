"""
Presenter for Sign Up screen
"""
from .signup_model import SignUpModel
from .signup_view import SignUpView
from PySide6.QtCore import Signal, QObject


class SignUpPresenter(QObject):
    # Signal to open main window after successful sign up
    auth_ok = Signal(str)

    def __init__(self, model: SignUpModel, view: SignUpView):
        super().__init__()
        self.model = model
        self.view = view
        self._connect_signals()

    def _connect_signals(self):
        self.view.submit_clicked.connect(self.on_submit)

    def on_submit(self):
        phone = self.view.get_phone()
        username = self.view.get_username()
        pwd_hash = self.view.get_password_hash()
        region = self.view.get_region()

        ok, msg = self.model.register(phone, username, pwd_hash, region)
        print("Sign up OK" if ok else "Sign up failed")  # console feedback
        self.view.show_message(msg, status="ok" if ok else "error")
        if ok:
            self.auth_ok.emit(username)
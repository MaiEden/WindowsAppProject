"""
Presenter: mediates between View and Model
- Pulls data from View, calls Model, updates View
- Keeps UI logic out of the Model and heavy logic out of the View
"""
from .login_model import AuthModel
from .login_view import LoginView
from PySide6.QtCore import Signal, QObject

DEMO_PASSWORD = "admin1234"

DEMO_USER = "admin"


class LoginPresenter(QObject):
    # Signal for moving to the main app after successful login
    auth_ok = Signal(str)

    def __init__(self, model: AuthModel, view: LoginView):
        super().__init__()
        self.model = model
        self.view = view
        self._connect_signals()

    def _connect_signals(self):
        self.view.sign_in_clicked.connect(self.on_sign_in)
        self.view.demo_clicked.connect(self.on_use_demo)

    # ---- Handlers ----
    def on_sign_in(self):
        ok = self.model.verify(self.view.get_username(),self.view.get_password())
        self.print_result(ok)
        if ok:
            self.view.show_message("Signed in successfully.", status="ok")
            self.auth_ok.emit(self.view.get_username())
        else:
            self.view.show_message("Invalid username or password.", status="error")

    def on_use_demo(self):
        self.view.set_demo_credentials(DEMO_USER, DEMO_PASSWORD)

    def print_result(self, ok: bool):
        """Print to console as requested."""
        print("Correct credentials" if ok else "Incorrect credentials")
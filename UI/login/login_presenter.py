"""
Presenter: mediates between View and Model
- Pulls data from View, calls Model, updates View
- Keeps UI logic out of the Model and heavy logic out of the View
"""

from login_model import AuthModel
from login_view import LoginView

class LoginPresenter:

    def __init__(self, model: AuthModel, view: LoginView):
        self.model = model
        self.view = view
        self._connect_signals()

    def _connect_signals(self):
        self.view.sign_in_clicked.connect(self.on_sign_in)
        self.view.demo_clicked.connect(self.on_use_demo)
        # self.view.sign_up_clicked.connect(self.on_sign_up)

    # ---- Handlers ----
    def on_sign_in(self):
        ok = self.model.verify(self.view.get_username(),self.view.get_password())
        self.print_result(ok)
        if ok:
            self.view.show_message("Signed in successfully.", status="ok")
        else:
            self.view.show_message("Invalid username or password.", status="error")

    def on_use_demo(self):
        self.view.set_demo_credentials("admin", "secret123")

    # def on_sign_up(self):




    def print_result(self, ok: bool):
        """Print to console as requested."""
        print("Correct credentials" if ok else "Incorrect credentials")
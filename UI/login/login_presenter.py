# UI/login/login_presenter.py
"""
Presenter: mediates between View and Model
"""

from typing import Optional
from PySide6.QtCore import QObject, Signal, Slot, QThread, Qt
from UI.login.login_model import AuthModel
from UI.login.login_view import LoginView
from UI.ui_helpers import start_button_loading, stop_button_loading

DEMO_PASSWORD = "hash:noa"
DEMO_USER = "Noa Hadad"

class _LoginWorker(QObject):
    """Worker that runs in a QThread and performs the sign-in verification."""
    finished = Signal(bool)  # ok

    def __init__(self, model: AuthModel, username: str, password: str):
        super().__init__()
        self._model = model
        self._username = username
        self._password = password

    @Slot()
    def run(self):
        """Execute the blocking verification logic off the GUI thread."""
        try:
            ok = self._model.verify(self._username, self._password)
        except Exception:
            ok = False
        self.finished.emit(ok)

class LoginPresenter(QObject):
    # Signal for moving to the main app after successful login
    auth_ok = Signal(str)

    def __init__(self, model: AuthModel, view: LoginView):
        super().__init__()
        self.model = model
        self.view = view
        self._thread: Optional[QThread] = None
        self._worker: Optional[_LoginWorker] = None
        self._pending_username: str = ""
        self._connect_signals()

    def _connect_signals(self):
        """Wire view signals to presenter slots."""
        self.view.sign_in_clicked.connect(self.on_sign_in)
        self.view.demo_clicked.connect(self.on_use_demo)

    @Slot()
    def on_sign_in(self):
        """Start async sign-in flow: show loading, spawn thread, run worker."""
        # Loading state on the button (spinner + disable)
        start_button_loading(self.view.sign_in_btn, "loading...")

        username = self.view.get_username()
        password = self.view.get_password()
        self._pending_username = username

        # If a previous thread is still around, attempt to stop it gracefully
        if self._thread is not None:
            try:
                self._thread.quit()
                self._thread.wait(100)
            except Exception:
                pass
            self._thread = None
            self._worker = None

        # Create thread and worker
        th = QThread(self)
        th.setObjectName("LoginWorkerThread")
        worker = _LoginWorker(self.model, username, password)
        worker.moveToThread(th)

        # When the thread starts -> run the work
        th.started.connect(worker.run)

        # When the work finishes:
        # 1) Update the UI on the GUI thread (QueuedConnection)
        worker.finished.connect(self._on_finished, Qt.QueuedConnection)
        # 2) Quit the thread
        worker.finished.connect(th.quit)
        # 3) Clean up resources when the thread actually finishes
        th.finished.connect(worker.deleteLater)
        th.finished.connect(th.deleteLater)

        # Hold references to avoid premature GC
        self._thread = th
        self._worker = worker

        # Go
        th.start()

    @Slot(bool)
    def _on_finished(self, ok: bool):
        """Runs on the GUI thread (connected via QueuedConnection)."""
        stop_button_loading(self.view.sign_in_btn)
        self.print_result(ok)

        if ok:
            self.view.show_message("Signed in successfully, loading app data...", status="ok")
            # Emit the username captured at the start of the operation
            self.auth_ok.emit(self._pending_username)
        else:
            self.view.show_message("Invalid username or password.", status="error")

        # Release references; actual objects are deleted via connections in on_sign_in
        self._pending_username = ""
        self._worker = None
        self._thread = None

    @Slot()
    def on_use_demo(self):
        """Fill the login form with demo credentials."""
        self.view.set_demo_credentials(DEMO_USER, DEMO_PASSWORD)

    def print_result(self, ok: bool):
        """Print the verification result to the console."""
        print("Correct credentials" if ok else "Incorrect credentials")
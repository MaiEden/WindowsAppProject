"""
Presenter for Sign Up screen
"""
from typing import Optional
from PySide6.QtCore import QObject, Signal, Slot, QThread
from UI.signup.signup_model import SignUpModel
from UI.signup.signup_view import SignUpView
from UI.ui_helpers import start_button_loading, stop_button_loading

class _SignUpWorker(QObject):
    """Worker that runs inside a QThread and performs the registration call."""
    finished = Signal(bool, str)  # ok, message

    def __init__(self, model: SignUpModel, phone: str, username: str, pwd_hash: str, region: str):
        super().__init__()
        self._model = model
        self._phone = phone
        self._username = username
        self._pwd_hash = pwd_hash
        self._region = region

    @Slot()
    def run(self):
        """Execute the blocking sign-up logic off the GUI thread and emit the result."""
        try:
            ok, msg = self._model.register(self._phone, self._username, self._pwd_hash, self._region)
        except Exception as e:
            ok, msg = False, f"Sign up failed: {e}"
        self.finished.emit(ok, msg)


class SignUpPresenter(QObject):
    # Signal to open main window after successful sign up
    auth_ok = Signal(str)

    def __init__(self, model: SignUpModel, view: SignUpView):
        super().__init__()
        self.model = model
        self.view = view
        self._thread: Optional[QThread] = None
        self._worker: Optional[_SignUpWorker] = None
        self._connect_signals()

    def _connect_signals(self):
        """Connect view events to presenter handlers."""
        self.view.submit_clicked.connect(self.on_submit)

    @Slot()
    def on_submit(self):
        """Collect form data, show loading, start worker in a background thread."""
        phone = self.view.get_phone()
        username = self.view.get_username()
        pwd_hash = self.view.get_password_hash()
        region = self.view.get_region()

        # Put the submit button in a loading state (spinner inside the button + disable)
        start_button_loading(self.view.submit_btn, "creating an account...")

        # Create thread and worker
        self._thread = QThread(self)
        self._worker = _SignUpWorker(self.model, phone, username, pwd_hash, region)
        self._worker.moveToThread(self._thread)

        # When the thread starts → run the worker job
        self._thread.started.connect(self._worker.run)

        # When finished → handle result and clean up resources
        def _on_finished(ok: bool, msg: str):
            stop_button_loading(self.view.submit_btn)
            print("Sign up OK" if ok else "Sign up failed")
            self.view.show_message(msg, status="ok" if ok else "error")
            if ok:
                self.auth_ok.emit(username)

            # Tidy cleanup
            if self._thread is not None:
                self._thread.quit()
                self._thread.wait()
                self._thread.deleteLater()
            if self._worker is not None:
                self._worker.deleteLater()
            self._thread = None
            self._worker = None

        self._worker.finished.connect(_on_finished)

        # Start the thread
        self._thread.start()
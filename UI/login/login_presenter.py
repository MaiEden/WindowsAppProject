# UI/login/login_presenter.py
"""
Presenter: mediates between View and Model
- Pulls data from View, calls Model, updates View
- Keeps UI logic out of the Model and heavy logic out of the View
גרסה תואמת Python 3.8/PySide6: QThread + Worker ללא QtConcurrent/QFutureWatcher
"""

from typing import Optional

from PySide6.QtCore import QObject, Signal, Slot, QThread, Qt

from UI.login.login_model import AuthModel
from UI.login.login_view import LoginView
from UI.ui_helpers import start_button_loading, stop_button_loading

DEMO_PASSWORD = "hash:noa"
DEMO_USER = "Noa hadad"


class _LoginWorker(QObject):
    """Worker שרץ ב־QThread ומבצע את בדיקת ההתחברות."""
    finished = Signal(bool)  # ok

    def __init__(self, model: AuthModel, username: str, password: str):
        super().__init__()
        self._model = model
        self._username = username
        self._password = password

    @Slot()
    def run(self):
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
        self.view.sign_in_clicked.connect(self.on_sign_in)
        self.view.demo_clicked.connect(self.on_use_demo)

    @Slot()
    def on_sign_in(self):
        # מצב טעינה על הכפתור (עם ספינר + disable)
        start_button_loading(self.view.sign_in_btn, "loading...")

        username = self.view.get_username()
        password = self.view.get_password()
        self._pending_username = username

        # אם יש thread קודם בתהליך — נסיים אותו בעדינות
        if self._thread is not None:
            try:
                self._thread.quit()
                self._thread.wait(100)
            except Exception:
                pass
            self._thread = None
            self._worker = None

        # יצירת thread ו־worker
        th = QThread(self)
        th.setObjectName("LoginWorkerThread")
        worker = _LoginWorker(self.model, username, password)
        worker.moveToThread(th)

        # כשתחיל ה-thread → להריץ את העבודה
        th.started.connect(worker.run)

        # כשנגמרת העבודה:
        # 1) לעדכן UI ב-GUI thread (QueuedConnection)
        worker.finished.connect(self._on_finished, Qt.QueuedConnection)
        # 2) לסגור את ה-thread
        worker.finished.connect(th.quit)
        # 3) לנקות משאבים כשה-thread באמת נסגר
        th.finished.connect(worker.deleteLater)
        th.finished.connect(th.deleteLater)

        # שמירת רפרנסים כדי למנוע GC
        self._thread = th
        self._worker = worker

        # הפעלה
        th.start()

    @Slot(bool)
    def _on_finished(self, ok: bool):
        """תמיד רץ ב-GUI thread (כי חיברנו כ-QueuedConnection)."""
        stop_button_loading(self.view.sign_in_btn)
        self.print_result(ok)

        if ok:
            self.view.show_message("Signed in successfully, loading app data...", status="ok")
            # שליחת שם המשתמש שנטען בתחילת הפעולה
            self.auth_ok.emit(self._pending_username)
        else:
            self.view.show_message("Invalid username or password.", status="error")

        # שחרור רפרנסים; האובייקטים עצמם יימחקו דרך החיבורים ב-on_sign_in
        self._pending_username = ""
        self._worker = None
        self._thread = None

    @Slot()
    def on_use_demo(self):
        self.view.set_demo_credentials(DEMO_USER, DEMO_PASSWORD)

    def print_result(self, ok: bool):
        """Print to console as requested."""
        print("Correct credentials" if ok else "Incorrect credentials")

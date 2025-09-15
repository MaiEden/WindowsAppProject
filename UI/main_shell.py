# ============================
# File: main_shell.py  (Halls + Services + Decors with Details)
# ============================
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QToolButton, QStackedWidget, QSizePolicy, QFrame
)

APP_BASE = Path(__file__).resolve().parent
PROJECT_ROOT = APP_BASE.parent  # WindowsAppProject/

for p in [
    APP_BASE / "halls_list",
    APP_BASE / "service_list",
    APP_BASE / "decorator_list",
    APP_BASE / "style&icons",
    APP_BASE / "agent",
    APP_BASE / "user_info",
]:
    sys.path.append(str(p))

# ---------- Lists ----------
from halls_list.hall_list_view import HallListView
from halls_list.hall_list_model import HallListModel
from halls_list.hall_list_presenter import HallListPresenter

from service_list.service_list_view import ServiceListView
from service_list.service_list_model import ServiceListModel
from service_list.service_list_presenter import ServiceListPresenter

from decorator_list.decor_list_view import DecorListView
from decorator_list.decor_list_model import DecorListModel
from decorator_list.decor_list_presenter import DecorListPresenter

# ---------- Details (NEW) ----------
# Halls
from halls_list.hall_details_view import HallDetailsView
from halls_list.hall_details_model import HallDetailsModel
from halls_list.hall_details_presenter import HallDetailsPresenter
# Services
from service_list.service_details_view import ServiceDetailsView
from service_list.service_details_model import ServiceDetailsModel
from service_list.service_details_presenter import ServiceDetailsPresenter
# Decors
from decorator_list.decor_details_view import DecorDetailsView
from decorator_list.decor_details_model import DecorDetailsModel
from decorator_list.decor_details_presenter import DecorDetailsPresenter

# --- Chat MVP factory ---
from agent.chat_factory import build_chat_module

# user info
from user_info.user_info_view import UserInfoView
from user_info.user_info_model import UserInfoModel
from user_info.user_info_presenter import UserInfoPresenter

# ---------- Helpers ----------
def circle_icon_button(char: str, tooltip: str) -> QToolButton:
    """Round, ghost-style icon button using a unicode glyph (e.g. ◀ ▶)."""
    b = QToolButton()
    b.setText(char)
    b.setToolTip(tooltip)
    b.setCursor(Qt.PointingHandCursor)
    b.setAutoRaise(True)
    b.setFixedSize(40, 40)
    b.setStyleSheet("""
        QToolButton {
            font-size: 18px; font-weight: 700;
            border-radius: 20px;
            border: 1px solid rgba(0,0,0,0.08);
            background: rgba(255,255,255,0.6);
        }
        QToolButton:hover   { background: rgba(66,133,244,0.10); }
        QToolButton:pressed { background: rgba(66,133,244,0.18); }
        QToolButton:disabled{ opacity: .35; }
    """)
    return b


# ---------- AppWindow ----------
class AppWindow(QMainWindow):
    """Top-level window that owns a stack of pages (login / signup / shell)."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Planner – App")
        self.setMinimumSize(960, 640)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)
        self._pages: dict[str, QWidget] = {}
        self._keepers: list[object] = []   # keep refs (presenters/views) to avoid GC
        self._shell: MainShell | None = None

    def keep(self, *objs): self._keepers.extend(objs)

    def add_page(self, name: str, widget: QWidget):
        self._pages[name] = widget
        self._stack.addWidget(widget)

    def set_shell(self, shell: "MainShell"):
        if getattr(self, "_shell", None):
            self._stack.removeWidget(self._shell)
            self._shell.deleteLater()
        self._shell = shell
        self.add_page("shell", shell)
        self.keep(shell)

    def goto(self, name: str):
        w = self._pages.get(name)
        if w is not None:
            self._stack.setCurrentWidget(w)


# ---------- MainShell ----------
class MainShell(QWidget):
    """Main application surface (after successful auth)."""
    def __init__(self, username: str):
        super().__init__()
        self.username = username

        # history for center stack
        self._history: list[str] = []
        self._hist_index: int = -1

        # name -> widget (center pages)
        self._center_pages: dict[str, QWidget] = {}

        # prevent GC of presenters
        self._presenters: list[object] = []

        self._build_ui()
        self._wire()
        self._load_microfrontends()
        self.navigate("decors")  # default landing

    # ----- UI -----
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # Top bar
        top = QHBoxLayout(); top.setSpacing(10)

        logo = QLabel()
        pm = QPixmap(str(APP_BASE / "style&icons" / "EventPlannerLogo.png"))
        if not pm.isNull():
            logo.setPixmap(pm.scaledToHeight(56, Qt.SmoothTransformation))

        title = QLabel(f"Welcome, {self.username}")
        title.setStyleSheet("font-size:20px; font-weight:700;")

        self.back_btn = circle_icon_button("◀", "Back")
        self.fwd_btn  = circle_icon_button("▶", "Forward")

        top.addWidget(logo)
        top.addSpacing(6)
        top.addWidget(title)
        top.addStretch(1)
        top.addWidget(self.back_btn)
        top.addWidget(self.fwd_btn)
        root.addLayout(top)

        # Middle row: LEFT sidebar + center stack
        mid = QHBoxLayout(); mid.setSpacing(10)

        side = QFrame(objectName="SidePanel")
        side_l = QVBoxLayout(side)
        side_l.setContentsMargins(12, 12, 12, 12)
        side_l.setSpacing(8)

        def mkbtn(text: str, emoji: str) -> QPushButton:
            b = QPushButton(f"{emoji}  {text}", objectName="NavBtn")
            b.setMinimumHeight(44)
            b.setCursor(Qt.PointingHandCursor)
            b.setCheckable(True)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            return b

        self.btn_halls   = mkbtn("Halls",       "📅")
        self.btn_services = mkbtn("Services",     "🧰")
        self.btn_decors   = mkbtn("Decorations",  "🎈")
        self.btn_profile  = mkbtn("Personal Info","👤")
        self.btn_ai       = mkbtn("AI Help",      "🤖")

        self._nav_buttons = [
            ("halls", self.btn_halls),
            ("services", self.btn_services),
            ("decors", self.btn_decors),
            ("profile", self.btn_profile),
            ("ai", self.btn_ai),
        ]
        for _, b in self._nav_buttons:
            side_l.addWidget(b)
        side_l.addStretch(1)
        side.setFixedWidth(220)

        self.center_stack = QStackedWidget()
        self.center_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        mid.addWidget(side, 0)
        mid.addWidget(self.center_stack, 1)
        root.addLayout(mid, 1)

        # Inline style
        self.setStyleSheet("""
            QFrame#SidePanel {
                background:#fff;
                border:1px solid rgba(0,0,0,0.07);
                border-radius:14px;
            }
            QPushButton#NavBtn {
                text-align:left;
                padding:10px 14px;
                border:none;
                border-radius:10px;
                font-size:14px;
            }
            QPushButton#NavBtn:hover:!checked { background:rgba(0,0,0,0.04); }
            QPushButton#NavBtn:checked {
                background:rgba(66,133,244,0.12);
                border-left:3px solid rgb(66,133,244);
                padding-left:11px; font-weight:600;
            }
        """)
        self._update_nav_buttons()

    def _wire(self):
        self.back_btn.clicked.connect(self.go_back)
        self.fwd_btn.clicked.connect(self.go_forward)

        self.btn_halls.clicked.connect(lambda: self.navigate("halls"))
        self.btn_services.clicked.connect(lambda: self.navigate("services"))
        self.btn_decors.clicked.connect(lambda: self.navigate("decors"))
        self.btn_profile.clicked.connect(lambda: self.navigate("profile"))
        self.btn_ai.clicked.connect(lambda: self.navigate("ai"))

    # ----- Microfrontends -----
    def _load_microfrontends(self):
        # Halls list
        halls_v = HallListView()
        halls_p = HallListPresenter(HallListModel(), halls_v)
        halls_p.start()
        self._presenters.append(halls_p)
        self._register_center_page("halls", halls_v)
        halls_v.cardClicked.connect(self.open_hall_details)        # NEW

        # Services (list)
        svc_v = ServiceListView()
        svc_p = ServiceListPresenter(ServiceListModel(), svc_v)
        svc_p.start()
        self._presenters.append(svc_p)
        self._register_center_page("services", svc_v)
        svc_v.cardClicked.connect(self.open_service_details)       # NEW

        # Decorations (list)
        dec_v = DecorListView()
        dec_p = DecorListPresenter(DecorListModel(), dec_v)
        dec_p.start()
        self._presenters.append(dec_p)
        self._register_center_page("decors", dec_v)
        dec_v.cardClicked.connect(self.open_decor_details)         # NEW

        # AI (chat) – via factory (keeps settings out of the presenter)
        chat_v, chat_p = build_chat_module(PROJECT_ROOT, sys.executable)
        self._presenters.append(chat_p);
        self._register_center_page("ai", chat_v)

        # User profile (real view instead of placeholder)
        user_v = UserInfoView(); user_p = UserInfoPresenter(UserInfoModel(), user_v); user_p.start(self.username)
        self._presenters.append(user_p); self._register_center_page("profile", user_v)

        # Placeholders
        #self._register_center_page("profile", self._placeholder("Personal Info – coming soon"))
        # self._register_center_page("ai", self._placeholder("AI Help – coming soon"))

    def _placeholder(self, text: str) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.addStretch(1)
        lbl = QLabel(text, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("font-size:16px; color:#666;")
        lay.addWidget(lbl)
        lay.addStretch(1)
        return w

    def _register_center_page(self, name: str, widget: QWidget):
        self._center_pages[name] = widget
        self.center_stack.addWidget(widget)

    # ----- Details openers -----
    def open_hall_details(self, hall_id: int):
        page_name = f"hall:{hall_id}"
        if page_name in self._center_pages:
            self.navigate(page_name); return
        view = HallDetailsView()
        presenter = HallDetailsPresenter(HallDetailsModel(), view)
        presenter.start(hall_id)
        self._presenters.append(presenter)   # prevent GC
        self._register_center_page(page_name, view)
        self.navigate(page_name)

    def open_service_details(self, service_id: int):
        page_name = f"service:{service_id}"
        if page_name in self._center_pages:
            self.navigate(page_name); return
        view = ServiceDetailsView()
        presenter = ServiceDetailsPresenter(ServiceDetailsModel(), view)
        presenter.start(service_id)
        self._presenters.append(presenter)   # prevent GC
        self._register_center_page(page_name, view)
        self.navigate(page_name)

    def open_decor_details(self, decor_id: int):
        page_name = f"decor:{decor_id}"
        if page_name in self._center_pages:
            self.navigate(page_name); return
        view = DecorDetailsView()
        presenter = DecorDetailsPresenter(DecorDetailsModel(), view)
        presenter.start(decor_id)
        self._presenters.append(presenter)   # prevent GC
        self._register_center_page(page_name, view)
        self.navigate(page_name)

    # ----- Navigation helpers -----
    def navigate(self, name: str):
        if name not in self._center_pages:
            return
        self.center_stack.setCurrentWidget(self._center_pages[name])

        if self._hist_index == -1 or self._history[self._hist_index] != name:
            if self._hist_index < len(self._history) - 1:
                self._history = self._history[: self._hist_index + 1]
            self._history.append(name)
            self._hist_index += 1

        self._update_nav_buttons()
        for key, btn in self._nav_buttons:
            btn.setChecked(key == name)

    def go_back(self):
        if self._hist_index > 0:
            self._hist_index -= 1
            name = self._history[self._hist_index]
            self.center_stack.setCurrentWidget(self._center_pages[name])
            self._update_nav_buttons()
            for key, btn in self._nav_buttons:
                btn.setChecked(key == name)

    def go_forward(self):
        if self._hist_index < len(self._history) - 1:
            self._hist_index += 1
            name = self._history[self._hist_index]
            self.center_stack.setCurrentWidget(self._center_pages[name])
            self._update_nav_buttons()
            for key, btn in self._nav_buttons:
                btn.setChecked(key == name)

    def _update_nav_buttons(self):
        self.back_btn.setDisabled(self._hist_index <= 0)
        self.fwd_btn.setDisabled(self._hist_index >= len(self._history) - 1)

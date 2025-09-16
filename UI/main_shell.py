import sys
from pathlib import Path
from typing import Optional, List, Dict  # ← שימוש ב-typing עבור 3.8
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
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
    APP_BASE / "add_decor",   # <- ensure add_decor is on path if needed
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

# ---------- Details ----------
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

# --- Add Decor screen (imports) ---
from UI.add_decor.add_decor_view import AddDecorView
from UI.add_decor.add_decor_model import AddDecorModel
from UI.add_decor.add_decor_presenter import AddDecorPresenter


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


class AppWindow(QMainWindow):
    """Top-level window that owns a stack of pages (login / signup / shell)."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Planner – App")
        self.setWindowIcon(QIcon(str(APP_BASE / "style&icons" / "no_words_icon.png")))
        self.setMinimumSize(960, 640)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)
        self._pages: Dict[str, QWidget] = {}
        self._keepers: List[object] = []   # keep refs (presenters/views) to avoid GC
        self._shell = None  # type: Optional[MainShell]

    def keep(self, *objs) -> None:
        self._keepers.extend(objs)

    def add_page(self, name: str, widget: QWidget) -> None:
        self._pages[name] = widget
        self._stack.addWidget(widget)

    def set_shell(self, shell: "MainShell") -> None:
        if getattr(self, "_shell", None):
            self._stack.removeWidget(self._shell)
            self._shell.deleteLater()
        self._shell = shell
        self.add_page("shell", shell)
        self.keep(shell)

    def goto(self, name: str) -> None:
        w = self._pages.get(name)
        if w is not None:
            self._stack.setCurrentWidget(w)


class MainShell(QWidget):
    """Main application surface (after successful auth)."""
    def __init__(self, username: str):
        super().__init__()
        self.setWindowTitle("Event Planner – App")
        self.username = username

        self._history: List[str] = []
        self._hist_index: int = -1
        self._center_pages: Dict[str, QWidget] = {}
        self._presenters: List[object] = []
        self._user_presenter = None  # type: Optional[UserInfoPresenter]
        self._user_view = None       # type: Optional[UserInfoView]

        self._build_ui()
        self._wire()
        self._load_microfrontends()
        self.navigate("decors")  # default landing

    # ----- UI -----
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # Top bar
        top = QHBoxLayout()
        top.setSpacing(10)

        logo = QLabel()
        pm = QPixmap(str(APP_BASE / "style&icons" / "EventPlannerLogo.png"))
        if not pm.isNull():
            logo.setPixmap(pm.scaledToHeight(56, Qt.SmoothTransformation))

        title = QLabel("Welcome, {}".format(self.username))
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
        mid = QHBoxLayout()
        mid.setSpacing(10)

        side = QFrame(objectName="SidePanel")
        side_l = QVBoxLayout(side)
        side_l.setContentsMargins(12, 12, 12, 12)
        side_l.setSpacing(8)

        def mkbtn(text: str, emoji: str) -> QPushButton:
            b = QPushButton("{}  {}".format(emoji, text), objectName="NavBtn")
            b.setMinimumHeight(44)
            b.setCursor(Qt.PointingHandCursor)
            b.setCheckable(True)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            return b

        self.btn_halls    = mkbtn("Halls",        "📅")
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

    def _wire(self) -> None:
        self.back_btn.clicked.connect(self.go_back)
        self.fwd_btn.clicked.connect(self.go_forward)

        self.btn_halls.clicked.connect(lambda: self.navigate("halls"))
        self.btn_services.clicked.connect(lambda: self.navigate("services"))
        self.btn_decors.clicked.connect(lambda: self.navigate("decors"))
        self.btn_profile.clicked.connect(lambda: self.navigate("profile"))
        self.btn_ai.clicked.connect(lambda: self.navigate("ai"))

    # ----- Microfrontends -----
    def _load_microfrontends(self) -> None:
        # Halls list
        halls_v = HallListView()
        halls_p = HallListPresenter(HallListModel(), halls_v)
        halls_p.start()
        self._presenters.append(halls_p)
        self._register_center_page("halls", halls_v)
        halls_v.cardClicked.connect(self.open_hall_details)

        # Services (list)
        svc_v = ServiceListView()
        svc_p = ServiceListPresenter(ServiceListModel(), svc_v)
        svc_p.start()
        self._presenters.append(svc_p)
        self._register_center_page("services", svc_v)
        svc_v.cardClicked.connect(self.open_service_details)

        # Decorations (list)
        dec_v = DecorListView()
        dec_p = DecorListPresenter(DecorListModel(), dec_v)
        dec_p.start()
        self._presenters.append(dec_p)
        self._register_center_page("decors", dec_v)
        dec_v.cardClicked.connect(self.open_decor_details)

        # AI (chat)
        chat_v, chat_p = build_chat_module(PROJECT_ROOT, sys.executable)
        self._presenters.append(chat_p)
        self._register_center_page("ai", chat_v)

        # User profile
        user_v = UserInfoView()
        user_p = UserInfoPresenter(UserInfoModel(), user_v)
        user_p.start(self.username)
        self._presenters.append(user_p)
        self._register_center_page("profile", user_v)

        # keep references for refresh after 'add decor'
        self._user_presenter = user_p
        self._user_view = user_v

        # '+' in Owned items opens the Add-Decor screen
        user_v.addDecorClicked.connect(self.open_add_decor)

    def _placeholder(self, text: str) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.addStretch(1)
        lbl = QLabel(text, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("font-size:16px; color:#666;")
        lay.addWidget(lbl)
        lay.addStretch(1)
        return w

    def _register_center_page(self, name: str, widget: QWidget) -> None:
        self._center_pages[name] = widget
        self.center_stack.addWidget(widget)

    # ----- Details openers -----
    def open_hall_details(self, hall_id: int) -> None:
        page_name = "hall:{}".format(hall_id)
        if page_name in self._center_pages:
            self.navigate(page_name); return
        view = HallDetailsView()
        presenter = HallDetailsPresenter(HallDetailsModel(), view)
        presenter.start(hall_id)
        self._presenters.append(presenter)
        self._register_center_page(page_name, view)
        self.navigate(page_name)

    def open_service_details(self, service_id: int) -> None:
        page_name = "service:{}".format(service_id)
        if page_name in self._center_pages:
            self.navigate(page_name); return
        view = ServiceDetailsView()
        presenter = ServiceDetailsPresenter(ServiceDetailsModel(), view)
        presenter.start(service_id)
        self._presenters.append(presenter)
        self._register_center_page(page_name, view)
        self.navigate(page_name)

    def open_decor_details(self, decor_id: int) -> None:
        page_name = "decor:{}".format(decor_id)
        if page_name in self._center_pages:
            self.navigate(page_name); return
        view = DecorDetailsView()
        presenter = DecorDetailsPresenter(DecorDetailsModel(), view)
        presenter.start(decor_id)
        self._presenters.append(presenter)
        self._register_center_page(page_name, view)
        self.navigate(page_name)

    # ----- Add-Decor opener -----
    def open_add_decor(self) -> None:
        page_name = "add_decor"
        if page_name in self._center_pages:
            view = self._center_pages[page_name]
            if hasattr(view, "reset_form"):
                view.reset_form()
            self.navigate(page_name)
            return

        view = AddDecorView()
        model = AddDecorModel()

        def back_to_profile() -> None:
            # navigate back and refresh the profile data
            self.navigate("profile")
            if self._user_presenter is not None:
                self._user_presenter.start(self.username)

        presenter = AddDecorPresenter(
            model, view,
            current_username=self.username,
            on_success=back_to_profile
        )
        presenter.start()

        # optional: cancel goes back without creating
        if hasattr(view, "cancelRequested"):
            view.cancelRequested.connect(back_to_profile)

        self._presenters.append(presenter)
        self._register_center_page(page_name, view)
        self.navigate(page_name)

    # ----- Navigation helpers -----
    def navigate(self, name: str) -> None:
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

    def go_back(self) -> None:
        if self._hist_index > 0:
            self._hist_index -= 1
            name = self._history[self._hist_index]
            self.center_stack.setCurrentWidget(self._center_pages[name])
            self._update_nav_buttons()
            for key, btn in self._nav_buttons:
                btn.setChecked(key == name)

    def go_forward(self) -> None:
        if self._hist_index < len(self._history) - 1:
            self._hist_index += 1
            name = self._history[self._hist_index]
            self.center_stack.setCurrentWidget(self._center_pages[name])
            self._update_nav_buttons()
            for key, btn in self._nav_buttons:
                btn.setChecked(key == name)

    def _update_nav_buttons(self) -> None:
        self.back_btn.setDisabled(self._hist_index <= 0)
        self.fwd_btn.setDisabled(self._hist_index >= len(self._history) - 1)

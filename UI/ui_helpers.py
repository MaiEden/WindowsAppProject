# ui_helpers.py
from pathlib import Path
from PySide6.QtCore import QSize
from PySide6.QtGui import QMovie, QIcon
from PySide6.QtWidgets import QPushButton

_SPINNER_GIF_PATHS = [
    # ממליץ לשים קובץ קטן, שקוף, 24x24 בפאת' הזה
    Path(__file__).resolve().parents[0] / "style&icons" / "spinner.gif",
    Path(__file__).resolve().parents[0] / "style&icons" / "spinner2.gif",
]

def _find_spinner():
    for p in _SPINNER_GIF_PATHS:
        if p.exists():
            return str(p)
    return None

def start_button_loading(btn: QPushButton, loading_text: str = "מבצע פעולה..."):
    """שם את הכפתור במצב 'טעינה' עם ספינר מסתובב כאייקון."""
    if btn.property("_loading"):
        return  # כבר בטעינה

    btn.setProperty("_loading", True)
    btn.setProperty("_orig_text", btn.text())
    btn.setProperty("_orig_icon", btn.icon())

    btn.setDisabled(True)
    btn.setText(loading_text)

    spinner_path = _find_spinner()
    if spinner_path:
        movie = QMovie(spinner_path)
        btn.setProperty("_spinner_movie", movie)
        # בכל frame נעדכן את האייקון של הכפתור
        def _update_icon(_):
            btn.setIcon(QIcon(movie.currentPixmap()))
        movie.frameChanged.connect(_update_icon)
        movie.start()
        btn.setIconSize(QSize(20, 20))
    else:
        # ללא GIF — נשאר רק עם הטקסט; עדיין טוב UX-wise
        pass

def stop_button_loading(btn: QPushButton):
    """מחזיר את הכפתור ממצב 'טעינה' למצב רגיל."""
    if not btn.property("_loading"):
        return
    movie = btn.property("_spinner_movie")
    if movie:
        movie.stop()
    orig_text = btn.property("_orig_text") or ""
    orig_icon = btn.property("_orig_icon")
    btn.setText(orig_text)
    if orig_icon is not None:
        btn.setIcon(orig_icon)
    btn.setDisabled(False)
    # ניקוי פרופרטיס
    for prop in ["_loading", "_orig_text", "_orig_icon", "_spinner_movie"]:
        btn.setProperty(prop, None)

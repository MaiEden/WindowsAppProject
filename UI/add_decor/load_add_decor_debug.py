# load_add_decor_debug.py
import sys
from PySide6.QtWidgets import QApplication
from add_decor_model import AddDecorModel
from add_decor_presenter import AddDecorPresenter
from add_decor_view import AddDecorView
from pathlib import Path

def load_qss(app, *paths):
    css = ""
    for p in paths:
        p = Path(p)
        if p.exists():
            css += p.read_text(encoding="utf-8") + "\n"
        else:
            print(f"[QSS] Not found: {p.resolve()}")
    app.setStyleSheet(css)

def main():
    app = QApplication(sys.argv)

    # <- UPDATE THIS PATH to where your QSS is located
    load_qss(app, "add_decor.qss")

    view = AddDecorView()
    model = AddDecorModel(default_owner_username="Noa Hadad")
    presenter = AddDecorPresenter(model, view, current_username="Noa hadad")
    presenter.start()
    view.resize(640, 820)
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

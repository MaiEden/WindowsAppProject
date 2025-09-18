import sys
from PySide6.QtWidgets import QApplication
from UI.add_decor.add_decor_model import AddDecorModel
from UI.add_decor.add_decor_presenter import AddDecorPresenter
from UI.add_decor.add_decor_view import AddDecorView
from pathlib import Path

def load_qss(app, styl):
    css = ""
    styl = Path(styl)
    if styl.exists():
        css += styl.read_text(encoding="utf-8") + "\n"
    else:
        print(f"[QSS] Not found: {styl.resolve()}")
    app.setStyleSheet(css)

def main():
    app = QApplication(sys.argv)
    load_qss(app, "UI/add_decor/add_decor.qss")

    # View + Model + Presenter wiring
    view = AddDecorView()
    model = AddDecorModel(default_owner_username="Noa Hadad")
    presenter = AddDecorPresenter(model, view, current_username="Noa hadad")
    presenter.start()
    view.resize(640, 820)
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
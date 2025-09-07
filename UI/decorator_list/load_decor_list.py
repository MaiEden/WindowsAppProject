"""
Run this file to debug the Decor list screen in isolation.
Usage:
    python -m UI.decorator_list.debug_decor_list
(הקפידי שיהיה __init__.py בתיקייה UI/decorator_list)
"""
import sys
from PySide6.QtWidgets import QApplication
from decor_list_model import DecorListModel
from decor_list_view import DecorListView
from decor_list_presenter import DecorListPresenter

def main():
    app = QApplication(sys.argv)
    view = DecorListView()
    model = DecorListModel()
    presenter = DecorListPresenter(model, view)
    presenter.start()
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

"""
Run this file to debug the Halls list screen in isolation.
Usage:
    python -m UI.halls_list.debug_hall_list
(הקפידי שיהיה __init__.py בתיקייה UI/halls_list)
"""
import sys
from PySide6.QtWidgets import QApplication
from hall_list_model import HallListModel
from hall_list_view import HallListView
from hall_list_presenter import HallListPresenter

def main():
    app = QApplication(sys.argv)
    view = HallListView()
    model = HallListModel()
    presenter = HallListPresenter(model, view)
    presenter.start()
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

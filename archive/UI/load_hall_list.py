"""
Run this file to debug the Halls list screen in isolation.
"""
import sys
from PySide6.QtWidgets import QApplication
from UI.halls_list.hall_list_model import HallListModel
from UI.halls_list.hall_list_view import HallListView
from UI.halls_list.hall_list_presenter import HallListPresenter

def main():
    app = QApplication(sys.argv)
    # View + Model + Presenter wiring
    view = HallListView()
    model = HallListModel()
    presenter = HallListPresenter(model, view)
    presenter.start()
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
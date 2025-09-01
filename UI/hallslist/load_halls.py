from PySide6.QtWidgets import QApplication
from UI.hallslist.halls_model import HallsModel
from UI.hallslist.halls_view import HallsView
from UI.hallslist.halls_presenter import HallsPresenter
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = HallsModel()
    view = HallsView()
    presenter = HallsPresenter(model, view)
    view.show()
    sys.exit(app.exec())

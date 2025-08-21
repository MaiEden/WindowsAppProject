from PySide6.QtWidgets import QApplication
from halls_model import HallsModel
from halls_view import HallsView
from halls_presenter import HallsPresenter
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = HallsModel()
    view = HallsView()
    presenter = HallsPresenter(model, view)
    view.show()
    sys.exit(app.exec())

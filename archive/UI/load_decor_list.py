"""
Run this file to debug the Decor list screen in isolation.
"""
import sys
from PySide6.QtWidgets import QApplication
from UI.decorator_list.decor_list_model import DecorListModel
from UI.decorator_list.decor_list_view import DecorListView
from UI.decorator_list.decor_list_presenter import DecorListPresenter

def main():
    app = QApplication(sys.argv)

    # View + Model + Presenter wiring
    view = DecorListView()
    model = DecorListModel()
    presenter = DecorListPresenter(model, view)
    presenter.start()
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
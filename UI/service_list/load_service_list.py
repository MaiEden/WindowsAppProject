"""
Run this file to debug the Services list screen in isolation.
Usage:
    python load_service_list.py
"""
import sys
from PySide6.QtWidgets import QApplication
from service_list_model import ServiceListModel
from service_list_view import ServiceListView
from service_list_presenter import ServiceListPresenter

def main():
    app = QApplication(sys.argv)
    view = ServiceListView()
    model = ServiceListModel()
    presenter = ServiceListPresenter(model, view)
    presenter.start()
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

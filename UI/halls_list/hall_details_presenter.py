from PySide6.QtCore import QObject
from .hall_details_model import HallDetailsModel
from .hall_details_view import HallDetailsView

class HallDetailsPresenter(QObject):
    def __init__(self, model: HallDetailsModel, view: HallDetailsView):
        super().__init__()
        self.model = model
        self.view = view

    def start(self, hall_id: int):
        self.view.set_busy(True)
        try:
            row = self.model.fetch(hall_id) or {}
        except Exception as e:
            self.view.show_error(str(e))
            self.view.set_busy(False)
            return
        self.view.populate(row)
        self.view.set_busy(False)
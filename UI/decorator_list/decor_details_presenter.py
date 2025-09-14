from PySide6.QtCore import QObject
from .decor_details_model import DecorDetailsModel
from .decor_details_view import DecorDetailsView

class DecorDetailsPresenter(QObject):
    def __init__(self, model: DecorDetailsModel, view: DecorDetailsView):
        super().__init__()
        self.model = model
        self.view = view

    def start(self, decor_id: int):
        self.view.set_busy(True)
        try:
            row = self.model.fetch(decor_id) or {}
        except Exception as e:
            self.view.show_error(str(e))
            self.view.set_busy(False)
            return
        self.view.populate(row)
        self.view.set_busy(False)

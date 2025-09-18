from PySide6.QtCore import QObject
from .service_details_model import ServiceDetailsModel
from .service_details_view import ServiceDetailsView

class ServiceDetailsPresenter(QObject):
    def __init__(self, model: ServiceDetailsModel, view: ServiceDetailsView):
        super().__init__()
        self.model = model
        self.view = view

    def start(self, service_id: int):
        self.view.set_busy(True)
        try:
            row = self.model.fetch(service_id) or {}
        except Exception as e:
            self.view.show_error(str(e))
            self.view.set_busy(False)
            return
        self.view.populate(row)
        self.view.set_busy(False)
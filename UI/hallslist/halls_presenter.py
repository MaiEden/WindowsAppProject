"""
Presenter: mediates between Model and View
"""
from server.database.read_api import get_halls_filtered
from .halls_model import HallsModel
from .halls_view import HallsView


class HallsPresenter:
    def __init__(self, model: HallsModel, view: HallsView):
        self.model = model
        self.view = view
        self.all_halls = []
        self._connect_signals()
        self.load_data()

    def _connect_signals(self):
        self.view.filter_changed.connect(self.apply_filters)

    def load_data(self):
        self.all_halls = self.model.fetch_all_halls()
        self.view.populate_filters(self.all_halls)
        self.view.render_halls(self.all_halls)

        # Connect filters
        self.view.filter_changed.connect(self.apply_filters)

    def apply_filters(self):
        region = self.view.filter_region.currentText()
        hall_type = self.view.filter_type.currentText()
        search = self.view.search_box.text().strip()

        halls = get_halls_filtered(region, hall_type, search)
        self.view.render_halls(halls)

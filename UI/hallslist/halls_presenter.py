"""
halls_presenter.py
Presenter: Mediates between the Model (data) and the View (UI).

Responsibilities:
- Load hall data from the model and pass it to the view.
- Listen to filter/search events from the view and apply filtering logic.
- Act as a middle layer so the view does not directly call the database.
"""


from .halls_model import HallsModel
from .halls_view import HallsView


class HallsPresenter:
    def __init__(self, model: HallsModel, view: HallsView):
        """
        Initialize the presenter with a model and a view.
        - model: Responsible for fetching hall data from the DB.
        - view: Responsible for displaying the halls and UI filters.

        On creation:
        1. Connects signals from the view to internal handlers.
        2. Loads initial data (all halls) and renders them in the view.
        """
        self.model = model
        self.view = view
        self.all_halls = []
        self._connect_signals()
        self.load_data()

    def _connect_signals(self):
        """
        Connect view signals to presenter logic.
        Specifically: when filters change in the view,
        call `apply_filters` to refresh the results.
        """
        self.view.filter_changed.connect(self.apply_filters)


    def load_data(self):
        """
        Fetch all halls from the model, populate filter options,
        and render the initial list of halls in the view.
        """
        self.all_halls = self.model.fetch_all_halls()
        self.view.populate_filters(self.all_halls)
        self.view.render_halls(self.all_halls)

        # Ensure filters are connected (redundant safeguard)
        self.view.filter_changed.connect(self.apply_filters)

    def apply_filters(self):
        """
        Apply filters based on the current view state.

        - Reads the selected region, hall type, and search term from the view.
        - Fetches filtered halls from the model.
        - Updates the view to display only the filtered results.
        """
        region = self.view.filter_region.currentText()
        hall_type = self.view.filter_type.currentText()
        search = self.view.search_box.text().strip()

        halls = self.model.fetch_filtered_halls(region, hall_type, search)
        self.view.render_halls(halls)

# UI/graphs/decor_price_presenter.py
class DecorPricePresenter:
    """
    Presenter for the "Decor Price" graph (MVP).
    - Orchestrates Model and View.
    - Loads data for a given decor_id and instructs the View to render.
    """
    def __init__(self, model, view) -> None:
        self.model = model
        self.view = view

    def show_for(self, decor_id: int) -> None:
        """
        Load data for the given decor_id and render the chart.
        """
        self.model.load(decor_id)
        self.view.render_chart(
            items=self.model.rows(),
            focus_id=self.model.focus_id,
            category=self.model.category,
            focus_item=self.model.focus_item,
        )

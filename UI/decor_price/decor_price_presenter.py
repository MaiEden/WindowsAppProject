# UI/decor_price/decor_price_presenter.py
class DecorPricePresenter:
    def __init__(self, model, view) -> None:
        self.model = model
        self.view = view

    def show_for(self, decor_id: int) -> None:
        self.model.load(decor_id)
        self.view.render_chart(
            items=self.model.rows(),
            focus_id=self.model.focus_id,
            category=self.model.category,
            focus_item=self.model.focus_item,  # ← כדי למלא את כרטיס “Selected decor”
        )

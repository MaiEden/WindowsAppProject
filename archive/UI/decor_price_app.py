# UI/decor/decor_price_app.py runs the graphs
import sys
from PySide6.QtWidgets import QApplication
from UI.graphs.decor_price_model import DecorPriceModel
from UI.graphs.decor_price_view import DecorPriceView
from UI.graphs.decor_price_presenter import DecorPricePresenter

def main():
    app = QApplication.instance() or QApplication(sys.argv)

    # View + Model + Presenter wiring
    model = DecorPriceModel()
    view = DecorPriceView()
    presenter = DecorPricePresenter(model, view)

    # Here you manually type the ID you want to check.
    DECOR_ID = 5

    presenter.show_for(DECOR_ID)

    view.resize(960, 640)
    view.show()
    app.exec()

if __name__ == "__main__":
    main()
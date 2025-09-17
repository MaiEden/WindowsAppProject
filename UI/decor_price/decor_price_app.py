# UI/decor/decor_price_app.py
import sys
from PySide6.QtWidgets import QApplication
from UI.decor_price.decor_price_model import DecorPriceModel
from UI.decor_price.decor_price_view import DecorPriceView
from UI.decor_price.decor_price_presenter import DecorPricePresenter

def main():
    app = QApplication.instance() or QApplication(sys.argv)

    model = DecorPriceModel()
    view = DecorPriceView()
    presenter = DecorPricePresenter(model, view)

    # >>> כאן אתה מקליד ידנית את ה-ID שאתה רוצה לבדוק <<<
    DECOR_ID = 5   # לדוגמה: 5, תחליף ל-ID אמיתי שקיים אצלך בטבלה dbo.DecorOption

    presenter.show_for(DECOR_ID)

    view.resize(960, 640)
    view.show()
    app.exec()

if __name__ == "__main__":
    main()

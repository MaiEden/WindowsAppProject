"""
AddDecorPresenter
-----------------
- Validates form input and returns a field->error map.
- Shows an error summary + inline field errors + red highlight.
- Calls the model for: ensure owner, create decor, link owner.
"""

from typing import Dict, Any, List, Tuple
from PySide6.QtCore import QObject
from add_decor_model import AddDecorModel

CATEGORIES = [
    "Balloons","Flowers","Tableware","Linens","Lighting",
    "Backdrop","CakeStands","Props","Centerpieces","Signage"
]


class AddDecorPresenter(QObject):
    def __init__(self, model: AddDecorModel, view) -> None:
        super().__init__()
        self.model = model
        self.view = view
        self._connect()

    def _connect(self):
        self.view.submitRequested.connect(self.on_submit)
        self.view.cancelRequested.connect(self.on_cancel)
        self.view.priceChanged.connect(self.on_price_changed)

    # lifecycle
    def start(self):
        self.view.populate_categories(CATEGORIES)
        self.on_price_changed()

    # helpers
    def _validate(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Returns {field_key: error_text} where keys match what the view expects.

        Required:
        - DecorName
        - Category
        - At least one price > 0 among PriceSmall/PriceMedium/PriceLarge
        """
        errors: Dict[str, str] = {}

        # Required: name + category
        if not (data.get("DecorName") or "").strip():
            errors["DecorName"] = "Name is required."

        if not (data.get("Category") or "").strip():
            errors["Category"] = "Category is required."

        # At least one price > 0
        ps = float(data.get("PriceSmall") or 0)
        pm = float(data.get("PriceMedium") or 0)
        pl = float(data.get("PriceLarge") or 0)
        if max(ps, pm, pl) <= 0:
            msg = "Enter at least one positive price (small/medium/large)."
            errors["PriceSmall"] = msg
            errors["PriceMedium"] = msg
            errors["PriceLarge"] = msg

        # Email (basic sanity)
        email = (data.get("ContactEmail") or "").strip()
        if email:
            parts = email.split("@")
            if len(parts) != 2 or "." not in parts[1]:
                errors["ContactEmail"] = "Email looks invalid."

        return errors

    def _price_hint(self, prices: Tuple[float, float, float]) -> str:
        p = [x for x in prices if x and x > 0]
        if not p:
            return ""
        return f"Pricing hint: from ₪{min(p):.0f}"

    # slots
    def on_price_changed(self):
        self.view.set_price_hint(self._price_hint(self.view.get_prices()))

    def on_cancel(self):
        self.view.reset_form()

    def on_submit(self):
        self.view.clear_errors()
        self.view.set_busy(True)
        try:
            data = self.view.collect_form()
            errors = self._validate(data)
            if errors:
                # Inline errors + summary banner
                self.view.apply_errors(errors)
                self.view.show_error_summary("Validation failed. Please fix the highlighted fields.")
                return

            # Ensure owner (MVP default owner: "Noa Hadad")
            owner_name = self.model.default_owner_username
            user = self.model.get_user_by_name(owner_name)
            if not user:
                user_id = self.model.ensure_user("050-1111111", owner_name, "hash:noa", "Rehovot")
            else:
                user_id = int(user.get("UserId"))

            # Create decor + link as OWNER
            decor_id = self.model.create_decor(data)
            self.model.link_owner(user_id, decor_id, "OWNER")

            self.view.show_success("Decoration created and linked to owner.")
            self.view.reset_form()

        except Exception as e:
            self.view.show_error_summary(str(e))
        finally:
            self.view.set_busy(False)

# user_info_presenter.py — minimal docs
# Presenter for the "User Info" screen (MVP).
# - Orchestrates Model (data fetching) and View (rendering).
# - Loads a user by username, populates header and section cards.

from typing import Optional
from .user_info_model import UserInfoModel
from .user_info_view import UserInfoView

class UserInfoPresenter:

    def __init__(self, model: UserInfoModel, view: UserInfoView):
        """Store references to the Model (data) and the View (UI)."""
        self.m = model
        self.v = view
        # Future: connect signals (refresh, click handlers, etc.)

    def start(self, username: str) -> None:
        """
        Load user data and render the screen.
        """
        user = self.m.get_user(username)
        if not user:
            # Empty state
            self.v.set_user_header(username, "", "")
            self.v.show_decor_cards([])
            self.v.show_service_cards([])
            self.v.show_hall_cards([])
            self.v.show_owned_cards([])
            return

        uid = int(user["UserId"])
        self.v.set_user_header(user["Username"], user["Phone"], user["Region"])

        decs = self.m.get_decor_used(uid)
        svcs = self.m.get_services_used(uid)
        halls = self.m.get_halls_used(uid)
        owned = self.m.get_owned_items(uid)

        # Mark used sections with a small pill label (owned already includes it from SQL).
        for it in decs:
            it["pill"] = "Decor"
        for it in svcs:
            it["pill"] = "Service"
        for it in halls:
            it["pill"] = "Hall"

        self.v.show_decor_cards(decs)
        self.v.show_service_cards(svcs)
        self.v.show_hall_cards(halls)
        self.v.show_owned_cards(owned)

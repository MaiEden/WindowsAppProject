# user_info_presenter.py
from typing import Optional
from .user_info_model import UserInfoModel
from .user_info_view import UserInfoView

class UserInfoPresenter:
    def __init__(self, model: UserInfoModel, view: UserInfoView):
        self.m = model
        self.v = view
        # future: wire signals if needed (refresh, clicks to open details, etc.)

    def start(self, username: str):
        user = self.m.get_user(username)
        if not user:
            self.v.set_user_header(username, "", "")
            self.v.show_decor_cards([]); self.v.show_service_cards([]); self.v.show_hall_cards([])
            return

        uid = int(user["UserId"])
        self.v.set_user_header(user["Username"], user["Phone"], user["Region"])

        decs = self.m.get_decor_used(uid)
        svcs = self.m.get_services_used(uid)
        halls = self.m.get_halls_used(uid)

        # להציג
        for it in decs:  it["pill"]  = "Decor"
        for it in svcs:  it["pill"]  = "Service"
        for it in halls: it["pill"]  = "Hall"

        self.v.show_decor_cards(decs)
        self.v.show_service_cards(svcs)
        self.v.show_hall_cards(halls)

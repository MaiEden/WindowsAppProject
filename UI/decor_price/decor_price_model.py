# UI/decor_price/decor_price_model.py
from typing import List, Dict, Any, Optional
from UI import server_access

class DecorPriceModel:
    """
    טוען את הקישוט הראשי לפי DecorId, מגלה את הקטגוריה שלו,
    מביא את כל הקישוטים מאותה קטגוריה, מחשב "מחיר בינוני" לכל אחד,
    ומסדר בסדר עולה.
    """

    def __init__(self) -> None:
        self._items: List[Dict[str, Any]] = []
        self.focus_id: Optional[int] = None
        self.focus_item: Optional[Dict[str, Any]] = None
        self.category: Optional[str] = None

    # ---------- API helpers ----------
    def _get_focus(self, decor_id: int) -> Dict[str, Any]:
        row = server_access.request(f"/DB/decors/get/{decor_id}")  # קיים כבר ב-ServerAPI :contentReference[oaicite:4]{index=4}
        if not isinstance(row, dict) or not row:
            raise ValueError("Decor not found")
        return row

    def _try_prices_endpoint(self, category: str) -> Optional[List[Dict[str, Any]]]:
        """
        ניסיון להשתמש ב-endpoint מתקדם שמחזיר גם PriceSmall/Medium/Large.
        אם לא קיים אצלך – פשוט נחזיר None ונשתמש ב-fallback.
        """
        try:
            data = server_access.request(
                f"/DB/decors/prices?category={category}&available=true&order_by=MidPrice&ascending=true"
            )
            if isinstance(data, list) and data:
                return data
        except Exception:
            pass
        return None

    def _fallback_fetch_and_enrich(self, category: str) -> List[Dict[str, Any]]:
        """
        fallback: נביא רשימת קישוטים בסיסית לפי קטגוריה דרך /DB/decors/list,
        ואז לכל אחד נביא /DB/decors/get/{id} כדי לקרוא את PriceSmall/Medium/Large
        ולחשב MidPrice מקומית.
        """
        # הרשימה הבסיסית (מוחזרת ללא מחירי S/M/L מלאים) :contentReference[oaicite:5]{index=5} :contentReference[oaicite:6]{index=6}
        base_list = server_access.request(
            f"/DB/decors/list?category={category}&available=true&order_by=DecorName&ascending=true"
        )
        if not isinstance(base_list, list):
            raise TypeError("/DB/decors/list must return a list")

        enriched: List[Dict[str, Any]] = []
        for row in base_list:
            did = row.get("DecorId") or row.get("decorId") or row.get("id")
            if did is None:
                continue
            full = server_access.request(f"/DB/decors/get/{int(did)}")  # מחזיר את כל השדות של DecorOption :contentReference[oaicite:7]{index=7}
            if not isinstance(full, dict):
                continue

            p_s = full.get("PriceSmall")
            p_m = full.get("PriceMedium")
            p_l = full.get("PriceLarge")

            # חישוב מחיר בינוני:
            # 1) אם יש PriceMedium – זה הערך
            # 2) אחרת ממוצע PriceSmall/PriceLarge אם שניהם קיימים
            # 3) אחרת המחיר היחיד שקיים מבין S/L
            mid = None
            if p_m is not None:
                mid = float(p_m)
            elif p_s is not None and p_l is not None:
                mid = (float(p_s) + float(p_l)) / 2.0
            else:
                mid = float(p_s if p_s is not None else p_l)

            enriched.append({
                "DecorId": int(full.get("DecorId")),
                "DecorName": full.get("DecorName"),
                "Category": full.get("Category"),
                "Region": full.get("Region"),
                "PhotoUrl": full.get("PhotoUrl"),
                "Available": full.get("Available"),
                "PriceSmall": p_s,
                "PriceMedium": p_m,
                "PriceLarge": p_l,
                "MidPrice": mid,
            })

        # מיון משני: MidPrice ואז שם
        enriched.sort(key=lambda d: ((d["MidPrice"] if d["MidPrice"] is not None else 1e18),
                                     str(d.get("DecorName") or "")))
        return enriched

    # ---------- Public API ----------
    def load(self, decor_id: int, only_available: bool = True) -> None:
        # פריט פוקוס
        focus = self._get_focus(decor_id)
        self.focus_item = focus
        self.focus_id = int(focus.get("DecorId"))
        self.category = focus.get("Category")  # עמודה קיימת ב-DecorOption :contentReference[oaicite:8]{index=8}

        # נסה להביא רשימה עשירה (אם הוספת endpoint מתקדם)
        data = self._try_prices_endpoint(self.category)
        if data is None:
            # fallback: נביא דרך /DB/decors/list + העשרה לפי get/{id}
            data = self._fallback_fetch_and_enrich(self.category)

        # סינון זמינות אם ביקשת
        if only_available:
            data = [d for d in data if bool(d.get("Available", True))]

        # ודא מיון עולה לפי MidPrice
        data.sort(key=lambda d: ((float(d.get("MidPrice") or 0)), str(d.get("DecorName") or "")))
        self._items = data

    def rows(self) -> List[Dict[str, Any]]:
        return list(self._items)

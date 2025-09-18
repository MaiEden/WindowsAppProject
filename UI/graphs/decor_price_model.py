# UI/graphs/decor_price_model.py
from typing import List, Dict, Any, Optional
from UI import server_access  # אותו helper שבו משתמש HallListModel שלך

class DecorPriceModel:
    """
    Load a focus decor by ID, derive its category, fetch all decors in that category,
    ensure a 'MidPrice' per item (single source of truth), and expose a sorted list.
    """

    def __init__(self) -> None:
        self._items: List[Dict[str, Any]] = []
        self.focus_id: Optional[int] = None
        self.focus_item: Optional[Dict[str, Any]] = None
        self.category: Optional[str] = None

    # ---------- Normalization helpers ----------
    def _ensure_midprice(self, it: Dict[str, Any]) -> float:
        """
        Ensure 'MidPrice' exists on the item.
        Rule: PriceMedium > avg(S/L) > S or L > MidPrice > MinPrice > 0.
        Returns the computed value.
        """
        def _to_float(x):
            try:
                return None if x is None else float(x)
            except Exception:
                return None

        p_s = _to_float(it.get("PriceSmall"))
        p_m = _to_float(it.get("PriceMedium"))
        p_l = _to_float(it.get("PriceLarge"))

        if p_m is not None:
            mid = p_m
        elif p_s is not None and p_l is not None:
            mid = (p_s + p_l) / 2.0
        elif p_s is not None:
            mid = p_s
        elif p_l is not None:
            mid = p_l
        else:
            mp = _to_float(it.get("MidPrice"))
            mn = _to_float(it.get("MinPrice"))
            mid = mp if mp is not None else (mn if mn is not None else 0.0)

        it["MidPrice"] = float(mid or 0.0)
        return it["MidPrice"]

    def _normalize_item(self, it: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coerce common fields to consistent types and ensure MidPrice.
        - DecorId -> int
        - DecorName -> str
        - Available -> bool (default True)
        - PriceSmall/Medium/Large/MinPrice/MidPrice -> float or None
        """
        def _to_float(x):
            try:
                return None if x is None else float(x)
            except Exception:
                return None

        # id/name/available
        decor_id = it.get("DecorId") or it.get("decorId") or it.get("id")
        if decor_id is not None:
            try:
                it["DecorId"] = int(decor_id)
            except Exception:
                pass
        name = it.get("DecorName") or it.get("Name") or ""
        it["DecorName"] = str(name)
        it["Available"] = bool(it.get("Available", True))

        # numeric prices
        it["PriceSmall"]  = _to_float(it.get("PriceSmall"))
        it["PriceMedium"] = _to_float(it.get("PriceMedium"))
        it["PriceLarge"]  = _to_float(it.get("PriceLarge"))
        it["MinPrice"]    = _to_float(it.get("MinPrice"))
        it["MidPrice"]    = _to_float(it.get("MidPrice"))

        # ensure mid price exists
        self._ensure_midprice(it)
        return it

    def _postprocess_list(self, items: List[Dict[str, Any]], only_available: bool) -> List[Dict[str, Any]]:
        """
        Normalize all items, optionally filter by availability,
        and sort ascending by (MidPrice, DecorName).
        """
        normed: List[Dict[str, Any]] = [self._normalize_item(dict(it)) for it in (items or [])]
        if only_available:
            normed = [d for d in normed if bool(d.get("Available", True))]
        normed.sort(key=lambda d: (float(d.get("MidPrice") or 0), str(d.get("DecorName") or "")))
        return normed

    # ---------- API helpers ----------
    def _get_focus(self, decor_id: int) -> Dict[str, Any]:
        """Fetch the focus decor from ServerAPI (/DB/decors/get/{id}); raise if missing/invalid."""
        row = server_access.request(f"/DB/decors/get/{decor_id}")
        if not isinstance(row, dict) or not row:
            raise ValueError("Decor not found")
        return row

    def _try_prices_endpoint(self, category: str) -> Optional[List[Dict[str, Any]]]:
        """
        Try an advanced endpoint that already returns S/M/L prices + MidPrice.
        """
        try:
            data = server_access.request(
                f"/DB/decors/prices?category={category}&available=true&order_by=MidPrice&ascending=true"
            )
            if isinstance(data, list) and data:
                return [(dict(it)) for it in data]
        except Exception:
            pass
        return None

    def _fallback_fetch_and_enrich(self, category: str) -> List[Dict[str, Any]]:
        """
        Fallback path:
        - GET /DB/decors/list?category=... (basic fields),
        """
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
            full = server_access.request(f"/DB/decors/get/{int(did)}")  # מחזיר את כל השדות של DecorOption
            if not isinstance(full, dict):
                continue
        return full

    # ---------- Public API ----------
    def load(self, decor_id: int, only_available: bool = True) -> None:
        """
        Populate the model:
          - Resolve focus decor + category and ensure MidPrice on focus,
          - Fetch category items (advanced endpoint or fallback),
          - Normalize all, optionally filter by Available, sort ascending by (MidPrice, DecorName),
          - Store into self._items.
        """
        # focus item (normalize to guarantee MidPrice)
        focus = self._get_focus(decor_id)
        self.focus_item = self._normalize_item(focus)
        self.focus_id = int(self.focus_item.get("DecorId"))
        self.category = self.focus_item.get("Category")

        # Try advanced prices endpoint; fall back if needed
        data = self._try_prices_endpoint(self.category)
        if data is None:
            data = self._fallback_fetch_and_enrich(self.category)

        # unify: normalize/filter/sort in one place (idempotent)
        self._items = self._postprocess_list(data, only_available)

    def rows(self) -> List[Dict[str, Any]]:
        """Return a shallow copy of the computed items list."""
        return list(self._items)
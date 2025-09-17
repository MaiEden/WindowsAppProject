# UI/decor_price/decor_price_view.py
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy,
    QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt, QSize, QMargins
from PySide6.QtGui import QBrush, QColor, QFont
from PySide6.QtCharts import (
    QChart, QChartView, QStackedBarSeries, QBarSet, QBarCategoryAxis, QValueAxis,
)

# ===== Tuning =====
MAX_LINE_LEN = 12        # אורך שורה לפני שבירה
MAX_LINES = 3            # מקס' שורות לתווית

# ---------- helpers ----------
def _wrap_words(text: str, max_line_len: int, max_lines: int) -> str:
    words = (text or "").split()
    lines: List[str] = []
    cur = ""
    i = 0
    while i < len(words) and len(lines) < max_lines:
        w = words[i]
        cand = w if not cur else f"{cur} {w}"
        if len(cand) <= max_line_len:
            cur = cand
            i += 1
        else:
            if cur:
                lines.append(cur); cur = ""
            else:
                lines.append(w[:max_line_len]); i += 1
        if len(lines) == max_lines - 1 and i < len(words):
            rest = " ".join(words[i:])
            lines.append(rest if len(rest) <= max_line_len else rest[:max_line_len - 1] + "…")
            return "\n".join(lines)
    if cur:
        lines.append(cur)
    return "\n".join(lines[:max_lines])

def _wrap_multiline(name: str, max_line_len: int = MAX_LINE_LEN, max_lines: int = MAX_LINES) -> str:
    s = (name or "").strip()
    if not s:
        return ""
    for sep in (" – ", " — ", " - ", " –", "– ", "-"):
        if sep in s and len(s) > max_line_len:
            parts = s.split(sep)
            if len(parts) >= 2:
                left = parts[0].strip()
                right = sep.join(parts[1:]).strip()
                return (_wrap_words(left, max_line_len, 1) + "\n" +
                        _wrap_words(right, max_line_len, max_lines - 1)).strip()
    return _wrap_words(s, max_line_len, max_lines)

def _fmt_currency(v: float) -> str:
    try:
        return f"₪{int(round(float(v)))}"
    except Exception:
        return "₪0"

def _calc_midprice(item: Dict[str, Any]) -> float:
    """Medium > avg(S/L) > S or L > MidPrice > MinPrice > 0."""
    p_s = item.get("PriceSmall")
    p_m = item.get("PriceMedium")
    p_l = item.get("PriceLarge")
    if p_m is not None: return float(p_m)
    if p_s is not None and p_l is not None: return (float(p_s) + float(p_l)) / 2.0
    if p_s is not None: return float(p_s)
    if p_l is not None: return float(p_l)
    mp = item.get("MidPrice")
    if mp is not None: return float(mp)
    mn = item.get("MinPrice")
    if mn is not None: return float(mn)
    return 0.0

def _ideal_bar_width_ratio(n_items: int, view_width_px: int) -> float:
    """
    רוחב עמודות 'יפה' כברירת מחדל, מצטמצם בהדרגה כשאין מקום.
    """
    if n_items <= 8: base = 0.60
    elif n_items <= 15: base = 0.45
    else: base = 0.32
    if view_width_px < 820: base -= 0.05
    if view_width_px < 680: base -= 0.05
    return max(0.25, min(0.70, base))

class _Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            #Card {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
        """)

# ---------- main view ----------
class DecorPriceView(QWidget):
    """
    - Scroll אנכי בלבד
    - כרטיס 'Selected decor' (ללא תמונה) עם מחיר בינוני
    - גרף עמודות מודגש (Stacked: אפור + כחול)
    - ציר X רב־שורות ללא חיתוך
    - קלפי תקציר: Lowest / Average / Highest
    """

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("DecorPriceView")
        self.setWindowTitle("Decor Price Comparison")

        # ===== Scroll container =====
        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # אין גלילה אופקית

        self._container = QWidget()
        self._root = QVBoxLayout(self._container)
        self._root.setContentsMargins(16, 16, 16, 16)
        self._root.setSpacing(16)
        self._scroll.setWidget(self._container)

        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.addWidget(self._scroll)

        # ===== Header =====
        header = _Card()
        h_lay = QHBoxLayout(header); h_lay.setContentsMargins(16, 12, 16, 12)
        dot = QLabel(); dot.setFixedSize(12, 12); dot.setStyleSheet("background:#2563eb; border-radius:6px;")
        title_box = QVBoxLayout()
        h1 = QLabel("Decor Price Comparison"); h1.setStyleSheet("font-size:20px; font-weight:700; color:#111827;")
        p1 = QLabel("Visual analysis of prices by category"); p1.setStyleSheet("font-size:12px; color:#6b7280;")
        title_box.addWidget(h1); title_box.addWidget(p1); title_box.setSpacing(2)
        h_lay.addWidget(dot); h_lay.addSpacing(8); h_lay.addLayout(title_box); h_lay.addStretch(1)
        self._root.addWidget(header)

        # ===== Selected Decor Card =====
        self.card_selected = _Card()
        cs = QHBoxLayout(self.card_selected); cs.setContentsMargins(16, 16, 16, 16); cs.setSpacing(16)

        info_box = QVBoxLayout(); info_box.setSpacing(6)
        selected_row = QHBoxLayout(); selected_row.setSpacing(6)
        star = QLabel("★"); star.setStyleSheet("color:#f59e0b; font-size:18px;")
        self.sel_name = QLabel(""); self.sel_name.setStyleSheet("font-size:18px; font-weight:700; color:#111827;")
        selected_row.addWidget(star); selected_row.addWidget(self.sel_name); selected_row.addStretch(1)

        meta_row = QHBoxLayout(); meta_row.setSpacing(8)
        self.sel_cat = QLabel(""); self.sel_cat.setStyleSheet(
            "background:#dbeafe; color:#1e40af; padding:2px 8px; border-radius:999px; font-size:12px;"
        )
        self.sel_price = QLabel(""); self.sel_price.setStyleSheet("font-size:18px; color:#16a34a; font-weight:700;")
        meta_row.addWidget(self.sel_cat); meta_row.addSpacing(8); meta_row.addWidget(self.sel_price); meta_row.addStretch(1)

        info_box.addLayout(selected_row)
        info_box.addLayout(meta_row)

        cs.addLayout(info_box); cs.addStretch(1)
        self._root.addWidget(self.card_selected)

        # ===== Chart Card =====
        chart_card = _Card()
        chart_card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        cc = QVBoxLayout(chart_card); cc.setContentsMargins(16, 16, 16, 16); cc.setSpacing(12)

        chart_head = QHBoxLayout(); chart_head.setSpacing(8)
        left = QVBoxLayout(); left.setSpacing(2)
        self.chart_title = QLabel("Price comparison — "); self.chart_title.setStyleSheet("font-size:16px; font-weight:600; color:#111827;")
        self.chart_sub = QLabel("0 items sorted by price"); self.chart_sub.setStyleSheet("font-size:12px; color:#6b7280;")
        left.addWidget(self.chart_title); left.addWidget(self.chart_sub)
        right = QHBoxLayout(); right.setSpacing(6)
        info_dot = QLabel(); info_dot.setFixedSize(10,10); info_dot.setStyleSheet("background:#111827; opacity:0.6; border-radius:5px;")
        info_txt = QLabel("Selected item highlighted in blue"); info_txt.setStyleSheet("font-size:12px; color:#4b5563;")
        right.addWidget(info_dot); right.addWidget(info_txt)
        chart_head.addLayout(left); chart_head.addStretch(1); chart_head.addLayout(right)
        cc.addLayout(chart_head)

        # chart + view
        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setBackgroundBrush(QBrush(QColor("#ffffff")))

        self.chart_view = QChartView(self.chart)
        self.chart_view.setMinimumHeight(460)
        self.chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # רספונסיבי
        cc.addWidget(self.chart_view, 1)

        # legend
        legend_row = QHBoxLayout(); legend_row.setSpacing(18)
        dot_sel = QLabel(); dot_sel.setFixedSize(14, 14); dot_sel.setStyleSheet("background:#2563eb; border-radius:7px;")
        lb_sel = QLabel("Selected decor"); lb_sel.setStyleSheet("font-size:12px; color:#374151;")
        dot_oth = QLabel(); dot_oth.setFixedSize(14, 14); dot_oth.setStyleSheet("background:#e5e7eb; border-radius:7px;")
        lb_oth = QLabel("Other items"); lb_oth.setStyleSheet("font-size:12px; color:#374151;")
        legend_row.addWidget(dot_sel); legend_row.addWidget(lb_sel)
        legend_row.addSpacing(16)
        legend_row.addWidget(dot_oth); legend_row.addWidget(lb_oth)
        legend_row.addStretch(1)
        cc.addLayout(legend_row)

        self._root.addWidget(chart_card)

        # ===== Summary cards =====
        summary = QGridLayout(); summary.setHorizontalSpacing(16); summary.setVerticalSpacing(16)
        def make_stat(color: str, title: str) -> QFrame:
            f = _Card()
            fl = QVBoxLayout(f); fl.setContentsMargins(16, 14, 16, 14); fl.setSpacing(6)
            val = QLabel("—"); val.setObjectName("statVal"); val.setStyleSheet(f"font-size:22px; font-weight:800; color:{color};")
            cap = QLabel(title); cap.setStyleSheet("font-size:12px; color:#6b7280;")
            fl.addWidget(val); fl.addWidget(cap)
            return f
        self.stat_low  = make_stat("#2563eb", "Lowest price")
        self.stat_avg  = make_stat("#16a34a", "Average price")
        self.stat_high = make_stat("#ef4444", "Highest price")
        summary.addWidget(self.stat_low, 0, 0)
        summary.addWidget(self.stat_avg, 0, 1)
        summary.addWidget(self.stat_high, 0, 2)
        self._root.addLayout(summary)

    # ---------- public API ----------
    def render_chart(
            self,
            items: List[Dict[str, Any]],
            focus_id: Optional[int],
            category: Optional[str],
            focus_item: Optional[Dict[str, Any]] = None,
    ):
        items = list(items or [])
        if not items:
            return

        # Selected card
        if focus_item:
            self.sel_name.setText(focus_item.get("DecorName") or focus_item.get("Name") or "")
            self.sel_cat.setText(category or "")
            self.sel_price.setText(_fmt_currency(_calc_midprice(focus_item)))
        else:
            self.sel_name.setText("")
            self.sel_cat.setText(category or "")
            self.sel_price.setText("")

        # Data
        labels: List[str] = []
        values: List[float] = []
        focus_index: int = -1
        for idx, it in enumerate(items):
            nm = it.get("DecorName") or it.get("Name") or f"#{it.get('DecorId', idx+1)}"
            labels.append(_wrap_multiline(nm))
            values.append(_calc_midprice(it))
            if focus_id is not None and int(it.get("DecorId", -1)) == int(focus_id):
                focus_index = idx

        n = len(values)
        self.chart_title.setText(f"Price comparison — {category or ''}")
        self.chart_sub.setText(f"{n} items sorted by price")

        # Series (grey others + blue selected)
        self.chart.removeAllSeries()

        set_other = QBarSet("")
        set_other.append([v if i != focus_index else 0.0 for i, v in enumerate(values)])
        set_other.setColor(QColor("#e5e7eb")); set_other.setBorderColor(QColor("#e5e7eb"))

        set_sel = QBarSet("")
        set_sel.append([v if i == focus_index else 0.0 for i, v in enumerate(values)])
        set_sel.setColor(QColor("#2563eb")); set_sel.setBorderColor(QColor("#1d4ed8"))

        series = QStackedBarSeries()
        series.append(set_other); series.append(set_sel)

        # רוחב עמודות – יפה כברירת מחדל, מצטמצם כשאין מקום
        view_w = max(self.chart_view.width(), 1)
        series.setBarWidth(_ideal_bar_width_ratio(n, view_w))

        self.chart.addSeries(series)

        # Axes
        axis_x = QBarCategoryAxis()
        axis_x.append(labels)
        axis_x.setGridLineVisible(False)
        font_x = QFont(); font_x.setPointSize(10)
        axis_x.setLabelsFont(font_x)
        axis_x.setLabelsAngle(0)

        max_lines = max(lbl.count("\n") + 1 for lbl in labels)
        est_h = int(16 + (max_lines * 14) + 10)  # גובה מוערך לתוויות X

        axis_y = QValueAxis()
        axis_y.applyNiceNumbers()
        axis_y.setLabelFormat("%d")
        axis_y.setMinorTickCount(0)
        axis_y.setTitleText("Price (₪)")
        font_y = QFont(); font_y.setPointSize(10)
        axis_y.setLabelsFont(font_y)

        self.chart.setAxisX(axis_x, series)
        self.chart.setAxisY(axis_y, series)

        # >>> FIX: אין QMargins.adjusted ב-PySide6 – יוצרים מרג'ינס חדשים
        cur = self.chart.margins()
        self.chart.setMargins(QMargins(cur.left(), cur.top(), cur.right(), est_h))

        # Summary
        lo = min(values); hi = max(values)
        avg = sum(values) / max(1, len(values))
        self._set_stat(self.stat_low,  _fmt_currency(lo))
        self._set_stat(self.stat_avg,  _fmt_currency(avg))
        self._set_stat(self.stat_high, _fmt_currency(hi))

    # ---------- private ----------
    def _set_stat(self, card: QFrame, text: str):
        val = card.findChild(QLabel, "statVal")
        if val is None:
            val = card.findChildren(QLabel)[0]
        val.setText(text)

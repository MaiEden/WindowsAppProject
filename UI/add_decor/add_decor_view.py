"""
AddDecorView (full)
-------------------
- Complete form for adding a decoration.
- Inline error labels, error summary banner, and red highlight via QSS.
- Primary/Secondary buttons with object names for styling.

Notes:
- All ids (object names) are lowercase to match the QSS selectors.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Tuple, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox,
    QPushButton, QFrame, QFormLayout, QDoubleSpinBox, QMessageBox,
    QScrollArea, QTextEdit
)


def _lbl(text: str, obj: Optional[str] = None) -> QLabel:
    l = QLabel(text)
    if obj:
        l.setObjectName(obj)
    return l


class AddDecorView(QWidget):
    submitRequested = Signal()
    cancelRequested = Signal()
    priceChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Decoration")
        self.setLayoutDirection(Qt.LeftToRight)

        # === Scroll wrapper
        wrapper = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        scroll.setWidget(body)
        wrapper.addWidget(scroll)

        root = QVBoxLayout(body)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        # Error summary (top banner)
        self.error_summary = _lbl("", "error-summary")
        self.error_summary.setWordWrap(True)
        self.error_summary.setVisible(False)
        root.addWidget(self.error_summary)

        # Title
        title = _lbl("Decoration Details", "h1")
        root.addWidget(title)

        # === Form
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignTop | Qt.AlignLeft)
        form.setSpacing(8)

        # Fields
        self.name = QLineEdit()
        self.category = QComboBox()
        self.theme = QLineEdit()
        self.description = QTextEdit()
        self.description.setPlaceholderText("Optional description")

        self.indoor = QCheckBox("Indoor use")
        self.indoor.setChecked(True)
        self.requires_electricity = QCheckBox("Requires electricity")

        self._load_local_qss()

        # Prices
        def mk_price():
            s = QDoubleSpinBox()
            s.setRange(0.0, 999999.99)
            s.setDecimals(2)
            s.setSingleStep(10.0)
            s.valueChanged.connect(self.priceChanged)
            return s

        self.price_s = mk_price()
        self.price_m = mk_price()
        self.price_l = mk_price()
        self.delivery = mk_price()

        self.price_hint = _lbl("", "price-hint")

        # Supplier / Region
        self.region = QLineEdit()
        self.vendor = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.photo = QLineEdit()
        self.available = QCheckBox("Available")
        self.available.setChecked(True)

        # Map: key -> (widget, error_label)
        self._field_map: Dict[str, tuple] = {}

        def add_row(label_text: str, widget, key: str):
            lbl = _lbl(label_text)
            form.addRow(lbl, widget)
            err = _lbl("", None)
            err.setObjectName("field-error")
            err.setVisible(False)
            err.setWordWrap(True)
            # A spare row under the field for inline error
            form.addRow(QLabel(""), err)
            self._field_map[key] = (widget, err)

        # Required ones
        add_row("Name *", self.name, "DecorName")
        add_row("Category *", self.category, "Category")

        # Optional ones
        add_row("Theme", self.theme, "Theme")
        form.addRow(_lbl("Description", obj="section"), self.description)
        form.addRow(QLabel(""), QLabel(""))

        # Checkboxes
        form.addRow(_lbl("Setup Options", obj="section"), self.indoor)
        form.addRow(QLabel(""), self.requires_electricity)

        # Prices
        add_row("Price (Small)", self.price_s, "PriceSmall")
        add_row("Price (Medium)", self.price_m, "PriceMedium")
        add_row("Price (Large)", self.price_l, "PriceLarge")
        add_row("Delivery Fee", self.delivery, "DeliveryFee")
        form.addRow(QLabel(""), self.price_hint)

        # Supplier / Region
        add_row("Region", self.region, "Region")
        add_row("Vendor name", self.vendor, "VendorName")
        add_row("Phone", self.phone, "ContactPhone")
        add_row("Email", self.email, "ContactEmail")
        add_row("Photo URL", self.photo, "PhotoUrl")

        # Availability
        form.addRow(_lbl("Availability", obj="section"), self.available)

        root.addLayout(form)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        root.addWidget(sep)

        # Buttons
        actions = QHBoxLayout()
        actions.addStretch(1)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_submit = QPushButton("Create")
        self.btn_submit.setDefault(True)

        # Object names for QSS styling
        self.btn_submit.setObjectName("btn-primary")
        self.btn_cancel.setObjectName("btn-secondary")
        self.btn_submit.setMinimumHeight(36)
        self.btn_cancel.setMinimumHeight(36)

        actions.addWidget(self.btn_cancel)
        actions.addWidget(self.btn_submit)
        root.addLayout(actions)

        # Signals
        self.btn_cancel.clicked.connect(self.cancelRequested)
        self.btn_submit.clicked.connect(self.submitRequested)

        # Keep list of error-able widgets
        self._all_errorable_widgets = [w for (w, _e) in self._field_map.values()]

        # Initial state
        self.set_price_hint("")
        self.clear_errors()

    # ===== Presenter API =====

    def populate_categories(self, items):
        self.category.clear()
        self.category.addItems(items)

    def collect_form(self) -> Dict[str, Any]:
        return {
            "DecorName": self.name.text().strip() or None,
            "Category": self.category.currentText().strip() or None,
            "Theme": self.theme.text().strip() or None,
            "Description": self.description.toPlainText().strip() or None,
            "Indoor": bool(self.indoor.isChecked()),
            "RequiresElectricity": bool(self.requires_electricity.isChecked()),
            "PriceSmall": float(self.price_s.value()) or None,
            "PriceMedium": float(self.price_m.value()) or None,
            "PriceLarge": float(self.price_l.value()) or None,
            "DeliveryFee": float(self.delivery.value()) or None,
            "Region": self.region.text().strip() or None,
            "VendorName": self.vendor.text().strip() or None,
            "ContactPhone": self.phone.text().strip() or None,
            "ContactEmail": self.email.text().strip() or None,
            "PhotoUrl": self.photo.text().strip() or None,
            "Available": bool(self.available.isChecked()),
        }

    def get_prices(self) -> Tuple[float, float, float]:
        return (self.price_s.value(), self.price_m.value(), self.price_l.value())

    def set_price_hint(self, txt: str):
        self.price_hint.setText(txt)

    def show_error_summary(self, text: str):
        self.error_summary.setText(text)
        self.error_summary.setVisible(True)

    def show_success(self, text: str):
        QMessageBox.information(self, "Success", text)

    def show_error(self, text: str):
        QMessageBox.warning(self, "Error", text)

    def set_busy(self, busy: bool):
        # Disable/enable entire form
        for w in self.findChildren(QWidget):
            if w is self.error_summary:
                continue
            w.setEnabled(not busy)

    def reset_form(self):
        for key, (w, err) in self._field_map.items():
            from PySide6.QtWidgets import QLineEdit, QComboBox, QDoubleSpinBox, QCheckBox
            if isinstance(w, QLineEdit):
                w.clear()
            elif isinstance(w, QComboBox):
                if w.count() > 0:
                    w.setCurrentIndex(0)
            elif isinstance(w, QDoubleSpinBox):
                w.setValue(0.0)
            elif isinstance(w, QCheckBox):
                # keep default states
                pass
            err.setVisible(False)

        self.description.clear()
        self.indoor.setChecked(True)
        self.requires_electricity.setChecked(False)
        self.available.setChecked(True)
        self.set_price_hint("")
        self.clear_errors()
        self.error_summary.setVisible(False)

    # ===== Error highlighting =====

    def _set_error_state(self, widget, error: bool):
        widget.setProperty("error", error)
        # Re-apply QSS so the "[error=true]" rule kicks in
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def clear_errors(self):
        for w in self._all_errorable_widgets:
            self._set_error_state(w, False)
        for _key, (_w, err_label) in self._field_map.items():
            err_label.clear()
            err_label.setVisible(False)
        self.error_summary.setVisible(False)

    def apply_errors(self, error_map: Dict[str, str]):
        self.clear_errors()
        for key, msg in (error_map or {}).items():
            pair = self._field_map.get(key)
            if not pair:
                continue
            w, err_label = pair
            self._set_error_state(w, True)
            err_label.setText(msg)
            err_label.setVisible(True)

    def _load_local_qss(self):
        # נטען את add_decor.qss שיושב לצד הקובץ הזה
        qss_path = Path(__file__).resolve().parent / "add_decor.qss"
        if qss_path.exists():
            css = qss_path.read_text(encoding="utf-8")
            # מומלץ לתת שם אובייקט לשורש – לא חובה, אבל טוב לספציפיות
            if not self.objectName():
                self.setObjectName("add-decor-root")
            self.setStyleSheet(css)


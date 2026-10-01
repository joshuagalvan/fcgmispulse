from PySide6.QtCore import QDate, QTime, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from .. import choices
from ..async_utils import run_async
from .autocomplete_combobox import AutocompleteComboBox
from .multi_select_combobox import MultiSelectComboBox

_FIELD_MIN_WIDTH = 380
_FORM_MAX_WIDTH = 760


def _short_text_edit() -> QTextEdit:
    edit = QTextEdit()
    edit.setMaximumHeight(70)
    edit.setTabChangesFocus(True)
    return _wide(edit)


def _wide(widget):
    # QComboBox/QLineEdit/QDateEdit/QTimeEdit don't expand to fill the
    # form's field column on their own even with ExpandingFieldsGrow --
    # only widgets with an explicit Expanding horizontal policy do, which
    # is why every field needs this, not just the ones that looked narrow.
    widget.setMinimumWidth(_FIELD_MIN_WIDTH)
    policy = widget.sizePolicy()
    policy.setHorizontalPolicy(QSizePolicy.Expanding)
    widget.setSizePolicy(policy)
    return widget


class EntryForm(QWidget):
    saved = Signal(dict)
    status_message = Signal(str)

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self._entry_id: int | None = None
        self._version: int | None = None

        self.heading = QLabel("New Entry")
        self.heading.setObjectName("formHeading")

        self.date_edit = _wide(QDateEdit(QDate.currentDate()))
        self.date_edit.setCalendarPopup(True)

        self.location_type_combo = _wide(QComboBox())
        self.location_type_combo.addItems(choices.LOCATION_TYPES)
        self.location_type_combo.currentTextChanged.connect(self._on_location_type_changed)

        self.brand_combo = _wide(QComboBox())
        self.brand_combo.currentTextChanged.connect(self._reload_stores)

        self.store_department_combo = _wide(AutocompleteComboBox())
        self.reported_by_combo = _wide(AutocompleteComboBox())

        now = QTime.currentTime()
        self.time_sent_edit = QTimeEdit(now)
        self.time_received_edit = QTimeEdit(now)
        self.time_done_edit = QTimeEdit(now)
        self.time_done_checkbox = QCheckBox("Finished")
        self.time_done_checkbox.setChecked(True)
        self.time_done_checkbox.toggled.connect(self.time_done_edit.setEnabled)

        time_done_row = QWidget()
        time_done_layout = QHBoxLayout(time_done_row)
        time_done_layout.setContentsMargins(0, 0, 0, 0)
        time_done_layout.addWidget(self.time_done_edit)
        time_done_layout.addWidget(self.time_done_checkbox)

        self.mis_personnel_combo = _wide(MultiSelectComboBox())
        self.mis_personnel_combo.set_items(choices.MIS_PERSONNEL)

        self.problem_edit = _short_text_edit()
        self.findings_edit = _short_text_edit()
        self.action_taken_edit = _short_text_edit()

        self.remarks_combo = _wide(QComboBox())
        self.remarks_combo.addItems([""] + choices.REMARKS)

        self.task_combo = _wide(QComboBox())
        self.task_combo.addItems(choices.TASK)

        self.task_remarks_edit = _wide(QLineEdit())
        self.acknowledged_by_edit = _wide(QLineEdit())
        self.area_manager_combo = _wide(AutocompleteComboBox())

        self.type_combo = _wide(QComboBox())
        self.type_combo.addItems(choices.OWNERSHIP_TYPE)

        self.type_of_support_combo = _wide(QComboBox())
        self.type_of_support_combo.addItems(choices.TYPE_OF_SUPPORT)

        form = QFormLayout()
        form.setRowWrapPolicy(QFormLayout.DontWrapRows)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(10)
        form.addRow("Date", self.date_edit)
        form.addRow("Store or Department?", self.location_type_combo)
        self._brand_row_label = "Brand"
        form.addRow(self._brand_row_label, self.brand_combo)
        form.addRow("Store / Department", self.store_department_combo)
        form.addRow("Reported By", self.reported_by_combo)
        form.addRow("Time Sent", self.time_sent_edit)
        form.addRow("Time Received", self.time_received_edit)
        form.addRow("Time Done", time_done_row)
        form.addRow("MIS Personnel", self.mis_personnel_combo)
        form.addRow("Problem", self.problem_edit)
        form.addRow("Findings / Cause", self.findings_edit)
        form.addRow("Action Taken", self.action_taken_edit)
        form.addRow("Remarks", self.remarks_combo)
        form.addRow("Task", self.task_combo)
        form.addRow("Task Remarks", self.task_remarks_edit)
        form.addRow("Acknowledged By", self.acknowledged_by_edit)
        form.addRow("Area Manager / Head", self.area_manager_combo)
        form.addRow("Type", self.type_combo)
        form.addRow("Type of Support", self.type_of_support_combo)
        self._form = form

        self.save_button = QPushButton("Save Entry  (Ctrl+S)")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self._save)
        self.new_button = QPushButton("New Entry")
        self.new_button.clicked.connect(self.reset_form)

        buttons = QHBoxLayout()
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.new_button)
        buttons.addStretch(1)

        # Cap the form to a comfortable reading width rather than letting
        # every field sprawl edge-to-edge on a wide window -- but give it a
        # stretch factor too, or it would just shrink to its minimum size
        # instead of actually growing to fill that cap.
        content = QWidget()
        content.setMaximumWidth(_FORM_MAX_WIDTH)
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.heading)
        content_layout.addSpacing(6)
        content_layout.addLayout(form)
        content_layout.addSpacing(6)
        content_layout.addLayout(buttons)

        centered = QHBoxLayout()
        centered.addWidget(content, 1)
        centered.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.addLayout(centered)
        layout.addStretch(1)

        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._save)

        self._update_brand_visibility()
        self.reload_lookups()

    # ---- lookups ----

    def reload_lookups(self):
        run_async(self.client.brands, on_success=self._on_brands_loaded)
        run_async(self.client.area_managers, on_success=self.area_manager_combo.set_items)
        run_async(self.client.reported_by, "", on_success=self.reported_by_combo.set_items)

    def _on_brands_loaded(self, brands: list[str]):
        current = self.brand_combo.currentText()
        self.brand_combo.blockSignals(True)
        self.brand_combo.clear()
        self.brand_combo.addItems(brands)
        if current in brands:
            self.brand_combo.setCurrentText(current)
        self.brand_combo.blockSignals(False)
        self._reload_stores()

    def _on_location_type_changed(self, _location_type: str):
        self._update_brand_visibility()
        self._reload_stores()

    def _update_brand_visibility(self):
        is_store = self.location_type_combo.currentText() == "STORE"
        self._form.setRowVisible(self.brand_combo, is_store)

    def _reload_stores(self):
        location_type = self.location_type_combo.currentText()
        brand = self.brand_combo.currentText() if location_type == "STORE" else None
        if location_type == "STORE" and not brand:
            self.store_department_combo.set_items([])
            return
        run_async(
            self.client.locations,
            location_type,
            brand,
            on_success=self.store_department_combo.set_items,
        )

    # ---- populate for edit ----

    def load_entry(self, entry: dict):
        self._entry_id = entry["id"]
        self._version = entry["version"]
        self.heading.setText(f"Editing Entry #{entry['id']}")

        self.date_edit.setDate(QDate.fromString(entry["entry_date"], "yyyy-MM-dd"))
        self.location_type_combo.setCurrentText(entry["location_type"])
        self._update_brand_visibility()
        if entry.get("brand"):
            self.brand_combo.setCurrentText(entry["brand"])
        self.store_department_combo.setCurrentText(entry["store_department"])
        self.reported_by_combo.setCurrentText(entry["reported_by"])
        self.time_sent_edit.setTime(QTime.fromString(entry["time_sent"], "HH:mm:ss"))
        self.time_received_edit.setTime(QTime.fromString(entry["time_received"], "HH:mm:ss"))
        if entry.get("time_done"):
            self.time_done_checkbox.setChecked(True)
            self.time_done_edit.setTime(QTime.fromString(entry["time_done"], "HH:mm:ss"))
        else:
            self.time_done_checkbox.setChecked(False)
        self.mis_personnel_combo.set_checked_items(
            [p.strip() for p in entry["mis_personnel"].split(",") if p.strip()]
        )
        self.problem_edit.setPlainText(entry.get("problem") or "")
        self.findings_edit.setPlainText(entry.get("findings_cause") or "")
        self.action_taken_edit.setPlainText(entry.get("action_taken") or "")
        self.remarks_combo.setCurrentText(entry.get("remarks") or "")
        self.task_combo.setCurrentText(entry["task"])
        self.task_remarks_edit.setText(entry.get("task_remarks") or "")
        self.acknowledged_by_edit.setText(entry.get("acknowledged_by") or "")
        self.area_manager_combo.setCurrentText(entry.get("area_manager_head") or "")
        self.type_combo.setCurrentText(entry.get("type_") or "")
        self.type_of_support_combo.setCurrentText(entry.get("type_of_support") or "")

    def reset_form(self):
        self._entry_id = None
        self._version = None
        self.heading.setText("New Entry")

        keep_location_type = self.location_type_combo.currentText()
        keep_brand = self.brand_combo.currentText()
        keep_mis_personnel = self.mis_personnel_combo.checked_items()

        self.date_edit.setDate(QDate.currentDate())
        self.location_type_combo.setCurrentText(keep_location_type)
        self.brand_combo.setCurrentText(keep_brand)
        self.store_department_combo.setCurrentIndex(-1)
        self.store_department_combo.clearEditText()
        self.reported_by_combo.setCurrentIndex(-1)
        self.reported_by_combo.clearEditText()
        now = QTime.currentTime()
        self.time_sent_edit.setTime(now)
        self.time_received_edit.setTime(now)
        self.time_done_edit.setTime(now)
        self.time_done_checkbox.setChecked(True)
        self.mis_personnel_combo.set_checked_items(keep_mis_personnel)
        self.problem_edit.clear()
        self.findings_edit.clear()
        self.action_taken_edit.clear()
        self.remarks_combo.setCurrentIndex(0)
        self.task_combo.setCurrentIndex(0)
        self.task_remarks_edit.clear()
        self.acknowledged_by_edit.clear()
        self.area_manager_combo.setCurrentIndex(-1)
        self.area_manager_combo.clearEditText()
        self.type_combo.setCurrentIndex(0)
        self.type_of_support_combo.setCurrentIndex(0)
        self.store_department_combo.setFocus()

    # ---- save ----

    def _collect_payload(self) -> dict | None:
        store_department = self.store_department_combo.currentText().strip()
        reported_by = self.reported_by_combo.currentText().strip()
        problem = self.problem_edit.toPlainText().strip()
        location_type = self.location_type_combo.currentText()
        brand = self.brand_combo.currentText().strip() if location_type == "STORE" else None
        mis_personnel = ", ".join(self.mis_personnel_combo.checked_items())

        missing = []
        if not store_department:
            missing.append("Store / Department")
        if location_type == "STORE" and not brand:
            missing.append("Brand")
        if not reported_by:
            missing.append("Reported By")
        if not problem:
            missing.append("Problem")
        if not mis_personnel:
            missing.append("MIS Personnel")
        if missing:
            QMessageBox.warning(
                self, "Missing information", "Please fill in: " + ", ".join(missing)
            )
            return None

        return {
            "entry_date": self.date_edit.date().toString("yyyy-MM-dd"),
            "location_type": location_type,
            "brand": brand,
            "store_department": store_department,
            "reported_by": reported_by,
            "time_sent": self.time_sent_edit.time().toString("HH:mm:ss"),
            "time_received": self.time_received_edit.time().toString("HH:mm:ss"),
            "time_done": (
                self.time_done_edit.time().toString("HH:mm:ss")
                if self.time_done_checkbox.isChecked()
                else None
            ),
            "mis_personnel": mis_personnel,
            "problem": problem,
            "findings_cause": self.findings_edit.toPlainText().strip() or None,
            "action_taken": self.action_taken_edit.toPlainText().strip() or None,
            "remarks": self.remarks_combo.currentText() or None,
            "task": self.task_combo.currentText(),
            "task_remarks": self.task_remarks_edit.text().strip() or None,
            "acknowledged_by": self.acknowledged_by_edit.text().strip() or None,
            "area_manager_head": self.area_manager_combo.currentText().strip() or None,
            "type_": self.type_combo.currentText(),
            "type_of_support": self.type_of_support_combo.currentText(),
        }

    def _save(self):
        payload = self._collect_payload()
        if payload is None:
            return

        self.save_button.setEnabled(False)
        if self._entry_id is None:
            run_async(
                self.client.create_entry,
                payload,
                on_success=self._on_save_success,
                on_error=self._on_save_error,
            )
        else:
            payload["version"] = self._version
            run_async(
                self.client.update_entry,
                self._entry_id,
                payload,
                on_success=self._on_save_success,
                on_error=self._on_save_error,
            )

    def _on_save_success(self, entry: dict):
        self.save_button.setEnabled(True)
        self.status_message.emit(f"Saved entry #{entry['id']}.")
        self.saved.emit(entry)
        self.reset_form()
        # New free-text values (reported-by/area-manager) may have been
        # introduced by this save; refresh so they appear immediately.
        self.reload_lookups()

    def _on_save_error(self, message: str):
        self.save_button.setEnabled(True)
        QMessageBox.critical(self, "Could not save", message)

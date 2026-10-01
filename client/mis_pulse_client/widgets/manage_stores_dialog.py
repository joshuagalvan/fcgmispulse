from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..async_utils import run_async

_INACTIVE_ROLE = Qt.UserRole
_ID_ROLE = Qt.UserRole + 1


class _LookupManagerPanel(QWidget):
    """Manages one curated lookup list (Stores, Departments, or Area
    Managers). Stores are further scoped to a Brand, chosen at the top."""

    def __init__(self, client, kind: str, location_type: str | None, needs_brand: bool):
        super().__init__()
        self.client = client
        self.kind = kind
        self.location_type = location_type
        self.needs_brand = needs_brand
        self._current_brand: str | None = None

        layout = QVBoxLayout(self)

        if needs_brand:
            brand_row = QHBoxLayout()
            brand_row.addWidget(QLabel("Brand:"))
            self.brand_combo = QComboBox()
            self.brand_combo.setMinimumWidth(260)
            self.brand_combo.currentTextChanged.connect(self._on_brand_changed)
            brand_row.addWidget(self.brand_combo)
            brand_row.addStretch(1)
            layout.addLayout(brand_row)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget, 1)

        add_row = QHBoxLayout()
        self.new_value_edit = QLineEdit()
        self.new_value_edit.setPlaceholderText(f"New {kind} name...")
        self.new_value_edit.returnPressed.connect(self._add)
        add_button = QPushButton("Add")
        add_button.clicked.connect(self._add)
        add_row.addWidget(self.new_value_edit, 1)
        add_row.addWidget(add_button)
        layout.addLayout(add_row)

        action_row = QHBoxLayout()
        rename_button = QPushButton("Rename Selected")
        rename_button.clicked.connect(self._rename)
        self.toggle_button = QPushButton("Deactivate / Restore Selected")
        self.toggle_button.clicked.connect(self._toggle_active)
        action_row.addWidget(rename_button)
        action_row.addWidget(self.toggle_button)
        action_row.addStretch(1)
        layout.addLayout(action_row)

        if needs_brand:
            run_async(self.client.brands, on_success=self._on_brands_loaded)
        else:
            self.refresh()

    def _on_brands_loaded(self, brands: list[str]):
        self.brand_combo.addItems(brands)
        if brands:
            self._current_brand = brands[0]
            self.refresh()

    def _on_brand_changed(self, brand: str):
        self._current_brand = brand
        self.refresh()

    def refresh(self):
        run_async(self.client.manage_list, self.kind, on_success=self._on_loaded)

    def _on_loaded(self, rows: list[dict]):
        if self.needs_brand:
            rows = [r for r in rows if r.get("brand") == self._current_brand]
        self.list_widget.clear()
        for row in rows:
            label = row["value"] + ("  (inactive)" if not row["is_active"] else "")
            item = QListWidgetItem(label)
            item.setData(_ID_ROLE, row["id"])
            item.setData(_INACTIVE_ROLE, not row["is_active"])
            if not row["is_active"]:
                item.setForeground(Qt.gray)
            self.list_widget.addItem(item)

    def _selected_item(self) -> QListWidgetItem | None:
        items = self.list_widget.selectedItems()
        return items[0] if items else None

    def _add(self):
        value = self.new_value_edit.text().strip()
        if not value:
            return
        if self.needs_brand and not self._current_brand:
            QMessageBox.warning(self, "Pick a brand", "Choose a brand first.")
            return
        run_async(
            self.client.add_lookup,
            self.kind,
            value,
            self.location_type,
            self._current_brand if self.needs_brand else None,
            on_success=lambda _row: self._on_added(),
            on_error=lambda msg: QMessageBox.critical(self, "Could not add", msg),
        )

    def _on_added(self):
        self.new_value_edit.clear()
        self.refresh()

    def _rename(self):
        item = self._selected_item()
        if item is None:
            QMessageBox.information(self, "No selection", "Select an item first.")
            return
        current_text = item.text().replace("  (inactive)", "")
        new_value, ok = QInputDialog.getText(self, "Rename", "New name:", text=current_text)
        if not ok or not new_value.strip():
            return
        run_async(
            self.client.update_lookup,
            item.data(_ID_ROLE),
            value=new_value.strip(),
            on_success=lambda _row: self.refresh(),
            on_error=lambda msg: QMessageBox.critical(self, "Could not rename", msg),
        )

    def _toggle_active(self):
        item = self._selected_item()
        if item is None:
            QMessageBox.information(self, "No selection", "Select an item first.")
            return
        currently_inactive = item.data(_INACTIVE_ROLE)
        run_async(
            self.client.update_lookup,
            item.data(_ID_ROLE),
            is_active=bool(currently_inactive),
            on_success=lambda _row: self.refresh(),
            on_error=lambda msg: QMessageBox.critical(self, "Could not update", msg),
        )


class _SingleLookupDialog(QDialog):
    """A focused dialog managing just one curated list -- split out from a
    single tabbed dialog per request, so each is its own window/button
    rather than three tabs buried in one place."""

    def __init__(self, title: str, panel: _LookupManagerPanel, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(480, 600)

        layout = QVBoxLayout(self)
        layout.addWidget(panel)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)


class ManageStoresDialog(_SingleLookupDialog):
    def __init__(self, client, parent=None):
        panel = _LookupManagerPanel(client, kind="location", location_type="STORE", needs_brand=True)
        super().__init__("Manage Stores", panel, parent)


class ManageDepartmentsDialog(_SingleLookupDialog):
    def __init__(self, client, parent=None):
        panel = _LookupManagerPanel(
            client, kind="location", location_type="DEPARTMENT", needs_brand=False
        )
        super().__init__("Manage Departments", panel, parent)


class ManageAreaManagersDialog(_SingleLookupDialog):
    def __init__(self, client, parent=None):
        panel = _LookupManagerPanel(client, kind="area_manager", location_type=None, needs_brand=False)
        super().__init__("Manage Area Managers", panel, parent)

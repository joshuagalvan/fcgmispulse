import datetime as dt

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from .. import choices
from ..async_utils import run_async
from ..models.entries_table_model import EntriesTableModel


def _recent_months(count: int = 14) -> list[tuple[str, str]]:
    """Returns (value, label) pairs, e.g. ("2026-09", "September 2026"),
    newest first, starting from the current month."""
    today = dt.date.today()
    months = []
    y, m = today.year, today.month
    for _ in range(count):
        months.append((f"{y:04d}-{m:02d}", dt.date(y, m, 1).strftime("%B %Y")))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return months


class EntriesListView(QWidget):
    edit_requested = Signal(dict)
    status_message = Signal(str)

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search problem, store, reported by...")
        self.search_edit.returnPressed.connect(self.refresh)

        self.task_filter_combo = QComboBox()
        self.task_filter_combo.addItems(["All statuses"] + choices.TASK)
        self.task_filter_combo.currentIndexChanged.connect(self.refresh)

        self.refresh_button = QPushButton("Search")
        self.refresh_button.clicked.connect(self.refresh)

        filters = QHBoxLayout()
        filters.addWidget(self.search_edit, 1)
        filters.addWidget(self.task_filter_combo)
        filters.addWidget(self.refresh_button)

        self.model = EntriesTableModel()
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self._edit_selected)

        self.edit_button = QPushButton("Edit Selected")
        self.edit_button.clicked.connect(self._edit_selected)
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.clicked.connect(self._delete_selected)

        row_buttons = QHBoxLayout()
        row_buttons.addWidget(self.edit_button)
        row_buttons.addWidget(self.delete_button)
        row_buttons.addStretch(1)

        self.export_month_combo = QComboBox()
        for value, label in _recent_months():
            self.export_month_combo.addItem(label, value)
        self.export_button = QPushButton("Export to Excel...")
        self.export_button.setObjectName("primaryButton")
        self.export_button.clicked.connect(self._export)

        export_row = QHBoxLayout()
        export_row.addWidget(self.export_month_combo)
        export_row.addWidget(self.export_button)
        export_row.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addLayout(filters)
        layout.addWidget(self.table, 1)
        layout.addLayout(row_buttons)
        layout.addLayout(export_row)

        self.refresh()

    # ---- data loading ----

    def refresh(self):
        status = self.task_filter_combo.currentText()
        run_async(
            self.client.list_entries,
            search=self.search_edit.text().strip() or None,
            task=None if status == "All statuses" else status,
            limit=300,
            on_success=self._on_loaded,
            on_error=lambda msg: self.status_message.emit(f"Could not load entries: {msg}"),
        )

    def _on_loaded(self, data: dict):
        self.model.set_rows(data["items"])
        self.table.resizeColumnsToContents()
        self.status_message.emit(f"{data['total']} entr{'y' if data['total'] == 1 else 'ies'}.")

    def _selected_entry(self) -> dict | None:
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return None
        return self.model.entry_at(indexes[0].row())

    def _edit_selected(self):
        entry = self._selected_entry()
        if entry is None:
            QMessageBox.information(self, "No selection", "Select an entry first.")
            return
        self.edit_requested.emit(entry)

    def _delete_selected(self):
        entry = self._selected_entry()
        if entry is None:
            QMessageBox.information(self, "No selection", "Select an entry first.")
            return
        confirm = QMessageBox.question(
            self,
            "Delete entry",
            f"Delete entry #{entry['id']} ({entry['store_department']})?",
        )
        if confirm != QMessageBox.Yes:
            return
        run_async(
            self.client.delete_entry,
            entry["id"],
            on_success=lambda _=None: self.refresh(),
            on_error=lambda msg: QMessageBox.critical(self, "Could not delete", msg),
        )

    # ---- export ----

    def _export(self):
        month_value = self.export_month_combo.currentData()
        month_label = self.export_month_combo.currentText()
        default_name = f"MIS SUPPORT SUMMARY REPORT - {month_label.upper()}.xlsx"
        path, _ = QFileDialog.getSaveFileName(self, "Save report as", default_name, "Excel Files (*.xlsx)")
        if not path:
            return

        self.export_button.setEnabled(False)
        self.export_button.setText("Exporting...")
        run_async(
            self.client.export,
            month_value,
            path,
            on_success=self._on_export_success,
            on_error=self._on_export_error,
        )

    def _on_export_success(self, path: str):
        self.export_button.setEnabled(True)
        self.export_button.setText("Export to Excel...")
        QMessageBox.information(self, "Export complete", f"Saved to:\n{path}")

    def _on_export_error(self, message: str):
        self.export_button.setEnabled(True)
        self.export_button.setText("Export to Excel...")
        QMessageBox.critical(self, "Export failed", message)

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QComboBox, QLineEdit


class MultiSelectComboBox(QComboBox):
    """A dropdown where each item has a checkbox and multiple can be
    selected at once (e.g. two MIS Personnel handling one ticket together).
    The closed combobox shows a comma-joined summary, matching how the
    original report has always recorded a multi-person ticket."""

    selectionChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = QStandardItemModel(self)
        self.setModel(self._model)
        self.view().pressed.connect(self._on_item_pressed)

        # Read-only line edit so it shows our joined summary, not a
        # selected item's raw text, while still looking/sizing like a
        # normal editable combo field.
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().installEventFilter(self)

    def set_items(self, items: list[str]):
        checked = set(self.checked_items())
        self._model.clear()
        for text in items:
            item = QStandardItem(text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setData(
                Qt.Checked if text in checked else Qt.Unchecked, Qt.CheckStateRole
            )
            self._model.appendRow(item)
        self._refresh_display()

    def checked_items(self) -> list[str]:
        result = []
        for row in range(self._model.rowCount()):
            item = self._model.item(row)
            if item.checkState() == Qt.Checked:
                result.append(item.text())
        return result

    def set_checked_items(self, values: list[str]):
        wanted = set(values)
        for row in range(self._model.rowCount()):
            item = self._model.item(row)
            item.setCheckState(Qt.Checked if item.text() in wanted else Qt.Unchecked)
        self._refresh_display()

    def clear_selection(self):
        self.set_checked_items([])

    def _on_item_pressed(self, index):
        item = self._model.itemFromIndex(index)
        item.setCheckState(Qt.Unchecked if item.checkState() == Qt.Checked else Qt.Checked)
        self._refresh_display()
        self.selectionChanged.emit()

    def _refresh_display(self):
        self.lineEdit().setText(", ".join(self.checked_items()))

    def eventFilter(self, obj, event):
        # Clicking the read-only line edit should open the popup, same as
        # clicking the dropdown arrow.
        if obj is self.lineEdit() and event.type() == event.Type.MouseButtonPress:
            self.showPopup()
            return True
        return super().eventFilter(obj, event)

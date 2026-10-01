from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QColor, QPalette, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QComboBox

from ..theme import CARD, TEXT


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

        # A plain QComboBox closes its popup the instant an item is
        # activated, which for a multi-select combo means every single
        # checkbox click immediately closes it again. Filtering the view's
        # viewport directly and consuming the release event ourselves is
        # the standard way around that -- toggling via the `pressed` signal
        # alone still lets Qt's own activation-close logic run afterward.
        self.view().viewport().installEventFilter(self)

        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        # A read-only QLineEdit renders with the palette's *Disabled* text
        # color on some native styles even though it isn't actually
        # disabled -- a stylesheet `color:` rule alone didn't fully
        # override that (it washed out to a near-invisible gray). Setting
        # the palette directly, for every color group, is the forceful fix.
        palette = self.lineEdit().palette()
        for group in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
            palette.setColor(group, QPalette.Text, QColor(TEXT))
            palette.setColor(group, QPalette.Base, QColor(CARD))
        self.lineEdit().setPalette(palette)
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

    def _toggle_row(self, row: int):
        item = self._model.item(row)
        if item is None:
            return
        item.setCheckState(Qt.Unchecked if item.checkState() == Qt.Checked else Qt.Checked)
        self._refresh_display()
        self.selectionChanged.emit()

    def _refresh_display(self):
        self.lineEdit().setText(", ".join(self.checked_items()))

    def eventFilter(self, obj, event):
        if obj is self.view().viewport() and event.type() == QEvent.Type.MouseButtonRelease:
            index = self.view().indexAt(event.pos())
            if index.isValid():
                self._toggle_row(index.row())
            return True  # swallow it so Qt doesn't also close the popup
        if obj is self.lineEdit() and event.type() == QEvent.Type.MouseButtonPress:
            self.showPopup()
            return True
        return super().eventFilter(obj, event)

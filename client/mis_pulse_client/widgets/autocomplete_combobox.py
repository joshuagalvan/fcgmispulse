from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import QComboBox, QCompleter


class AutocompleteComboBox(QComboBox):
    """An editable combobox with contains-anywhere, case-insensitive
    autocomplete -- used for fields backed by a growable or curated lookup
    list (Store/Department, Reported By, Area Manager/Head).

    Clicking into the field immediately shows the full searchable popup
    (not just after you start typing), and the popup is generously sized
    so long store names aren't clipped even when the field itself is
    narrower than the widest entry.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.setMinimumWidth(320)

        self._completer = QCompleter(self)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchContains)
        self._completer.setCompletionMode(QCompleter.PopupCompletion)
        self._completer.setModel(self.model())
        self._completer.setMaxVisibleItems(20)
        self.setCompleter(self._completer)
        if self._completer.popup() is not None:
            self._completer.popup().setMinimumWidth(360)

        self.lineEdit().installEventFilter(self)

    def set_items(self, items: list[str], keep_current: bool = True):
        current = self.currentText() if keep_current else ""
        self.blockSignals(True)
        self.clear()
        self.addItems(items)
        self._completer.setModel(self.model())
        # QComboBox auto-selects index 0 once addItems() makes the list
        # non-empty; without this, a freshly loaded/reset field would show
        # an arbitrary (alphabetically-first) value pre-selected instead of
        # staying blank, risking a ticket silently saved against the wrong
        # store/person if nobody notices.
        self.setCurrentIndex(-1)
        self.setEditText(current)
        self.blockSignals(False)

    def eventFilter(self, obj, event):
        if obj is self.lineEdit() and event.type() == QEvent.Type.MouseButtonPress:
            if not self._completer.popup().isVisible():
                self._completer.setCompletionPrefix(self.lineEdit().text())
                self._completer.complete()
        return super().eventFilter(obj, event)

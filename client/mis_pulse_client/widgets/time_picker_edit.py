from PySide6.QtCore import QTime, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QToolButton,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)


class TimePickerEdit(QWidget):
    """A QTimeEdit (still directly typeable/spinnable, unchanged) plus a
    button that opens a scrollable list of times in 15-minute steps, so a
    common time is one click instead of several spinner nudges."""

    def __init__(self, time: QTime | None = None, parent=None):
        super().__init__(parent)
        self.time_edit = QTimeEdit(time or QTime.currentTime())
        policy = self.time_edit.sizePolicy()
        policy.setHorizontalPolicy(QSizePolicy.Expanding)
        self.time_edit.setSizePolicy(policy)

        self.picker_button = QToolButton()
        self.picker_button.setText("▼")
        self.picker_button.setToolTip("Pick a time")
        self.picker_button.clicked.connect(self._show_popup)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(self.time_edit, 1)
        layout.addWidget(self.picker_button)

        self._popup: QFrame | None = None

    def time(self) -> QTime:
        return self.time_edit.time()

    def setTime(self, value: QTime):
        self.time_edit.setTime(value)

    def _show_popup(self):
        popup = QFrame(self, Qt.Popup)
        popup.setObjectName("timePickerPopup")
        popup.setFrameShape(QFrame.StyledPanel)

        list_widget = QListWidget(popup)
        current = self.time_edit.time()
        closest_row = 0
        best_diff = None
        row = 0
        for hour in range(24):
            for minute in (0, 15, 30, 45):
                t = QTime(hour, minute)
                item = QListWidgetItem(t.toString("h:mm AP"))
                item.setData(Qt.UserRole, t)
                list_widget.addItem(item)
                diff = abs(QTime(0, 0).secsTo(t) - QTime(0, 0).secsTo(current))
                if best_diff is None or diff < best_diff:
                    best_diff = diff
                    closest_row = row
                row += 1

        list_widget.setCurrentRow(closest_row)
        list_widget.itemClicked.connect(lambda item: self._pick(item, popup))

        layout = QVBoxLayout(popup)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.addWidget(list_widget)
        popup.resize(140, 260)

        pos = self.picker_button.mapToGlobal(self.picker_button.rect().bottomRight())
        popup.move(pos.x() - popup.width(), pos.y())
        popup.show()
        list_widget.scrollToItem(list_widget.item(closest_row), QListWidget.PositionAtCenter)
        self._popup = popup

    def _pick(self, item: QListWidgetItem, popup: QFrame):
        self.time_edit.setTime(item.data(Qt.UserRole))
        popup.close()

from PySide6.QtCore import QEvent, QObject


class _WheelGuard(QObject):
    """QComboBox/QDateEdit/QTimeEdit/QSpinBox all change their value on a
    bare mouse-wheel scroll by default, even without focus -- so scrolling
    the page past one of these fields silently changes whatever it's set
    to instead of just scrolling by. Only let the wheel act once the field
    actually has focus (i.e. was clicked into first), same as most modern
    forms; otherwise let the event bubble up so the page scrolls instead."""

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Wheel and not obj.hasFocus():
            event.ignore()
            return True
        return super().eventFilter(obj, event)


_guard = _WheelGuard()


def no_wheel_unless_focused(widget):
    # QComboBox/QDateEdit/QTimeEdit already accept click-to-focus by
    # default (StrongFocus), so no focus-policy change is needed here.
    widget.installEventFilter(_guard)
    return widget

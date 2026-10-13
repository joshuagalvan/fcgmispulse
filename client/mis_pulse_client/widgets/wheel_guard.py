from PySide6.QtCore import QEvent, QObject, Qt


class _WheelBlocker(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Wheel:
            event.ignore()  # filtered *and* ignored: Qt hands it to the parent, so the page scrolls
            return True
        return super().eventFilter(obj, event)


_blocker = _WheelBlocker()


def block_wheel(widget):
    """Stop the mouse wheel changing a combo/date/time field's value; scroll the page instead."""
    # Default on Windows is WheelFocus, which grabs focus on scroll before any event filter runs.
    widget.setFocusPolicy(Qt.StrongFocus)
    widget.installEventFilter(_blocker)
    return widget

"""Runs a blocking callable (an API call) off the GUI thread, delivering the
result or error back via Qt signals. Every network call in this app must go
through run_async, never called directly from a slot, or the UI would freeze
for the duration of the request."""

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot


class _WorkerSignals(QObject):
    success = Signal(object)
    error = Signal(str)


class _Worker(QRunnable):
    def __init__(self, fn, args, kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = _WorkerSignals()

    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:  # noqa: BLE001 - surfaced to the UI, not swallowed
            self.signals.error.emit(str(e))
        else:
            self.signals.success.emit(result)


def run_async(fn, *args, on_success=None, on_error=None, **kwargs) -> _Worker:
    worker = _Worker(fn, args, kwargs)
    if on_success:
        worker.signals.success.connect(on_success)
    if on_error:
        worker.signals.error.connect(on_error)
    QThreadPool.globalInstance().start(worker)
    return worker

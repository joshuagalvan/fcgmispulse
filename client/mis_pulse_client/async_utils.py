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


_in_flight: set = set()  # keeps workers alive for the duration of the task --
# see run_async's docstring note below for why this exists.


def run_async(fn, *args, on_success=None, on_error=None, **kwargs) -> _Worker:
    """QThreadPool owns the C++ side of a QRunnable, but nothing keeps the
    *Python* wrapper (or its .signals QObject) alive once run_async returns,
    since callers never hold onto the returned worker. Python's GC can and
    does collect it before the background thread finishes, which silently
    drops the success/error signal instead of raising anything -- the
    callback just never fires. Tracking in-flight workers here keeps a
    strong reference until they're done."""
    worker = _Worker(fn, args, kwargs)
    _in_flight.add(worker)

    def _cleanup():
        _in_flight.discard(worker)

    if on_success:
        worker.signals.success.connect(on_success)
    if on_error:
        worker.signals.error.connect(on_error)
    worker.signals.success.connect(_cleanup)
    worker.signals.error.connect(_cleanup)
    QThreadPool.globalInstance().start(worker)
    return worker

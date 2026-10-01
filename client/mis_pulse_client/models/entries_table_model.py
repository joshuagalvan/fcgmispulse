from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

_COLUMNS = [
    ("entry_date", "Date"),
    ("brand", "Brand"),
    ("store_department", "Store / Department"),
    ("reported_by", "Reported By"),
    ("mis_personnel", "MIS Personnel"),
    ("problem", "Problem"),
    ("task", "Task"),
    ("duration_seconds", "Duration"),
    ("type_of_support", "Type of Support"),
]


def _duration_display(seconds: int | None) -> str:
    if seconds is None:
        return ""
    sign = "-" if seconds < 0 else ""
    seconds = abs(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{sign}{hours}:{minutes:02d}:{secs:02d}"


class EntriesTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: list[dict] = []

    def set_rows(self, rows: list[dict]):
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def entry_at(self, row: int) -> dict:
        return self._rows[row]

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(_COLUMNS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole or orientation != Qt.Horizontal:
            return None
        return _COLUMNS[section][1]

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        row = self._rows[index.row()]
        key = _COLUMNS[index.column()][0]
        value = row.get(key)
        if key == "duration_seconds":
            return _duration_display(value)
        if key == "problem" and value and len(value) > 80:
            return value[:77] + "..."
        return value or ""

import datetime as dt
import json

from sqlalchemy.orm import Session

from .. import models
from ..timeutil import utcnow

_TRACKED_FIELDS = [
    "entry_date",
    "location_type",
    "brand",
    "store_department",
    "reported_by",
    "time_sent",
    "time_received",
    "time_done",
    "mis_personnel",
    "problem",
    "findings_cause",
    "action_taken",
    "remarks",
    "task",
    "task_remarks",
    "acknowledged_by",
    "area_manager_head",
    "type_",
    "type_of_support",
    "is_deleted",
]


def snapshot(entry: models.Entry) -> dict:
    out = {}
    for field in _TRACKED_FIELDS:
        value = getattr(entry, field)
        if isinstance(value, (dt.date, dt.time, dt.datetime)):
            value = value.isoformat()
        out[field] = value
    return out


def record_change(db: Session, entry: models.Entry, changed_by_id: int) -> None:
    """Snapshot the entry's state as it is *right now*, before the caller
    applies new field values, so entry_history holds the prior version."""
    db.add(
        models.EntryHistory(
            entry_id=entry.id,
            changed_by=changed_by_id,
            changed_at=utcnow(),
            snapshot_json=json.dumps(snapshot(entry)),
        )
    )

from sqlalchemy.orm import Session

from .. import models


def ensure_reported_by(db: Session, value: str) -> None:
    """Grow-on-write: add a new Reported By name to the autocomplete pool if
    it isn't already there. Caller is responsible for committing."""
    value = value.strip()
    if not value:
        return
    exists = (
        db.query(models.Lookup)
        .filter(models.Lookup.kind == "reported_by", models.Lookup.value == value)
        .first()
    )
    if exists is None:
        db.add(models.Lookup(kind="reported_by", location_type=None, value=value))

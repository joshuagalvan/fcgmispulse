import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..deps import get_current_user
from ..services import history
from ..services.lookups import ensure_reported_by

router = APIRouter(prefix="/entries", tags=["entries"])


def _duration_seconds(entry: models.Entry) -> int | None:
    if entry.time_done is None:
        return None
    anchor = dt.date(2000, 1, 1)
    delta = dt.datetime.combine(anchor, entry.time_done) - dt.datetime.combine(
        anchor, entry.time_received
    )
    return int(delta.total_seconds())


def _to_out(db: Session, entry: models.Entry) -> schemas.EntryOut:
    created_by = db.get(models.User, entry.created_by)
    updated_by = db.get(models.User, entry.updated_by) if entry.updated_by else None
    base = schemas.EntryBase.model_validate(entry).model_dump()
    return schemas.EntryOut(
        **base,
        id=entry.id,
        created_by=entry.created_by,
        created_by_name=created_by.display_name if created_by else "?",
        updated_by=entry.updated_by,
        updated_by_name=updated_by.display_name if updated_by else None,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
        version=entry.version,
        duration_seconds=_duration_seconds(entry),
    )


@router.get("", response_model=schemas.EntryListResponse)
def list_entries(
    date_from: dt.date | None = None,
    date_to: dt.date | None = None,
    store_department: str | None = None,
    mis_personnel: str | None = None,
    task: str | None = None,
    search: str | None = None,
    limit: int = Query(default=100, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    q = db.query(models.Entry).filter(models.Entry.is_deleted.is_(False))
    if date_from:
        q = q.filter(models.Entry.entry_date >= date_from)
    if date_to:
        q = q.filter(models.Entry.entry_date <= date_to)
    if store_department:
        q = q.filter(models.Entry.store_department == store_department)
    if mis_personnel:
        q = q.filter(models.Entry.mis_personnel == mis_personnel)
    if task:
        q = q.filter(models.Entry.task == task)
    if search:
        like = f"%{search}%"
        q = q.filter(
            or_(
                models.Entry.problem.ilike(like),
                models.Entry.findings_cause.ilike(like),
                models.Entry.action_taken.ilike(like),
                models.Entry.reported_by.ilike(like),
                models.Entry.store_department.ilike(like),
            )
        )

    total = q.count()
    rows = (
        q.order_by(models.Entry.entry_date.desc(), models.Entry.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return schemas.EntryListResponse(total=total, items=[_to_out(db, r) for r in rows])


@router.post("", response_model=schemas.EntryOut, status_code=status.HTTP_201_CREATED)
def create_entry(
    body: schemas.EntryCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    entry = models.Entry(**body.model_dump(), created_by=user.id)
    ensure_reported_by(db, body.reported_by)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _to_out(db, entry)


@router.get("/{entry_id}", response_model=schemas.EntryOut)
def get_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    entry = db.get(models.Entry, entry_id)
    if entry is None or entry.is_deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Entry not found")
    return _to_out(db, entry)


@router.put("/{entry_id}", response_model=schemas.EntryOut)
def update_entry(
    entry_id: int,
    body: schemas.EntryUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    entry = db.get(models.Entry, entry_id)
    if entry is None or entry.is_deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Entry not found")
    if entry.version != body.version:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "This entry was changed by someone else. Reload it and try again.",
        )

    history.record_change(db, entry, changed_by_id=user.id)

    for field, value in body.model_dump(exclude={"version"}).items():
        setattr(entry, field, value)
    entry.updated_by = user.id
    entry.version += 1
    ensure_reported_by(db, body.reported_by)

    db.commit()
    db.refresh(entry)
    return _to_out(db, entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    entry = db.get(models.Entry, entry_id)
    if entry is None or entry.is_deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Entry not found")

    history.record_change(db, entry, changed_by_id=user.id)
    entry.is_deleted = True
    entry.updated_by = user.id
    entry.version += 1
    db.commit()

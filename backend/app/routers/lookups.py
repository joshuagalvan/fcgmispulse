from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..deps import get_current_user, require_admin

router = APIRouter(prefix="/lookups", tags=["lookups"])


@router.get("/brands", response_model=list[str])
def brands(db: Session = Depends(get_db), _user: models.User = Depends(get_current_user)):
    rows = (
        db.query(models.Lookup)
        .filter(models.Lookup.kind == "brand", models.Lookup.is_active.is_(True))
        .order_by(models.Lookup.value)
        .all()
    )
    return [r.value for r in rows]


@router.get("/locations", response_model=list[str])
def locations(
    location_type: str,
    brand: str | None = None,
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    q = db.query(models.Lookup).filter(
        models.Lookup.kind == "location",
        models.Lookup.location_type == location_type,
        models.Lookup.is_active.is_(True),
    )
    if brand:
        q = q.filter(models.Lookup.brand == brand)
    rows = q.order_by(models.Lookup.value).all()
    return [r.value for r in rows]


@router.get("/area-managers", response_model=list[str])
def area_managers(
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    rows = (
        db.query(models.Lookup)
        .filter(models.Lookup.kind == "area_manager", models.Lookup.is_active.is_(True))
        .order_by(models.Lookup.value)
        .all()
    )
    return [r.value for r in rows]


@router.get("/reported-by", response_model=list[str])
def reported_by(
    q: str = "",
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    query = db.query(models.Lookup).filter(models.Lookup.kind == "reported_by")
    if q:
        query = query.filter(models.Lookup.value.ilike(f"%{q}%"))
    # No q: the client preloads the full pool for local autocomplete rather
    # than querying per keystroke, so this needs to return "all", not a
    # small page -- a plain limit as a sanity ceiling, not real pagination.
    rows = query.order_by(models.Lookup.value).limit(5000).all()
    return [r.value for r in rows]


# ---- admin management (add/edit/deactivate curated lists) ----


@router.get("/manage", response_model=list[schemas.LookupOut])
def manage_list(
    kind: str,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    """Everything for a kind, including inactive rows, for the admin screen."""
    rows = (
        db.query(models.Lookup)
        .filter(models.Lookup.kind == kind)
        .order_by(models.Lookup.brand, models.Lookup.value)
        .all()
    )
    return rows


@router.post("", response_model=schemas.LookupOut)
def add_curated_lookup(
    body: schemas.LookupCreate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    value = body.value.strip()
    existing = (
        db.query(models.Lookup)
        .filter(
            models.Lookup.kind == body.kind,
            models.Lookup.location_type == body.location_type,
            models.Lookup.brand == body.brand,
            models.Lookup.value == value,
        )
        .first()
    )
    if existing:
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        return existing

    row = models.Lookup(
        kind=body.kind, location_type=body.location_type, brand=body.brand, value=value
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/{lookup_id}", response_model=schemas.LookupOut)
def update_lookup(
    lookup_id: int,
    body: schemas.LookupUpdate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    row = db.get(models.Lookup, lookup_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    if body.value is not None:
        row.value = body.value.strip()
    if body.brand is not None:
        row.brand = body.brand
    if body.is_active is not None:
        row.is_active = body.is_active
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{lookup_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_lookup(
    lookup_id: int,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    """Removes it from dropdowns going forward (soft delete) -- existing
    entries already saved with this value are plain text and unaffected."""
    row = db.get(models.Lookup, lookup_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    row.is_active = False
    db.commit()

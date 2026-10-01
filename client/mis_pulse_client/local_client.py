"""Single-user, no-server data access -- talks to a local SQLite file
directly instead of a backend over HTTP."""

import calendar
import datetime as dt

from mis_pulse_export import EntryRow, build_monthly_workbook
from mis_pulse_export.recalc import recalc
from sqlalchemy import or_

from . import choices
from .local_db import store_data
from .local_db.db import Base, SessionLocal, engine
from .local_db.models import Entry, Lookup
from .local_db.seed_data import SEED_ENTRIES, SEED_LOOKUPS


def _parse_date(s):
    return dt.date.fromisoformat(s)


def _parse_time(s):
    return dt.time.fromisoformat(s) if s else None


class LocalError(Exception):
    pass


class LocalClient:
    def __init__(self):
        Base.metadata.create_all(bind=engine)
        self._ensure_seeded()

    # ---- first-run seeding ----

    def _ensure_seeded(self):
        db = SessionLocal()
        try:
            if db.query(Lookup).count() == 0:
                for brand, stores in store_data.STORES_BY_BRAND.items():
                    db.add(Lookup(kind="brand", value=brand))
                    for name in stores:
                        db.add(
                            Lookup(
                                kind="location", location_type="STORE", brand=brand, value=name
                            )
                        )
                for row in SEED_LOOKUPS:
                    db.add(
                        Lookup(
                            kind=row["kind"],
                            location_type=row["location_type"],
                            brand=row["brand"],
                            value=row["value"],
                        )
                    )
                db.commit()

            if db.query(Entry).count() == 0:
                for row in SEED_ENTRIES:
                    db.add(
                        Entry(
                            entry_date=_parse_date(row["entry_date"]),
                            location_type=row["location_type"],
                            brand=row["brand"],
                            store_department=row["store_department"],
                            reported_by=row["reported_by"],
                            time_sent=_parse_time(row["time_sent"]),
                            time_received=_parse_time(row["time_received"]),
                            time_done=_parse_time(row["time_done"]),
                            mis_personnel=row["mis_personnel"],
                            problem=row["problem"],
                            findings_cause=row["findings_cause"],
                            action_taken=row["action_taken"],
                            remarks=row["remarks"],
                            task=row["task"],
                            task_remarks=row["task_remarks"],
                            acknowledged_by=row["acknowledged_by"],
                            area_manager_head=row["area_manager_head"],
                            type_=row["type_"],
                            type_of_support=row["type_of_support"],
                        )
                    )
                db.commit()
        finally:
            db.close()

    # ---- entries ----

    def _duration_seconds(self, entry: Entry) -> int | None:
        if entry.time_done is None:
            return None
        anchor = dt.date(2000, 1, 1)
        delta = dt.datetime.combine(anchor, entry.time_done) - dt.datetime.combine(
            anchor, entry.time_received
        )
        return int(delta.total_seconds())

    def _to_dict(self, e: Entry) -> dict:
        return {
            "id": e.id,
            "entry_date": e.entry_date.isoformat(),
            "location_type": e.location_type,
            "brand": e.brand,
            "store_department": e.store_department,
            "reported_by": e.reported_by,
            "time_sent": e.time_sent.isoformat(),
            "time_received": e.time_received.isoformat(),
            "time_done": e.time_done.isoformat() if e.time_done else None,
            "mis_personnel": e.mis_personnel,
            "problem": e.problem,
            "findings_cause": e.findings_cause,
            "action_taken": e.action_taken,
            "remarks": e.remarks,
            "task": e.task,
            "task_remarks": e.task_remarks,
            "acknowledged_by": e.acknowledged_by,
            "area_manager_head": e.area_manager_head,
            "type_": e.type_,
            "type_of_support": e.type_of_support,
            "version": e.version,
            "duration_seconds": self._duration_seconds(e),
        }

    def _validate(self, payload: dict):
        errors = []
        if payload["location_type"] not in choices.LOCATION_TYPES:
            errors.append("location_type")
        if payload["location_type"] == "STORE" and not payload.get("brand"):
            errors.append("brand (required for a Store)")
        for value in payload["mis_personnel"].split(","):
            if value.strip() not in choices.MIS_PERSONNEL:
                errors.append(f"mis_personnel: {value.strip()!r}")
        if payload.get("remarks") and payload["remarks"] not in choices.REMARKS:
            errors.append("remarks")
        if payload["task"] not in choices.TASK:
            errors.append("task")
        if payload["type_"] not in choices.OWNERSHIP_TYPE:
            errors.append("type_")
        if payload["type_of_support"] not in choices.TYPE_OF_SUPPORT:
            errors.append("type_of_support")
        if errors:
            raise LocalError("Invalid value(s): " + ", ".join(errors))

    def list_entries(self, **params) -> dict:
        db = SessionLocal()
        try:
            q = db.query(Entry).filter(Entry.is_deleted.is_(False))
            if params.get("date_from"):
                q = q.filter(Entry.entry_date >= _parse_date(params["date_from"]))
            if params.get("date_to"):
                q = q.filter(Entry.entry_date <= _parse_date(params["date_to"]))
            if params.get("store_department"):
                q = q.filter(Entry.store_department == params["store_department"])
            if params.get("mis_personnel"):
                q = q.filter(Entry.mis_personnel == params["mis_personnel"])
            if params.get("task"):
                q = q.filter(Entry.task == params["task"])
            if params.get("search"):
                like = f"%{params['search']}%"
                q = q.filter(
                    or_(
                        Entry.problem.ilike(like),
                        Entry.findings_cause.ilike(like),
                        Entry.action_taken.ilike(like),
                        Entry.reported_by.ilike(like),
                        Entry.store_department.ilike(like),
                    )
                )
            total = q.count()
            rows = (
                q.order_by(Entry.entry_date.desc(), Entry.id.desc())
                .offset(params.get("offset", 0))
                .limit(params.get("limit", 100))
                .all()
            )
            return {"total": total, "items": [self._to_dict(r) for r in rows]}
        finally:
            db.close()

    def create_entry(self, payload: dict) -> dict:
        self._validate(payload)
        db = SessionLocal()
        try:
            entry = Entry(
                entry_date=_parse_date(payload["entry_date"]),
                location_type=payload["location_type"],
                brand=payload.get("brand"),
                store_department=payload["store_department"],
                reported_by=payload["reported_by"],
                time_sent=_parse_time(payload["time_sent"]),
                time_received=_parse_time(payload["time_received"]),
                time_done=_parse_time(payload.get("time_done")),
                mis_personnel=payload["mis_personnel"],
                problem=payload["problem"],
                findings_cause=payload.get("findings_cause"),
                action_taken=payload.get("action_taken"),
                remarks=payload.get("remarks"),
                task=payload["task"],
                task_remarks=payload.get("task_remarks"),
                acknowledged_by=payload.get("acknowledged_by"),
                area_manager_head=payload.get("area_manager_head"),
                type_=payload["type_"],
                type_of_support=payload["type_of_support"],
            )
            self._grow_reported_by(db, payload["reported_by"])
            db.add(entry)
            db.commit()
            db.refresh(entry)
            return self._to_dict(entry)
        finally:
            db.close()

    def update_entry(self, entry_id: int, payload: dict) -> dict:
        self._validate(payload)
        db = SessionLocal()
        try:
            entry = db.get(Entry, entry_id)
            if entry is None or entry.is_deleted:
                raise LocalError("Entry not found")
            if entry.version != payload["version"]:
                raise LocalError(
                    "This entry was changed since it was loaded. Reload it and try again."
                )
            for field in [
                "entry_date",
                "location_type",
                "brand",
                "store_department",
                "reported_by",
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
            ]:
                value = payload.get(field)
                if field == "entry_date":
                    value = _parse_date(value)
                setattr(entry, field, value)
            entry.time_sent = _parse_time(payload["time_sent"])
            entry.time_received = _parse_time(payload["time_received"])
            entry.time_done = _parse_time(payload.get("time_done"))
            entry.version += 1
            self._grow_reported_by(db, payload["reported_by"])
            db.commit()
            db.refresh(entry)
            return self._to_dict(entry)
        finally:
            db.close()

    def delete_entry(self, entry_id: int) -> None:
        db = SessionLocal()
        try:
            entry = db.get(Entry, entry_id)
            if entry is None or entry.is_deleted:
                raise LocalError("Entry not found")
            entry.is_deleted = True
            entry.version += 1
            db.commit()
        finally:
            db.close()

    def _grow_reported_by(self, db, value: str):
        value = value.strip()
        if not value:
            return
        exists = (
            db.query(Lookup)
            .filter(Lookup.kind == "reported_by", Lookup.value == value)
            .first()
        )
        if exists is None:
            db.add(Lookup(kind="reported_by", value=value))

    # ---- lookups ----

    def brands(self) -> list[str]:
        db = SessionLocal()
        try:
            rows = (
                db.query(Lookup)
                .filter(Lookup.kind == "brand", Lookup.is_active.is_(True))
                .order_by(Lookup.value)
                .all()
            )
            return [r.value for r in rows]
        finally:
            db.close()

    def locations(self, location_type: str, brand: str | None = None) -> list[str]:
        db = SessionLocal()
        try:
            q = db.query(Lookup).filter(
                Lookup.kind == "location",
                Lookup.location_type == location_type,
                Lookup.is_active.is_(True),
            )
            if brand:
                q = q.filter(Lookup.brand == brand)
            return [r.value for r in q.order_by(Lookup.value).all()]
        finally:
            db.close()

    def area_managers(self) -> list[str]:
        db = SessionLocal()
        try:
            rows = (
                db.query(Lookup)
                .filter(Lookup.kind == "area_manager", Lookup.is_active.is_(True))
                .order_by(Lookup.value)
                .all()
            )
            return [r.value for r in rows]
        finally:
            db.close()

    def reported_by(self, q: str = "") -> list[str]:
        db = SessionLocal()
        try:
            query = db.query(Lookup).filter(Lookup.kind == "reported_by")
            if q:
                query = query.filter(Lookup.value.ilike(f"%{q}%"))
            return [r.value for r in query.order_by(Lookup.value).all()]
        finally:
            db.close()

    # ---- lookup management ----

    def manage_list(self, kind: str) -> list[dict]:
        db = SessionLocal()
        try:
            rows = (
                db.query(Lookup)
                .filter(Lookup.kind == kind)
                .order_by(Lookup.brand, Lookup.value)
                .all()
            )
            return [
                {
                    "id": r.id,
                    "kind": r.kind,
                    "location_type": r.location_type,
                    "brand": r.brand,
                    "value": r.value,
                    "is_active": r.is_active,
                }
                for r in rows
            ]
        finally:
            db.close()

    def add_lookup(
        self, kind: str, value: str, location_type: str | None = None, brand: str | None = None
    ) -> dict:
        value = value.strip()
        db = SessionLocal()
        try:
            existing = (
                db.query(Lookup)
                .filter(
                    Lookup.kind == kind,
                    Lookup.location_type == location_type,
                    Lookup.brand == brand,
                    Lookup.value == value,
                )
                .first()
            )
            if existing:
                existing.is_active = True
                db.commit()
                return {"id": existing.id}
            row = Lookup(kind=kind, location_type=location_type, brand=brand, value=value)
            db.add(row)
            db.commit()
            db.refresh(row)
            return {"id": row.id}
        finally:
            db.close()

    def update_lookup(self, lookup_id: int, **fields) -> dict:
        db = SessionLocal()
        try:
            row = db.get(Lookup, lookup_id)
            if row is None:
                raise LocalError("Not found")
            if fields.get("value") is not None:
                row.value = fields["value"].strip()
            if fields.get("brand") is not None:
                row.brand = fields["brand"]
            if "is_active" in fields and fields["is_active"] is not None:
                row.is_active = fields["is_active"]
            db.commit()
            return {"id": row.id}
        finally:
            db.close()

    def remove_lookup(self, lookup_id: int) -> None:
        db = SessionLocal()
        try:
            row = db.get(Lookup, lookup_id)
            if row is None:
                raise LocalError("Not found")
            row.is_active = False
            db.commit()
        finally:
            db.close()

    # ---- export ----

    def export(self, month: str, dest_path: str) -> str:
        year, mon = (int(p) for p in month.split("-"))
        first_day = dt.date(year, mon, 1)
        last_day = dt.date(year, mon, calendar.monthrange(year, mon)[1])

        db = SessionLocal()
        try:
            entries = (
                db.query(Entry)
                .filter(
                    Entry.is_deleted.is_(False),
                    Entry.entry_date >= first_day,
                    Entry.entry_date <= last_day,
                )
                .order_by(Entry.entry_date, Entry.id)
                .all()
            )
            rows = [
                EntryRow(
                    entry_date=e.entry_date,
                    store_department=e.store_department,
                    reported_by=e.reported_by,
                    time_sent=e.time_sent,
                    time_received=e.time_received,
                    time_done=e.time_done,
                    mis_personnel=e.mis_personnel,
                    problem=e.problem,
                    task=e.task,
                    type_=e.type_,
                    type_of_support=e.type_of_support,
                    findings_cause=e.findings_cause,
                    action_taken=e.action_taken,
                    remarks=e.remarks,
                    task_remarks=e.task_remarks,
                    acknowledged_by=e.acknowledged_by,
                    area_manager_head=e.area_manager_head,
                )
                for e in entries
            ]
        finally:
            db.close()

        month_name = calendar.month_name[mon].upper()
        wb = build_monthly_workbook(rows, month_name, year)
        wb.save(dest_path)
        try:
            # Best-effort: if LibreOffice isn't installed on this machine,
            # the file still opens fine -- Excel recalculates formulas
            # itself on open, it just won't have a pre-computed cache.
            recalc(dest_path, timeout=90)
        except Exception:
            pass
        return dest_path

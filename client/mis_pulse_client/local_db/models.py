import datetime as dt

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)


class Lookup(Base):
    """Dropdown/autocomplete value pools -- same shape as the multi-user
    backend's, just local. kind='brand' and kind='location' (STORE rows
    also carry a brand) are curated; kind='area_manager' is curated;
    kind='reported_by' grows automatically as names are typed."""

    __tablename__ = "lookups"
    __table_args__ = (
        UniqueConstraint("kind", "location_type", "brand", "value", name="uq_lookup_value"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(String(30), index=True)
    location_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    value: Mapped[str] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow)


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    entry_date: Mapped[dt.date] = mapped_column(Date, index=True)
    location_type: Mapped[str] = mapped_column(String(20))
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    store_department: Mapped[str] = mapped_column(String(200), index=True)
    reported_by: Mapped[str] = mapped_column(String(200))

    time_sent: Mapped[dt.time] = mapped_column(Time)
    time_received: Mapped[dt.time] = mapped_column(Time)
    time_done: Mapped[dt.time | None] = mapped_column(Time, nullable=True)

    mis_personnel: Mapped[str] = mapped_column(String(50))

    problem: Mapped[str] = mapped_column(Text)
    findings_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_taken: Mapped[str | None] = mapped_column(Text, nullable=True)

    remarks: Mapped[str | None] = mapped_column(String(50), nullable=True)
    task: Mapped[str] = mapped_column(String(50))
    task_remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    acknowledged_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    area_manager_head: Mapped[str | None] = mapped_column(String(200), nullable=True)

    type_: Mapped[str | None] = mapped_column("type", String(50), nullable=True)
    type_of_support: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

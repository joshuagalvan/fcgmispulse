import datetime as dt

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base
from .timeutil import utcnow as _utcnow


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow)


class UserSession(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow)
    last_seen_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow)
    expires_at: Mapped[dt.datetime] = mapped_column(DateTime)
    revoked_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship()


class Lookup(Base):
    """Dropdown/autocomplete value pools.

    kind='brand' rows are the list of brands (Angels Pizza, Figaro, ...),
    curated (admin-managed). kind='location' rows carry a location_type of
    STORE or DEPARTMENT and are curated too; STORE rows also carry a brand.
    kind='area_manager' rows are curated. kind='reported_by' rows grow
    automatically as staff type new names.
    """

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

    # Nullable at the DB layer (a handful of historical rows predate these
    # being required) even though the live API requires them for new entries.
    type_: Mapped[str | None] = mapped_column("type", String(50), nullable=True)
    type_of_support: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class EntryHistory(Base):
    __tablename__ = "entry_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey("entries.id"), index=True)
    changed_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    changed_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow)
    snapshot_json: Mapped[str] = mapped_column(Text)

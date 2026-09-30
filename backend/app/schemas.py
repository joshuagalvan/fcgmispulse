import datetime as dt

from mis_pulse_export.choices import (
    LOCATION_TYPES,
    MIS_PERSONNEL,
    OWNERSHIP_TYPE,
    REMARKS,
    TASK,
    TYPE_OF_SUPPORT,
)
from pydantic import BaseModel, ConfigDict, field_validator, model_validator


def _choice_validator(allowed: list[str]):
    def _validate(cls, v):
        if v is not None and v not in allowed:
            raise ValueError(f"must be one of {allowed}, got {v!r}")
        return v

    return _validate


def _multi_choice_validator(allowed: list[str]):
    """mis_personnel is stored as a single comma-joined string (matching the
    original sheet's convention for the rare multi-person ticket), but each
    named person must still be one of the known 6."""

    def _validate(cls, v):
        parts = [p.strip() for p in v.split(",") if p.strip()]
        if not parts:
            raise ValueError("at least one MIS Personnel is required")
        invalid = [p for p in parts if p not in allowed]
        if invalid:
            raise ValueError(f"must be one of {allowed}, got invalid value(s) {invalid}")
        return ", ".join(parts)

    return _validate


# ---- Auth -------------------------------------------------------------


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str
    is_admin: bool


class LoginResponse(BaseModel):
    token: str
    user: UserOut


# ---- Lookups ------------------------------------------------------------


class LookupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: str
    location_type: str | None
    brand: str | None
    value: str
    is_active: bool


class LookupCreate(BaseModel):
    kind: str
    location_type: str | None = None
    brand: str | None = None
    value: str


class LookupUpdate(BaseModel):
    value: str | None = None
    brand: str | None = None
    is_active: bool | None = None


# ---- Entries ------------------------------------------------------------


class EntryBase(BaseModel):
    """Field shape as it can exist at rest, including historical rows that
    predate today's strict choices (e.g. a handful of pre-dropdown rows with
    a multi-name mis_personnel value like "MARCO, RAMON") or that are simply
    missing an optional field. No choice validation here -- reading a row
    back must never fail just because it doesn't fit today's rules. Only
    EntryCreate/EntryUpdate (new writes from the live UI) enforce choices."""

    model_config = ConfigDict(from_attributes=True)

    entry_date: dt.date
    location_type: str
    brand: str | None = None
    store_department: str
    reported_by: str
    time_sent: dt.time
    time_received: dt.time
    time_done: dt.time | None = None
    mis_personnel: str
    problem: str
    findings_cause: str | None = None
    action_taken: str | None = None
    remarks: str | None = None
    task: str
    task_remarks: str | None = None
    acknowledged_by: str | None = None
    area_manager_head: str | None = None
    type_: str | None = None
    type_of_support: str | None = None


class EntryCreate(EntryBase):
    type_: str
    type_of_support: str

    _v_location_type = field_validator("location_type")(_choice_validator(LOCATION_TYPES))
    _v_mis_personnel = field_validator("mis_personnel")(_multi_choice_validator(MIS_PERSONNEL))
    _v_remarks = field_validator("remarks")(_choice_validator(REMARKS))
    _v_task = field_validator("task")(_choice_validator(TASK))
    _v_type_ = field_validator("type_")(_choice_validator(OWNERSHIP_TYPE))
    _v_type_of_support = field_validator("type_of_support")(_choice_validator(TYPE_OF_SUPPORT))

    @model_validator(mode="after")
    def _require_brand_for_stores(self):
        if self.location_type == "STORE" and not self.brand:
            raise ValueError("brand is required when location_type is STORE")
        return self


class EntryUpdate(EntryCreate):
    version: int


class EntryOut(EntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by: int
    created_by_name: str
    updated_by: int | None
    updated_by_name: str | None
    created_at: dt.datetime
    updated_at: dt.datetime
    version: int
    duration_seconds: int | None = None


class EntryListResponse(BaseModel):
    total: int
    items: list[EntryOut]

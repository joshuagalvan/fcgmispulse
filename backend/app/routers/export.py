import calendar
import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from mis_pulse_export import EntryRow, build_monthly_workbook
from mis_pulse_export.build_workbook import save_and_recalc
from sqlalchemy.orm import Session

from .. import models
from ..config import settings
from ..db import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/export", tags=["export"])


def _entry_to_row(e: models.Entry) -> EntryRow:
    return EntryRow(
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


@router.get("")
def export_month(
    month: str,
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    """month is 'YYYY-MM', e.g. '2026-09'."""
    try:
        year, mon = (int(part) for part in month.split("-"))
        first_day = dt.date(year, mon, 1)
    except (ValueError, TypeError):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "month must be formatted YYYY-MM")

    last_day = dt.date(year, mon, calendar.monthrange(year, mon)[1])

    entries = (
        db.query(models.Entry)
        .filter(
            models.Entry.is_deleted.is_(False),
            models.Entry.entry_date >= first_day,
            models.Entry.entry_date <= last_day,
        )
        .order_by(models.Entry.entry_date, models.Entry.id)
        .all()
    )

    month_name = calendar.month_name[mon].upper()
    wb = build_monthly_workbook([_entry_to_row(e) for e in entries], month_name, year)

    export_dir = settings.db_path.parent / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    filename = f"MIS SUPPORT SUMMARY REPORT - {month_name} {year}.xlsx"
    out_path = export_dir / filename

    save_and_recalc(wb, out_path)

    return FileResponse(
        out_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

import datetime as dt


def utcnow() -> dt.datetime:
    """Naive UTC now — SQLite has no real datetime type, so SQLAlchemy round-trips
    DateTime(timezone=True) values as naive anyway. Standardizing on naive UTC
    everywhere avoids offset-aware/offset-naive comparison errors."""
    return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)

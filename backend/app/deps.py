import datetime as dt

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from . import models
from .config import settings
from .db import get_db
from .security import hash_token
from .timeutil import utcnow


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> models.User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    token_hash = hash_token(token)

    session = (
        db.query(models.UserSession)
        .filter(models.UserSession.token_hash == token_hash)
        .first()
    )
    now = utcnow()
    if (
        session is None
        or session.revoked_at is not None
        or session.expires_at < now
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired session")

    session.last_seen_at = now
    session.expires_at = now + dt.timedelta(days=settings.session_ttl_days)
    db.commit()

    user = db.get(models.User, session.user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User no longer exists")
    return user


def require_admin(user: models.User = Depends(get_current_user)) -> models.User:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    return user

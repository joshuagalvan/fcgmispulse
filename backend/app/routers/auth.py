import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import settings
from ..db import get_db
from ..deps import get_current_user
from ..limiter import limiter
from ..security import hash_token, new_session_token, verify_password
from ..timeutil import utcnow

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.LoginResponse)
@limiter.limit(settings.login_rate_limit)
def login(request: Request, body: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .filter(models.User.username == body.username.strip().lower())
        .first()
    )
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password")

    token, token_hash = new_session_token()
    now = utcnow()
    session = models.UserSession(
        user_id=user.id,
        token_hash=token_hash,
        created_at=now,
        last_seen_at=now,
        expires_at=now + dt.timedelta(days=settings.session_ttl_days),
    )
    db.add(session)
    db.commit()

    return schemas.LoginResponse(token=token, user=schemas.UserOut.model_validate(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, db: Session = Depends(get_db)):
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("bearer "):
        token_hash = hash_token(authorization.split(" ", 1)[1].strip())
        session = (
            db.query(models.UserSession)
            .filter(models.UserSession.token_hash == token_hash)
            .first()
        )
        if session is not None:
            session.revoked_at = utcnow()
            db.commit()


@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return schemas.UserOut.model_validate(user)

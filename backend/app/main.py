from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from . import models  # noqa: F401 (registers models on Base.metadata)
from .config import settings
from .db import Base, engine
from .limiter import limiter
from .routers import auth, entries, export, lookups, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FCG MIS Pulse API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth.router)
app.include_router(entries.router)
app.include_router(lookups.router)
app.include_router(export.router)
app.include_router(users.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"min_client_version": settings.min_client_version}

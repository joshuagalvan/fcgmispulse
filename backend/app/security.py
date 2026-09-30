import hashlib
import secrets

from pwdlib import PasswordHash

from .config import settings

_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _password_hash.verify(password, password_hash)


def new_session_token() -> tuple[str, str]:
    """Returns (token_to_hand_to_client, hash_to_store_in_db)."""
    token = secrets.token_urlsafe(settings.token_bytes)
    return token, hash_token(token)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

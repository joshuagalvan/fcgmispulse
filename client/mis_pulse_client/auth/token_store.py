import keyring

from ..config import KEYRING_SERVICE

_ACCOUNT = "session_token"


def save_token(token: str) -> None:
    try:
        keyring.set_password(KEYRING_SERVICE, _ACCOUNT, token)
    except Exception:
        pass  # trusted-device convenience only; login still works without it


def load_token() -> str | None:
    try:
        return keyring.get_password(KEYRING_SERVICE, _ACCOUNT)
    except Exception:
        return None


def clear_token() -> None:
    try:
        keyring.delete_password(KEYRING_SERVICE, _ACCOUNT)
    except Exception:
        pass

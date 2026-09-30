from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="MIS_PULSE_")

    db_path: Path = Path(__file__).resolve().parent.parent / "data" / "mis_pulse.db"
    token_bytes: int = 32
    session_ttl_days: int = 90
    min_client_version: str = "0.1.0"

    login_rate_limit: str = "10/minute"


settings = Settings()
settings.db_path.parent.mkdir(parents=True, exist_ok=True)

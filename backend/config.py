"""Application configuration and settings helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Central application settings loaded via Pydantic."""

    # General application metadata
    APP_NAME: str = "happyStock Trading API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Primary database settings
    DB_TYPE: str = "sqlite"
    DATABASE_URL: str = "sqlite:///virtual_market.db"

    SIM_DB_HOST: str = "localhost"
    SIM_DB_PORT: int = 5432
    SIM_DB_USER: str = "postgres"
    SIM_DB_PASSWORD: str = "ChangeMe123!"
    SIM_DB_NAME: str = "happystock_sim"

    @property
    def resolved_database_url(self) -> str:
        """Return an absolute SQLite URL when a relative path is provided."""
        prefix = "sqlite:///"
        if self.DATABASE_URL.startswith(prefix):
            db_path = self.DATABASE_URL[len(prefix) :]
            if (len(db_path) > 1 and db_path[1] == ":") or db_path.startswith("/"):
                return self.DATABASE_URL
            absolute = BASE_DIR / db_path
            return f"{prefix}{absolute}"
        return self.DATABASE_URL

    @property
    def sim_database_url(self) -> str:
        """Timescale/Postgres DSN used by the simulation services."""
        password = quote_plus(self.SIM_DB_PASSWORD or "")
        return (
            f"postgresql://{self.SIM_DB_USER}:{password}"
            f"@{self.SIM_DB_HOST}:{self.SIM_DB_PORT}/{self.SIM_DB_NAME}"
        )

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None
    SIM_REDIS_URL: Optional[str] = None
    SIM_SIGNAL_SESSION: Optional[str] = None
    SIM_SIGNAL_REDIS_URL: Optional[str] = None
    SIM_SIGNAL_DRIFT_SCALE: float = 0.0005

    # JWT / auth
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@happystock.com"
    SMTP_FROM_NAME: str = "happyStock"
    SMTP_SENDER_EMAIL: str = "support@happystock.com"
    SMTP_USE_TLS: bool = True

    # URLs
    APP_BASE_URL: str = "http://localhost:3000"
    API_BASE_URL: str = "http://localhost:8000"

    # Token expirations (seconds)
    PASSWORD_RESET_TOKEN_EXPIRY: int = 86400
    EMAIL_VERIFICATION_TOKEN_EXPIRY: int = 172800

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # Simulation options
    PRICE_GENERATION_ENABLED: bool = False
    SIM_SLOW_TICK_THRESHOLD_MS: int = 1000
    SIM_SLOW_TICK_LOG: str = "backend/logs/slow_ticks.log"
    SIM_AGENTS_ENABLED: bool = True

    class Config:
        env_file = str(BASE_DIR / ".env")
        case_sensitive = True


settings = Settings()


TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {
                "file_path": "db.sqlite3"
            }
        }
    },
    "apps": {
        "models": {
            "models": [
                "models.user",
                "models.account",
                "models.asset",
                "models.trade",
                "models.holding",
                "models.password_reset_token",
                "models.email_verification_token",
                "models.email_log",
            ],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai",
}

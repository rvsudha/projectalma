"""Application configuration.

Settings are loaded from environment variables (12-factor); a local ``.env`` file
is read for convenience in development. In ``production`` the model refuses to
start with insecure defaults — see :meth:`Settings._guard_production`.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

Environment = Literal["local", "test", "staging", "production"]

_INSECURE_SECRET = "dev-only-insecure-secret-change-me"
_INSECURE_PASSWORD = "changeme123"


def _csv(value: object) -> object:
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    # --- App ---
    environment: Environment = "local"
    debug: bool = True
    project_name: str = "ProjectAlma API"
    version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    docs_enabled: bool = True

    cors_origins: Annotated[list[str], NoDecode] = Field(default=["http://localhost:3000"])

    # --- Database ---
    # Async driver DSN used by the app (asyncpg / aiosqlite).
    database_url: str = "postgresql+asyncpg://projectalma:projectalma@localhost:5432/projectalma"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout_seconds: int = 30
    db_pool_recycle_seconds: int = 1800
    db_echo: bool = False
    db_statement_timeout_ms: int = 10_000  # Postgres only

    # --- Auth ---
    secret_key: str = _INSECURE_SECRET
    access_token_expire_minutes: int = 60 * 8
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "projectalma-api"
    bcrypt_rounds: int = 12

    seed_attorney_email: str = "attorney@projectalma.com"
    seed_attorney_password: str = _INSECURE_PASSWORD
    seed_attorney_name: str = "Attorney"

    # Attorney self-registration. Gated by an invite code so signup is not an
    # open door to lead PII. Disable entirely, or rotate the code, in production.
    attorney_signup_enabled: bool = True
    attorney_signup_code: str = "welcome"

    # --- Rate limiting (in-process token bucket; see core.ratelimit) ---
    rate_limit_enabled: bool = True
    rate_limit_lead_create_per_hour: int = 20
    rate_limit_login_per_15min: int = 10
    rate_limit_signup_per_hour: int = 5

    # --- Email (Resend) ---
    resend_api_key: str | None = None
    email_from: str = "ProjectAlma <noreply@projectalma.com>"
    attorney_notification_email: str = "intake@projectalma.com"
    frontend_base_url: str = "http://localhost:3000"

    # --- Resume storage ---
    storage_backend: Literal["local", "s3"] = "local"
    storage_local_dir: str = "./var/resumes"
    max_resume_bytes: int = 10 * 1024 * 1024
    allowed_resume_content_types: Annotated[list[str], NoDecode] = Field(
        default=[
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]
    )

    s3_bucket: str | None = None
    s3_region: str | None = None
    s3_endpoint_url: str | None = None
    s3_presign_expiry_seconds: int = 3600
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    # ------------------------------------------------------------------

    @model_validator(mode="before")
    @classmethod
    def _split_csv_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            for key in ("cors_origins", "allowed_resume_content_types", "CORS_ORIGINS"):
                if key in data:
                    data[key] = _csv(data[key])
        return data

    @model_validator(mode="after")
    def _guard_production(self) -> Settings:
        if self.environment != "production":
            return self
        problems: list[str] = []
        if self.secret_key == _INSECURE_SECRET or len(self.secret_key) < 32:
            problems.append("SECRET_KEY must be set to a strong value (>=32 chars)")
        if self.seed_attorney_password == _INSECURE_PASSWORD:
            problems.append("SEED_ATTORNEY_PASSWORD must not be the default")
        if self.storage_backend == "s3" and not self.s3_bucket:
            problems.append("STORAGE_BACKEND=s3 requires S3_BUCKET")
        if self.debug:
            problems.append("DEBUG must be false in production")
        if self.attorney_signup_enabled and self.attorney_signup_code == "welcome":
            problems.append(
                "ATTORNEY_SIGNUP_CODE must be rotated (or ATTORNEY_SIGNUP_ENABLED=false)"
            )
        if problems:
            raise ValueError("Insecure production configuration: " + "; ".join(problems))
        return self

    @property
    def sync_database_url(self) -> str:
        """Blocking DSN for Alembic and management scripts."""
        return self.database_url.replace("+asyncpg", "+psycopg").replace("+aiosqlite", "+pysqlite")

    @property
    def is_testing(self) -> bool:
        return self.environment == "test"

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

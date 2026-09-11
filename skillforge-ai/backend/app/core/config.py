"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import AliasChoices, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Placeholder only — never a real password. Replace in local .env.
_DATABASE_URL_PLACEHOLDER = (
    "postgresql+psycopg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/skillforge_db"
)

_PLACEHOLDER_MARKERS = ("YOUR_POSTGRES_PASSWORD", "<PRIVATE_PASSWORD>")


def is_placeholder_database_url(url: str | None) -> bool:
    """Return True when DATABASE_URL still contains a non-secret password placeholder."""
    value = (url or "").strip()
    if not value:
        return True
    return any(marker in value for marker in _PLACEHOLDER_MARKERS)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="SkillForge AI", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    api_prefix: str = Field(default="/api", alias="API_PREFIX")

    cors_origins_raw: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS",
    )

    database_url: str = Field(default=_DATABASE_URL_PLACEHOLDER, alias="DATABASE_URL")

    jwt_secret: str = Field(
        default="change-me-to-a-long-random-string",
        validation_alias=AliasChoices("JWT_SECRET_KEY", "JWT_SECRET"),
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=60,
        validation_alias=AliasChoices(
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
            "ACCESS_TOKEN_EXPIRE_MINUTES",
        ),
    )

    # Development-only admin bootstrap (never used by public registration).
    bootstrap_admin_email: str | None = Field(default=None, alias="BOOTSTRAP_ADMIN_EMAIL")
    bootstrap_admin_password: str | None = Field(default=None, alias="BOOTSTRAP_ADMIN_PASSWORD")

    upload_dir: str = Field(default="./storage/uploads", alias="UPLOAD_DIR")
    max_upload_mb: int = Field(default=10, alias="MAX_UPLOAD_MB")

    ai_provider: str = Field(default="mock", alias="AI_PROVIDER")
    course_provider_mode: str = Field(default="mock", alias="COURSE_PROVIDER_MODE")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins(self) -> list[str]:
        raw = self.cors_origins_raw.strip()
        if not raw:
            return []
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() in {"development", "dev", "local"}

    @property
    def has_database_credentials(self) -> bool:
        """True when DATABASE_URL does not still contain the password placeholder."""
        return not is_placeholder_database_url(self.database_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()


settings = get_settings()

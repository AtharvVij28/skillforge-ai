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

    email_verification_required: bool = Field(default=True, alias="EMAIL_VERIFICATION_REQUIRED")
    frontend_public_url: str = Field(
        default="http://localhost:5173",
        validation_alias=AliasChoices("FRONTEND_URL", "FRONTEND_PUBLIC_URL"),
    )
    smtp_host: str | None = Field(
        default=None,
        validation_alias=AliasChoices("RESEND_SMTP_HOST", "SMTP_HOST"),
    )
    smtp_port: int = Field(
        default=587,
        validation_alias=AliasChoices("RESEND_SMTP_PORT", "SMTP_PORT"),
    )
    smtp_username: str | None = Field(
        default=None,
        validation_alias=AliasChoices("RESEND_SMTP_USERNAME", "SMTP_USERNAME"),
    )
    smtp_password: str | None = Field(default=None, alias="SMTP_PASSWORD")
    smtp_from: str | None = Field(default=None, alias="SMTP_FROM")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")
    resend_api_key: str | None = Field(default=None, alias="RESEND_API_KEY")
    resend_from: str | None = Field(
        default=None,
        validation_alias=AliasChoices("RESEND_FROM_EMAIL", "RESEND_FROM"),
    )

    upload_dir: str = Field(default="./storage/uploads", alias="UPLOAD_DIR")
    max_upload_mb: int = Field(default=10, alias="MAX_UPLOAD_MB")

    ai_provider: str = Field(default="mock", alias="AI_PROVIDER")
    llm_api_key: str | None = Field(default=None, alias="LLM_API_KEY")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")
    llm_api_base: str = Field(default="https://api.openai.com/v1", alias="LLM_API_BASE")
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

    @property
    def uses_live_llm(self) -> bool:
        provider = (self.ai_provider or "mock").strip().lower()
        key = (self.llm_api_key or "").strip()
        return provider in {"openai", "open_ai"} and bool(key)

    @property
    def mail_delivery_configured(self) -> bool:
        has_smtp = bool((self.smtp_host or "").strip() and (self.smtp_from or "").strip())
        has_resend = bool((self.resend_api_key or "").strip())
        return has_smtp or has_resend


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()


settings = get_settings()

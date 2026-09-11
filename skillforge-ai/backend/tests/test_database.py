"""Database configuration and session tests (no secrets in assertions)."""

import os

import pytest
from sqlalchemy import inspect

from app.core.config import clear_settings_cache, get_settings, settings
from app.core.database import (
    check_database_connection,
    get_engine,
    get_session_factory,
    reset_db_state,
)
import app.models  # noqa: F401
from app.core.database import Base


def test_database_url_comes_from_settings() -> None:
    assert settings.database_url
    assert "postgresql" in settings.database_url
    # Never assert or print the password/url value beyond scheme checks.
    assert "@" in settings.database_url


def test_placeholder_detection() -> None:
    clear_settings_cache()
    reset_db_state()
    os.environ["DATABASE_URL"] = (
        "postgresql+psycopg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/skillforge_db"
    )
    clear_settings_cache()
    try:
        cfg = get_settings()
        assert cfg.has_database_credentials is False
        # Must short-circuit on placeholder — must not use a cached real engine/.env URL.
        assert check_database_connection() is False
    finally:
        os.environ.pop("DATABASE_URL", None)
        clear_settings_cache()
        reset_db_state()


def test_model_metadata_registered() -> None:
    expected = {
        "roles",
        "departments",
        "users",
        "user_profiles",
        "competency_categories",
        "competencies",
        "role_competencies",
        "user_competencies",
        "learning_resources",
        "learning_resource_competencies",
        "learning_history",
        "documents",
        "document_chunks",
        "questions",
        "assessments",
        "assessment_questions",
        "assessment_attempts",
        "assessment_answers",
        "recommendations",
        "audit_logs",
    }
    assert expected.issubset(set(Base.metadata.tables.keys()))


def test_user_relationships_defined() -> None:
    user_table = Base.metadata.tables["users"]
    fk_targets = {fk.column.table.name for fk in user_table.foreign_keys}
    assert "roles" in fk_targets
    assert "departments" in fk_targets

    profile = Base.metadata.tables["user_profiles"]
    assert any(fk.column.table.name == "users" for fk in profile.foreign_keys)


@pytest.mark.integration
def test_database_connection_and_session() -> None:
    """Requires a real DATABASE_URL in the environment (not the placeholder).

    Set SKIP_DB_TESTS=1 to skip. Uses DATABASE_URL or TEST_DATABASE_URL.
    """
    if os.getenv("SKIP_DB_TESTS", "").lower() in {"1", "true", "yes"}:
        pytest.skip("SKIP_DB_TESTS is set")

    test_url = os.getenv("TEST_DATABASE_URL")
    if test_url:
        clear_settings_cache()
        os.environ["DATABASE_URL"] = test_url
        clear_settings_cache()
        reset_db_state()

    clear_settings_cache()
    cfg = get_settings()
    if not cfg.has_database_credentials:
        pytest.skip("DATABASE_URL password placeholder still set — configure local .env")

    reset_db_state()
    assert check_database_connection() is True

    session = get_session_factory()()
    try:
        assert session.bind is not None
        inspector = inspect(get_engine())
        # Tables may be missing until alembic upgrade; connection itself must work.
        assert inspector is not None
    finally:
        session.close()
        reset_db_state()
        if test_url:
            clear_settings_cache()

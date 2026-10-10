"""Shared pytest fixtures for API tests (SQLite in-memory — no real credentials)."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(_type, _compiler, **_kw) -> str:
    return "JSON"


@compiles(UUID, "sqlite")
def _compile_uuid_sqlite(_type, _compiler, **_kw) -> str:
    return "CHAR(36)"

from app.core.config import clear_settings_cache
from app.core.database import get_db, reset_db_state
from app.main import app
from app.models.assessment import (
    Assessment,
    AssessmentAnswer,
    AssessmentAttempt,
    AssessmentQuestion,
    Question,
)
from app.models.competency import Competency, CompetencyCategory, RoleCompetency, UserCompetency
from app.models.document import Document, DocumentChunk
from app.models.learning import LearningHistory, LearningResource, LearningResourceCompetency, Recommendation
from app.models.skill_gap import SkillGapSnapshot
from app.models.user import Department, EmailVerificationToken, PasswordResetToken, Role, User, UserProfile


def _create_auth_tables(engine) -> None:
    """Create tables required for Phase 3–4 tests (avoids full PostgreSQL-only schema on SQLite)."""
    Role.__table__.create(bind=engine, checkfirst=True)
    Department.__table__.create(bind=engine, checkfirst=True)
    User.__table__.create(bind=engine, checkfirst=True)
    UserProfile.__table__.create(bind=engine, checkfirst=True)
    EmailVerificationToken.__table__.create(bind=engine, checkfirst=True)
    PasswordResetToken.__table__.create(bind=engine, checkfirst=True)
    CompetencyCategory.__table__.create(bind=engine, checkfirst=True)
    Competency.__table__.create(bind=engine, checkfirst=True)
    RoleCompetency.__table__.create(bind=engine, checkfirst=True)
    UserCompetency.__table__.create(bind=engine, checkfirst=True)
    SkillGapSnapshot.__table__.create(bind=engine, checkfirst=True)
    Document.__table__.create(bind=engine, checkfirst=True)
    DocumentChunk.__table__.create(bind=engine, checkfirst=True)
    LearningResource.__table__.create(bind=engine, checkfirst=True)
    Question.__table__.create(bind=engine, checkfirst=True)
    Assessment.__table__.create(bind=engine, checkfirst=True)
    AssessmentQuestion.__table__.create(bind=engine, checkfirst=True)
    AssessmentAttempt.__table__.create(bind=engine, checkfirst=True)
    AssessmentAnswer.__table__.create(bind=engine, checkfirst=True)
    LearningResourceCompetency.__table__.create(bind=engine, checkfirst=True)
    LearningHistory.__table__.create(bind=engine, checkfirst=True)
    Recommendation.__table__.create(bind=engine, checkfirst=True)


def _drop_auth_tables(engine) -> None:
    Recommendation.__table__.drop(bind=engine, checkfirst=True)
    LearningHistory.__table__.drop(bind=engine, checkfirst=True)
    LearningResourceCompetency.__table__.drop(bind=engine, checkfirst=True)
    AssessmentAnswer.__table__.drop(bind=engine, checkfirst=True)
    AssessmentAttempt.__table__.drop(bind=engine, checkfirst=True)
    AssessmentQuestion.__table__.drop(bind=engine, checkfirst=True)
    Assessment.__table__.drop(bind=engine, checkfirst=True)
    Question.__table__.drop(bind=engine, checkfirst=True)
    LearningResource.__table__.drop(bind=engine, checkfirst=True)
    DocumentChunk.__table__.drop(bind=engine, checkfirst=True)
    Document.__table__.drop(bind=engine, checkfirst=True)
    SkillGapSnapshot.__table__.drop(bind=engine, checkfirst=True)
    UserCompetency.__table__.drop(bind=engine, checkfirst=True)
    RoleCompetency.__table__.drop(bind=engine, checkfirst=True)
    Competency.__table__.drop(bind=engine, checkfirst=True)
    CompetencyCategory.__table__.drop(bind=engine, checkfirst=True)
    UserProfile.__table__.drop(bind=engine, checkfirst=True)
    PasswordResetToken.__table__.drop(bind=engine, checkfirst=True)
    EmailVerificationToken.__table__.drop(bind=engine, checkfirst=True)
    User.__table__.drop(bind=engine, checkfirst=True)
    Department.__table__.drop(bind=engine, checkfirst=True)
    Role.__table__.drop(bind=engine, checkfirst=True)


@pytest.fixture()
def test_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Use isolated JWT settings for auth tests."""
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret-not-for-production")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("EMAIL_VERIFICATION_REQUIRED", "false")
    clear_settings_cache()
    reset_db_state()
    yield
    clear_settings_cache()
    reset_db_state()


@pytest.fixture()
def db_session(test_settings: None) -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    _create_auth_tables(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        _drop_auth_tables(engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session, test_settings: None) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def learner_credentials() -> dict[str, str]:
    return {
        "email": "learner@example.com",
        "password": "LearnerPass123!",
        "full_name": "Test Learner",
    }


@pytest.fixture()
def registered_learner(client: TestClient, learner_credentials: dict[str, str]) -> dict:
    response = client.post("/api/auth/register", json=learner_credentials)
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def learner_token(
    client: TestClient, registered_learner: dict, learner_credentials: dict[str, str]
) -> str:
    response = client.post(
        "/api/auth/login",
        json={
            "email": learner_credentials["email"],
            "password": learner_credentials["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture()
def admin_user(db_session: Session) -> dict:
    from app.services.auth_service import bootstrap_admin_if_configured
    from app.services.role_service import ensure_default_roles

    ensure_default_roles(db_session)
    user = bootstrap_admin_if_configured(
        db_session,
        "admin@example.com",
        "AdminPass123!",
    )
    assert user is not None
    return {"email": "admin@example.com", "password": "AdminPass123!"}


@pytest.fixture()
def admin_token(client: TestClient, admin_user: dict) -> str:
    response = client.post("/api/auth/login", json=admin_user)
    assert response.status_code == 200
    return response.json()["access_token"]

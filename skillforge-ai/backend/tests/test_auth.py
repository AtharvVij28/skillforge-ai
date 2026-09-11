"""Phase 3 authentication and RBAC tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.user import User, UserProfile
from app.services.role_service import ROLE_ADMIN, ROLE_LEARNER, ensure_default_roles, get_role_by_code


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_successful_registration(client: TestClient, learner_credentials: dict) -> None:
    response = client.post("/api/auth/register", json=learner_credentials)
    assert response.status_code == 201
    payload = response.json()
    assert payload["email"] == learner_credentials["email"]
    assert payload["full_name"] == learner_credentials["full_name"]
    assert payload["role"]["code"] == ROLE_LEARNER
    assert payload["is_active"] is True
    assert "hashed_password" not in payload
    assert "password" not in payload


def test_duplicate_email_registration(
    client: TestClient, registered_learner: dict, learner_credentials: dict
) -> None:
    response = client.post("/api/auth/register", json=learner_credentials)
    assert response.status_code == 409


def test_password_is_hashed_not_plaintext(db_session: Session, learner_credentials: dict) -> None:
    from app.services.auth_service import register_learner
    from app.schemas.auth import RegisterRequest

    user_response = register_learner(db_session, RegisterRequest(**learner_credentials))
    user = db_session.scalar(select(User).where(User.email == user_response.email))
    assert user is not None
    assert user.hashed_password != learner_credentials["password"]
    assert user.hashed_password.startswith("$argon2")


def test_successful_login(client: TestClient, registered_learner: dict, learner_credentials: dict) -> None:
    response = client.post(
        "/api/auth/login",
        json={
            "email": learner_credentials["email"],
            "password": learner_credentials["password"],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert "password" not in payload


def test_invalid_password_login(client: TestClient, registered_learner: dict, learner_credentials: dict) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": learner_credentials["email"], "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_nonexistent_user_login(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "missing@example.com", "password": "SomePass123!"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_me_with_valid_token(client: TestClient, learner_token: str, learner_credentials: dict) -> None:
    response = client.get("/api/auth/me", headers=_auth_header(learner_token))
    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == learner_credentials["email"]
    assert payload["role"]["code"] == ROLE_LEARNER
    assert "hashed_password" not in payload


def test_me_without_token(client: TestClient) -> None:
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_with_invalid_token(client: TestClient) -> None:
    response = client.get("/api/auth/me", headers=_auth_header("not-a-valid-jwt"))
    assert response.status_code == 401


def test_expired_token_rejected(client: TestClient, registered_learner: dict) -> None:
    settings = get_settings()
    expired = jwt.encode(
        {
            "sub": registered_learner["id"],
            "role": ROLE_LEARNER,
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    response = client.get("/api/auth/me", headers=_auth_header(expired))
    assert response.status_code == 401


def test_learner_can_access_learner_endpoint(client: TestClient, learner_token: str) -> None:
    response = client.get("/api/learner/test", headers=_auth_header(learner_token))
    assert response.status_code == 200
    assert response.json()["message"] == "Learner access granted"


def test_learner_cannot_access_admin_endpoint(client: TestClient, learner_token: str) -> None:
    response = client.get("/api/admin/test", headers=_auth_header(learner_token))
    assert response.status_code == 403


def test_admin_can_access_admin_endpoint(client: TestClient, admin_token: str) -> None:
    response = client.get("/api/admin/test", headers=_auth_header(admin_token))
    assert response.status_code == 200
    assert response.json()["message"] == "Admin access granted"


def test_inactive_user_cannot_login(
    client: TestClient, db_session: Session, learner_credentials: dict
) -> None:
    ensure_default_roles(db_session)
    learner_role = get_role_by_code(db_session, ROLE_LEARNER)
    assert learner_role is not None
    user = User(
        email=learner_credentials["email"],
        hashed_password=hash_password(learner_credentials["password"]),
        full_name=learner_credentials["full_name"],
        role_id=learner_role.id,
        is_active=False,
        profile=UserProfile(profile_completion_pct=0),
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/auth/login",
        json={
            "email": learner_credentials["email"],
            "password": learner_credentials["password"],
        },
    )
    assert response.status_code == 403


def test_public_registration_always_learner_role(
    client: TestClient, learner_credentials: dict
) -> None:
    response = client.post("/api/auth/register", json=learner_credentials)
    assert response.status_code == 201
    assert response.json()["role"]["code"] == ROLE_LEARNER
    assert response.json()["role"]["code"] != ROLE_ADMIN


def test_api_never_exposes_password_hash(
    client: TestClient, registered_learner: dict, learner_token: str, learner_credentials: dict
) -> None:
    endpoints = [
        client.get("/api/auth/me", headers=_auth_header(learner_token)),
        client.post("/api/auth/login", json=learner_credentials),
    ]
    for response in endpoints:
        body = response.text.lower()
        assert "hashed_password" not in body
        assert learner_credentials["password"] not in body

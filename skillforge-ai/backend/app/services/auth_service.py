"""Authentication application service."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserProfile
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.role_service import ROLE_ADMIN, ROLE_LEARNER, ensure_default_roles, get_role_by_code


def _user_to_response(user: User) -> UserResponse:
    return UserResponse.model_validate(user)


def register_learner(db: Session, payload: RegisterRequest) -> UserResponse:
    ensure_default_roles(db)

    email = payload.email.lower().strip()
    existing = db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    learner_role = get_role_by_code(db, ROLE_LEARNER)
    if learner_role is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LEARNER role is not configured",
        )

    user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        role_id=learner_role.id,
        is_active=True,
        profile=UserProfile(profile_completion_pct=0),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    # Ensure role relationship is loaded for response
    user = db.scalar(
        select(User).options(joinedload(User.role)).where(User.id == user.id)
    )
    assert user is not None
    return _user_to_response(user)


def authenticate_user(db: Session, payload: LoginRequest) -> TokenResponse:
    email = payload.email.lower().strip()
    user = db.scalar(
        select(User).options(joinedload(User.role)).where(User.email == email)
    )

    # Uniform 401 — do not reveal whether email exists.
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise invalid
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()

    token = create_access_token(subject=user.id, role_code=user.role.code)
    return TokenResponse(access_token=token, token_type="bearer")


def bootstrap_admin_if_configured(db: Session, email: str, password: str) -> User | None:
    """Create or update a development ADMIN user. Never called from public registration."""
    ensure_default_roles(db)
    admin_role = get_role_by_code(db, ROLE_ADMIN)
    if admin_role is None:
        return None

    normalized = email.lower().strip()
    user = db.scalar(
        select(User).options(joinedload(User.role)).where(User.email == normalized)
    )
    if user is None:
        user = User(
            email=normalized,
            hashed_password=hash_password(password),
            full_name="Bootstrap Admin",
            role_id=admin_role.id,
            is_active=True,
            profile=UserProfile(profile_completion_pct=0),
        )
        db.add(user)
    else:
        user.role_id = admin_role.id
        user.hashed_password = hash_password(password)
        user.is_active = True
        db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id) -> User | None:
    return db.scalar(
        select(User).options(joinedload(User.role)).where(User.id == user_id)
    )

"""Authentication application service."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserProfile
from app.schemas.auth import LoginRequest, RegisterRequest, ResetPasswordRequest, TokenResponse, UserResponse
from app.services.email_policy import email_signup_error
from app.services.email_service import (
    consume_password_reset_token,
    consume_verification_token,
    create_password_reset_token,
    create_verification_token,
    dispatch_email,
    issue_and_send_verification,
    send_password_reset_email,
    send_verification_email,
    send_welcome_email,
)
from app.services.role_service import ROLE_ADMIN, ROLE_LEARNER, ensure_default_roles, get_role_by_code

logger = logging.getLogger(__name__)


def _user_to_response(user: User) -> UserResponse:
    return UserResponse.model_validate(user)


FORGOT_PASSWORD_MESSAGE = (
    "If an account exists for this email, you will receive password reset instructions."
)


def register_learner(
    db: Session,
    payload: RegisterRequest,
    background: BackgroundTasks | None = None,
) -> UserResponse:
    ensure_default_roles(db)

    email = payload.email.lower().strip()
    policy_error = email_signup_error(email)
    if policy_error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=policy_error)

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

    settings = get_settings()
    now = datetime.now(timezone.utc)
    user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        role_id=learner_role.id,
        is_active=True,
        email_verified_at=None if settings.email_verification_required else now,
        profile=UserProfile(profile_completion_pct=0),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id
    user_email = user.email
    user_name = user.full_name
    verify_token = None
    if settings.email_verification_required:
        verify_token = create_verification_token(db, user.id)

    dispatch_email(
        background,
        "Welcome",
        user_id,
        lambda: send_welcome_email(to_email=user_email, full_name=user_name, user_id=user_id),
    )
    if verify_token:
        token_value = verify_token
        dispatch_email(
            background,
            "Verification",
            user_id,
            lambda: send_verification_email(user_email, user_name, token_value),
        )

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
    if get_settings().email_verification_required and user.email_verified_at is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Confirm your email before signing in. Check your inbox for a SkillForge confirmation link.",
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
            email_verified_at=datetime.now(timezone.utc),
            profile=UserProfile(profile_completion_pct=0),
        )
        db.add(user)
    else:
        user.role_id = admin_role.id
        user.hashed_password = hash_password(password)
        user.is_active = True
        if user.email_verified_at is None:
            user.email_verified_at = datetime.now(timezone.utc)
        db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id) -> User | None:
    return db.scalar(
        select(User).options(joinedload(User.role)).where(User.id == user_id)
    )


def confirm_email(db: Session, token: str) -> UserResponse:
    try:
        user = consume_verification_token(db, token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    user = db.scalar(select(User).options(joinedload(User.role)).where(User.id == user.id))
    assert user is not None
    return _user_to_response(user)


def resend_verification(db: Session, email: str) -> None:
    settings = get_settings()
    if not settings.email_verification_required:
        return
    normalized = email.lower().strip()
    user = db.scalar(select(User).where(User.email == normalized))
    if user is None or user.email_verified_at is not None:
        return
    issue_and_send_verification(db, user)


def request_password_reset(
    db: Session,
    email: str,
    background: BackgroundTasks | None = None,
) -> str:
    normalized = email.lower().strip()
    user = db.scalar(select(User).where(User.email == normalized, User.is_active.is_(True)))
    if user is None:
        return FORGOT_PASSWORD_MESSAGE
    token = create_password_reset_token(db, user.id)
    user_id = user.id
    user_email = user.email
    user_name = user.full_name
    dispatch_email(
        background,
        "Password reset",
        user_id,
        lambda: send_password_reset_email(
            to_email=user_email,
            full_name=user_name,
            reset_token=token,
            user_id=user_id,
        ),
    )
    return FORGOT_PASSWORD_MESSAGE


def reset_password(db: Session, payload: ResetPasswordRequest) -> None:
    try:
        user = consume_password_reset_token(db, payload.token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    user.hashed_password = hash_password(payload.password)
    db.add(user)
    db.commit()

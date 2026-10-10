"""Authentication API routes."""

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_current_user
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    VerifyEmailRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    payload: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Public registration — always creates a LEARNER (never ADMIN)."""
    return auth_service.register_learner(db, payload, background=background_tasks)


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> MessageResponse:
    message = auth_service.request_password_reset(db, payload.email, background=background_tasks)
    return MessageResponse(message=message)


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> MessageResponse:
    auth_service.reset_password(db, payload)
    return MessageResponse(message="Password updated. You can sign in with your new password.")


@router.post("/verify-email", response_model=MessageResponse)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)) -> MessageResponse:
    auth_service.confirm_email(db, payload.token)
    return MessageResponse(message="Email confirmed. You can sign in now.")


@router.post("/resend-verification", response_model=MessageResponse)
def resend_verification(
    payload: ResendVerificationRequest, db: Session = Depends(get_db)
) -> MessageResponse:
    auth_service.resend_verification(db, payload.email)
    return MessageResponse(
        message="If this address can receive mail and still needs confirmation, we sent a new link."
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_service.authenticate_user(db, payload)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(require_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.post("/logout", response_model=MessageResponse)
def logout(current_user: User = Depends(require_current_user)) -> MessageResponse:
    """Stateless JWT logout — client must discard the token."""
    _ = current_user
    return MessageResponse(message="Logged out. Discard the access token on the client.")

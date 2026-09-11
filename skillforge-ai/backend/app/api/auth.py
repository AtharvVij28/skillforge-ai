"""Authentication API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    """Public registration — always creates a LEARNER (never ADMIN)."""
    return auth_service.register_learner(db, payload)


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

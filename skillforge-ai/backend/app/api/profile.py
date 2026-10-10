"""Profile API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_current_user, require_role
from app.models.user import User
from app.schemas.profile import (
    DepartmentListResponse,
    ProfileCompletionResponse,
    ProfileResponse,
    ProfileUpdateRequest,
)
from app.services import profile_service
from app.services.role_service import ROLE_ADMIN

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
def get_own_profile(
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    return profile_service.get_profile(db, current_user.id)


@router.put("", response_model=ProfileResponse)
def update_own_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    return profile_service.update_profile(db, current_user.id, payload)


@router.get("/completion", response_model=ProfileCompletionResponse)
def get_own_completion(
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> ProfileCompletionResponse:
    return profile_service.get_completion(db, current_user.id)


@router.get("/departments", response_model=DepartmentListResponse)
def list_departments(
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> DepartmentListResponse:
    _ = current_user
    return DepartmentListResponse(items=profile_service.list_departments(db))


@router.get("/{user_id}", response_model=ProfileResponse)
def get_user_profile(
    user_id: UUID,
    current_user: User = Depends(require_role(ROLE_ADMIN)),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    _ = current_user
    return profile_service.get_profile(db, user_id)

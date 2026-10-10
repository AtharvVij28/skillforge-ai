"""Admin routes — live account directory (not demo data)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_role
from app.models.user import User
from app.schemas.admin import AdminUserListResponse
from app.services import admin_service
from app.services.role_service import ROLE_ADMIN

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/test")
def admin_test(current_user: User = Depends(require_role(ROLE_ADMIN))) -> dict[str, str]:
    return {
        "message": "Admin access granted",
        "role": current_user.role.code,
        "email": current_user.email,
    }


@router.get("/users", response_model=AdminUserListResponse)
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(require_role(ROLE_ADMIN)),
    db: Session = Depends(get_db),
) -> AdminUserListResponse:
    _ = current_user
    return admin_service.list_registered_accounts(db, page=page, page_size=page_size)

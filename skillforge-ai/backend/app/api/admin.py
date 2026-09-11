"""Admin verification routes (Phase 3 scaffold only)."""

from fastapi import APIRouter, Depends

from app.dependencies.auth import require_role
from app.models.user import User
from app.services.role_service import ROLE_ADMIN

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/test")
def admin_test(current_user: User = Depends(require_role(ROLE_ADMIN))) -> dict[str, str]:
    return {
        "message": "Admin access granted",
        "role": current_user.role.code,
        "email": current_user.email,
    }

"""Learner verification routes (Phase 3 scaffold only)."""

from fastapi import APIRouter, Depends

from app.dependencies.auth import require_role
from app.models.user import User
from app.services.role_service import ROLE_LEARNER

router = APIRouter(prefix="/learner", tags=["learner"])


@router.get("/test")
def learner_test(current_user: User = Depends(require_role(ROLE_LEARNER))) -> dict[str, str]:
    return {
        "message": "Learner access granted",
        "role": current_user.role.code,
        "email": current_user.email,
    }

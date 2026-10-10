"""Admin user directory service."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.user import User
from app.schemas.admin import AdminUserListResponse, AdminUserSummary


def list_registered_accounts(
    db: Session, *, page: int = 1, page_size: int = 50
) -> AdminUserListResponse:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    total = int(db.scalar(select(func.count()).select_from(User)) or 0)
    rows = db.scalars(
        select(User)
        .options(joinedload(User.role), joinedload(User.department), joinedload(User.profile))
        .order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return AdminUserListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[
            AdminUserSummary(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role_code=user.role.code if user.role else "",
                role_name=user.role.name if user.role else "",
                is_active=user.is_active,
                department_name=user.department.name if user.department else None,
                job_role=user.profile.job_role if user.profile else None,
                last_login_at=user.last_login_at,
                created_at=user.created_at,
            )
            for user in rows
        ],
    )

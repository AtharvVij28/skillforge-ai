"""Role constants and seed helpers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import Role

ROLE_LEARNER = "LEARNER"
ROLE_ADMIN = "ADMIN"

DEFAULT_ROLES: tuple[tuple[str, str, str], ...] = (
    (ROLE_LEARNER, "Learner", "Standard learner account"),
    (ROLE_ADMIN, "Administrator", "Platform administrator"),
)


def ensure_default_roles(db: Session) -> dict[str, Role]:
    """Idempotently create LEARNER and ADMIN roles. Returns code -> Role map."""
    existing = {
        role.code: role
        for role in db.scalars(select(Role).where(Role.code.in_([ROLE_LEARNER, ROLE_ADMIN]))).all()
    }
    created = False
    for code, name, description in DEFAULT_ROLES:
        if code not in existing:
            role = Role(code=code, name=name, description=description)
            db.add(role)
            existing[code] = role
            created = True
    if created:
        db.commit()
        for code in list(existing):
            db.refresh(existing[code])
    return existing


def get_role_by_code(db: Session, code: str) -> Role | None:
    return db.scalar(select(Role).where(Role.code == code))

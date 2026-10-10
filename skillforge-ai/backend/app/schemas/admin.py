"""Admin API schemas. Never include password hashes."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class AdminUserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str
    role_code: str
    role_name: str
    is_active: bool
    department_name: str | None = None
    job_role: str | None = None
    last_login_at: datetime | None = None
    created_at: datetime | None = None


class AdminUserListResponse(BaseModel):
    items: list[AdminUserSummary]
    total: int
    page: int
    page_size: int

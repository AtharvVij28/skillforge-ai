"""Profile and department API schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class DepartmentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    department_id: UUID | None = None
    designation: str | None = Field(default=None, max_length=255)
    job_role: str | None = Field(default=None, max_length=255)
    assignment: str | None = None
    education: str | None = None
    years_of_experience: int | None = Field(default=None, ge=0, le=60)
    technical_skills: list[str] | None = None
    statistical_skills: list[str] | None = None
    digital_skills: list[str] | None = None
    managerial_skills: list[str] | None = None
    behavioural_skills: list[str] | None = None
    previous_training: list[str] | None = None
    career_goals: str | None = None


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    email: EmailStr
    full_name: str
    role_code: str
    is_active: bool
    department: DepartmentSummary | None = None
    designation: str | None = None
    job_role: str | None = None
    assignment: str | None = None
    education: str | None = None
    years_of_experience: int | None = None
    technical_skills: list[str] = Field(default_factory=list)
    statistical_skills: list[str] = Field(default_factory=list)
    digital_skills: list[str] = Field(default_factory=list)
    managerial_skills: list[str] = Field(default_factory=list)
    behavioural_skills: list[str] = Field(default_factory=list)
    previous_training: list[str] = Field(default_factory=list)
    career_goals: str | None = None
    profile_completion_pct: int
    updated_at: datetime | None = None


class ProfileCompletionResponse(BaseModel):
    profile_completion_pct: int
    filled_fields: int
    total_fields: int
    missing_fields: list[str]


class DepartmentListResponse(BaseModel):
    items: list[DepartmentSummary]

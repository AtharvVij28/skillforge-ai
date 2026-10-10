"""Competency framework API schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreateRequest(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None
    sort_order: int = 0


class CategoryUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
    sort_order: int | None = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    description: str | None = None
    sort_order: int


class CompetencyCreateRequest(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    category_id: UUID
    description: str | None = None
    proficiency_levels: Any | None = None
    default_priority: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH)$")
    is_active: bool = True


class CompetencyUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    category_id: UUID | None = None
    description: str | None = None
    proficiency_levels: Any | None = None
    default_priority: str | None = Field(default=None, pattern="^(LOW|MEDIUM|HIGH)$")
    is_active: bool | None = None


class CompetencyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    category_id: UUID
    category_code: str
    category_name: str
    description: str | None = None
    proficiency_levels: Any | None = None
    default_priority: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class FrameworkCategoryResponse(BaseModel):
    id: UUID
    code: str
    name: str
    description: str | None = None
    sort_order: int
    competencies: list[CompetencyResponse]


class FrameworkResponse(BaseModel):
    categories: list[FrameworkCategoryResponse]


class CompetencyListResponse(BaseModel):
    items: list[CompetencyResponse]
    total: int
    page: int
    page_size: int


class RoleRequirementItem(BaseModel):
    role_code: str = Field(min_length=2, max_length=128)
    department_id: UUID | None = None
    competency_id: UUID
    required_score: Decimal = Field(ge=0, le=100)
    priority: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH)$")
    relevance_weight: Decimal = Field(default=Decimal("1.00"), ge=0, le=10)


class RoleRequirementUpsertRequest(BaseModel):
    items: list[RoleRequirementItem] = Field(min_length=1)


class RoleRequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role_code: str
    department_id: UUID | None = None
    competency_id: UUID
    competency_code: str
    competency_name: str
    required_score: Decimal
    priority: str
    relevance_weight: Decimal

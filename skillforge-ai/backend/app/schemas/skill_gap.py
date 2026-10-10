"""Skill-gap API schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserCompetencyScore(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    competency_id: UUID
    competency_code: str
    competency_name: str
    current_score: Decimal
    confidence: Decimal
    source: str
    last_assessed_at: datetime | None = None


class UserCompetencyListResponse(BaseModel):
    items: list[UserCompetencyScore]
    profile_completion_pct: int
    job_role: str | None = None
    has_assessment: bool = False


class SkillGapItem(BaseModel):
    competency_id: UUID
    competency_code: str
    competency_name: str
    current_score: Decimal
    required_score: Decimal
    gap: Decimal
    priority: str
    confidence: Decimal
    source: str
    status: str
    explanation: str


class SkillGapAnalysisResponse(BaseModel):
    analysis_id: UUID | None = None
    user_id: UUID
    job_role: str | None = None
    profile_completion_pct: int
    computed_at: datetime | None = None
    message: str | None = None
    open_gaps: int
    items: list[SkillGapItem] = Field(default_factory=list)

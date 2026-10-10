"""Learning path and resource schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class LearningResourceOut(BaseModel):
    id: UUID
    title: str
    provider: str
    description: str | None = None
    url: str | None = None
    estimated_hours: Decimal | None = None
    difficulty: str | None = None
    is_mock: bool
    competency_code: str | None = None
    competency_name: str | None = None


class RecommendationOut(BaseModel):
    id: UUID
    rank: int
    title: str
    provider: str
    url: str | None = None
    competency_code: str
    competency_name: str
    gap_at_generation: Decimal | None = None
    relevance_score: Decimal
    estimated_effort_hours: Decimal | None = None
    reason: str
    expected_benefit: str | None = None
    is_mock: bool
    status: str


class LearningPathResponse(BaseModel):
    job_role: str | None = None
    message: str | None = None
    items: list[RecommendationOut] = Field(default_factory=list)

"""Assessment API schemas. Correct answers are omitted until an attempt is submitted."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class QuestionOption(BaseModel):
    key: str
    text: str


class AssessmentQuestionOut(BaseModel):
    id: UUID
    stem: str
    options: list[QuestionOption]
    competency_code: str
    competency_name: str
    points: Decimal
    correct_option: str | None = None
    explanation: str | None = None


class AssessmentSummary(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    is_published: bool
    question_count: int
    generation_method: str
    created_at: datetime | None = None


class AssessmentDetail(AssessmentSummary):
    questions: list[AssessmentQuestionOut]


class GenerateAssessmentRequest(BaseModel):
    question_count: int = Field(default=5, ge=3, le=12)
    competency_codes: list[str] = Field(default_factory=list)


class StartAttemptResponse(BaseModel):
    attempt_id: UUID
    assessment_id: UUID
    status: str
    questions: list[AssessmentQuestionOut]


class AnswerSubmission(BaseModel):
    question_id: UUID
    selected_option: str = Field(min_length=1, max_length=8)


class SubmitAttemptRequest(BaseModel):
    answers: list[AnswerSubmission] = Field(min_length=1)


class CompetencyBreakdownItem(BaseModel):
    competency_id: UUID
    competency_code: str
    competency_name: str
    percent_correct: Decimal
    previous_score: Decimal | None = None
    updated_score: Decimal


class AttemptResult(BaseModel):
    attempt_id: UUID
    assessment_id: UUID
    status: str
    total_score: Decimal | None = None
    percentage: Decimal | None = None
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    feedback_summary: str | None = None
    next_action: str | None = None
    competency_breakdown: list[CompetencyBreakdownItem] = Field(default_factory=list)
    questions: list[AssessmentQuestionOut] = Field(default_factory=list)
    submitted_at: datetime | None = None

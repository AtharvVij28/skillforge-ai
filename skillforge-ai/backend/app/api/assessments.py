"""Assessment generation, attempts, and scoring routes."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_current_user
from app.models.user import User
from app.schemas.assessment import (
    AssessmentDetail,
    AssessmentSummary,
    GenerateAssessmentRequest,
    StartAttemptResponse,
    SubmitAttemptRequest,
    AttemptResult,
)
from app.services import assessment_service

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("/generate", response_model=AssessmentDetail)
def generate_assessment(
    payload: GenerateAssessmentRequest | None = None,
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> AssessmentDetail:
    body = payload or GenerateAssessmentRequest()
    return assessment_service.generate_assessment(db, current_user, body)


@router.get("", response_model=list[AssessmentSummary])
def list_assessments(
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> list[AssessmentSummary]:
    return assessment_service.list_assessments(db, current_user.id)


@router.post("/attempts/{attempt_id}/submit", response_model=AttemptResult)
def submit_attempt(
    attempt_id: UUID,
    payload: SubmitAttemptRequest,
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> AttemptResult:
    return assessment_service.submit_attempt(db, current_user.id, attempt_id, payload.answers)


@router.get("/attempts/{attempt_id}", response_model=AttemptResult)
def get_attempt(
    attempt_id: UUID,
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> AttemptResult:
    return assessment_service.get_attempt(db, current_user.id, attempt_id)


@router.post("/{assessment_id}/start", response_model=StartAttemptResponse)
def start_assessment(
    assessment_id: UUID,
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> StartAttemptResponse:
    return assessment_service.start_attempt(db, current_user.id, assessment_id)


@router.get("/{assessment_id}", response_model=AssessmentDetail)
def get_assessment(
    assessment_id: UUID,
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> AssessmentDetail:
    return assessment_service.get_assessment(db, current_user.id, assessment_id, reveal=False)

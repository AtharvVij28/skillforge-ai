"""Skill scores and explainable gap analysis routes."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_current_user, require_role
from app.models.user import User
from app.schemas.skill_gap import SkillGapAnalysisResponse, UserCompetencyListResponse
from app.services import skill_gap_service
from app.services.role_service import ROLE_ADMIN

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/me", response_model=UserCompetencyListResponse)
def get_my_scores(
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> UserCompetencyListResponse:
    return skill_gap_service.get_user_scores(db, current_user.id)


@router.post("/gaps/analyze", response_model=SkillGapAnalysisResponse)
def analyze_my_gaps(
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> SkillGapAnalysisResponse:
    return skill_gap_service.analyze_gaps(db, current_user.id)


@router.get("/gaps", response_model=SkillGapAnalysisResponse)
def get_my_gaps(
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> SkillGapAnalysisResponse:
    return skill_gap_service.get_latest_gaps(db, current_user.id)


@router.get("/gaps/{user_id}", response_model=SkillGapAnalysisResponse)
def get_user_gaps(
    user_id: UUID,
    current_user: User = Depends(require_role(ROLE_ADMIN)),
    db: Session = Depends(get_db),
) -> SkillGapAnalysisResponse:
    _ = current_user
    return skill_gap_service.get_latest_gaps(db, user_id)

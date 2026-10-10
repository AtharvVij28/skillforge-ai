"""Learning path routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_current_user
from app.models.user import User
from app.schemas.learning import LearningPathResponse
from app.services import recommendation_service

router = APIRouter(prefix="/learning", tags=["learning"])


@router.get("/path", response_model=LearningPathResponse)
def get_path(
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> LearningPathResponse:
    return recommendation_service.get_learning_path(db, current_user.id)


@router.post("/path/generate", response_model=LearningPathResponse)
def generate_path(
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> LearningPathResponse:
    return recommendation_service.generate_learning_path(db, current_user.id)

"""Competency framework API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_current_user, require_role
from app.models.competency import CompetencyCategory
from app.models.user import User
from app.schemas.competency import (
    CategoryResponse,
    CompetencyCreateRequest,
    CompetencyListResponse,
    CompetencyResponse,
    CompetencyUpdateRequest,
    FrameworkResponse,
    RoleRequirementResponse,
    RoleRequirementUpsertRequest,
)
from app.services import competency_service
from app.services.role_service import ROLE_ADMIN

router = APIRouter(prefix="/competencies", tags=["competencies"])


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> list[CompetencyCategory]:
    _ = current_user
    return competency_service.list_categories(db)


@router.get("/framework", response_model=FrameworkResponse)
def get_framework(
    include_inactive: bool = False,
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> FrameworkResponse:
    _ = current_user
    return competency_service.get_framework(db, include_inactive=include_inactive)


@router.get("/role-requirements", response_model=list[RoleRequirementResponse])
def list_role_requirements(
    role_code: str | None = None,
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> list[RoleRequirementResponse]:
    _ = current_user
    return competency_service.list_role_requirements(db, role_code=role_code)


@router.put("/role-requirements", response_model=list[RoleRequirementResponse])
def upsert_role_requirements(
    payload: RoleRequirementUpsertRequest,
    current_user: User = Depends(require_role(ROLE_ADMIN)),
    db: Session = Depends(get_db),
) -> list[RoleRequirementResponse]:
    _ = current_user
    return competency_service.upsert_role_requirements(db, payload.items)


@router.get("", response_model=CompetencyListResponse)
def list_competencies(
    category_id: UUID | None = None,
    include_inactive: bool = False,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> CompetencyListResponse:
    _ = current_user
    return competency_service.list_competencies(
        db,
        category_id=category_id,
        include_inactive=include_inactive,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=CompetencyResponse, status_code=201)
def create_competency(
    payload: CompetencyCreateRequest,
    current_user: User = Depends(require_role(ROLE_ADMIN)),
    db: Session = Depends(get_db),
) -> CompetencyResponse:
    _ = current_user
    return competency_service.create_competency(db, payload)


@router.get("/{competency_id}", response_model=CompetencyResponse)
def get_competency(
    competency_id: UUID,
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> CompetencyResponse:
    _ = current_user
    return competency_service.get_competency(db, competency_id)


@router.put("/{competency_id}", response_model=CompetencyResponse)
def update_competency(
    competency_id: UUID,
    payload: CompetencyUpdateRequest,
    current_user: User = Depends(require_role(ROLE_ADMIN)),
    db: Session = Depends(get_db),
) -> CompetencyResponse:
    _ = current_user
    return competency_service.update_competency(db, competency_id, payload)


@router.delete("/{competency_id}", response_model=CompetencyResponse)
def deactivate_competency(
    competency_id: UUID,
    current_user: User = Depends(require_role(ROLE_ADMIN)),
    db: Session = Depends(get_db),
) -> CompetencyResponse:
    _ = current_user
    return competency_service.deactivate_competency(db, competency_id)

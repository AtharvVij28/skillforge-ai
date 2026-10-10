"""Competency framework service (Phase 4)."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.competency import Competency, CompetencyCategory, RoleCompetency
from app.models.user import Department
from app.schemas.competency import (
    CompetencyCreateRequest,
    CompetencyListResponse,
    CompetencyResponse,
    CompetencyUpdateRequest,
    FrameworkCategoryResponse,
    FrameworkResponse,
    RoleRequirementItem,
    RoleRequirementResponse,
)

DEFAULT_PROFICIENCY_LEVELS = [
    {"level": 1, "label": "Awareness", "min_score": 0},
    {"level": 2, "label": "Working knowledge", "min_score": 40},
    {"level": 3, "label": "Proficient", "min_score": 60},
    {"level": 4, "label": "Advanced", "min_score": 80},
    {"level": 5, "label": "Expert", "min_score": 90},
]


def _to_competency_response(item: Competency) -> CompetencyResponse:
    return CompetencyResponse(
        id=item.id,
        code=item.code,
        name=item.name,
        category_id=item.category_id,
        category_code=item.category.code if item.category else "",
        category_name=item.category.name if item.category else "",
        description=item.description,
        proficiency_levels=item.proficiency_levels,
        default_priority=item.default_priority,
        is_active=item.is_active,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def list_categories(db: Session) -> list[CompetencyCategory]:
    return list(
        db.scalars(select(CompetencyCategory).order_by(CompetencyCategory.sort_order, CompetencyCategory.name)).all()
    )


def list_competencies(
    db: Session,
    *,
    category_id: UUID | None = None,
    include_inactive: bool = False,
    page: int = 1,
    page_size: int = 50,
) -> CompetencyListResponse:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)

    query = select(Competency).options(joinedload(Competency.category))
    count_query = select(func.count()).select_from(Competency)
    if category_id is not None:
        query = query.where(Competency.category_id == category_id)
        count_query = count_query.where(Competency.category_id == category_id)
    if not include_inactive:
        query = query.where(Competency.is_active.is_(True))
        count_query = count_query.where(Competency.is_active.is_(True))

    total = int(db.scalar(count_query) or 0)
    items = db.scalars(
        query.order_by(Competency.name).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return CompetencyListResponse(
        items=[_to_competency_response(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


def get_framework(db: Session, *, include_inactive: bool = False) -> FrameworkResponse:
    categories = list_categories(db)
    competency_query = select(Competency).options(joinedload(Competency.category))
    if not include_inactive:
        competency_query = competency_query.where(Competency.is_active.is_(True))
    competencies = db.scalars(competency_query.order_by(Competency.name)).all()
    grouped: dict[UUID, list[Competency]] = {}
    for item in competencies:
        grouped.setdefault(item.category_id, []).append(item)

    return FrameworkResponse(
        categories=[
            FrameworkCategoryResponse(
                id=category.id,
                code=category.code,
                name=category.name,
                description=category.description,
                sort_order=category.sort_order,
                competencies=[_to_competency_response(item) for item in grouped.get(category.id, [])],
            )
            for category in categories
        ]
    )


def get_competency(db: Session, competency_id: UUID) -> CompetencyResponse:
    item = db.scalar(
        select(Competency).options(joinedload(Competency.category)).where(Competency.id == competency_id)
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competency not found")
    return _to_competency_response(item)


def create_competency(db: Session, payload: CompetencyCreateRequest) -> CompetencyResponse:
    code = payload.code.strip().upper()
    existing = db.scalar(select(Competency).where(Competency.code == code))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Competency code already exists")

    category = db.scalar(select(CompetencyCategory).where(CompetencyCategory.id == payload.category_id))
    if category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown category")

    item = Competency(
        code=code,
        name=payload.name.strip(),
        category_id=category.id,
        description=payload.description,
        proficiency_levels=payload.proficiency_levels or DEFAULT_PROFICIENCY_LEVELS,
        default_priority=payload.default_priority,
        is_active=payload.is_active,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    item = db.scalar(
        select(Competency).options(joinedload(Competency.category)).where(Competency.id == item.id)
    )
    assert item is not None
    return _to_competency_response(item)


def update_competency(
    db: Session, competency_id: UUID, payload: CompetencyUpdateRequest
) -> CompetencyResponse:
    item = db.scalar(
        select(Competency).options(joinedload(Competency.category)).where(Competency.id == competency_id)
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competency not found")

    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data and data["category_id"] is not None:
        category = db.scalar(select(CompetencyCategory).where(CompetencyCategory.id == data["category_id"]))
        if category is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown category")
        item.category_id = category.id
    if "name" in data and data["name"] is not None:
        item.name = data["name"].strip()
    if "description" in data:
        item.description = data["description"]
    if "proficiency_levels" in data:
        item.proficiency_levels = data["proficiency_levels"]
    if "default_priority" in data and data["default_priority"] is not None:
        item.default_priority = data["default_priority"]
    if "is_active" in data and data["is_active"] is not None:
        item.is_active = data["is_active"]

    db.add(item)
    db.commit()
    return get_competency(db, competency_id)


def deactivate_competency(db: Session, competency_id: UUID) -> CompetencyResponse:
    return update_competency(db, competency_id, CompetencyUpdateRequest(is_active=False))


def upsert_role_requirements(
    db: Session, items: list[RoleRequirementItem]
) -> list[RoleRequirementResponse]:
    saved: list[RoleCompetency] = []
    for item in items:
        if item.department_id is not None:
            department = db.scalar(select(Department).where(Department.id == item.department_id))
            if department is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown department")

        competency = db.scalar(select(Competency).where(Competency.id == item.competency_id))
        if competency is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown competency")

        query = select(RoleCompetency).where(
            RoleCompetency.role_code == item.role_code.strip().upper(),
            RoleCompetency.competency_id == item.competency_id,
        )
        if item.department_id is None:
            query = query.where(RoleCompetency.department_id.is_(None))
        else:
            query = query.where(RoleCompetency.department_id == item.department_id)

        existing = db.scalar(query)
        if existing is None:
            existing = RoleCompetency(
                role_code=item.role_code.strip().upper(),
                department_id=item.department_id,
                competency_id=item.competency_id,
            )
        existing.required_score = item.required_score
        existing.priority = item.priority
        existing.relevance_weight = item.relevance_weight
        db.add(existing)
        saved.append(existing)

    db.commit()
    return list_role_requirements(
        db,
        role_code=items[0].role_code.strip().upper(),
        department_id=items[0].department_id,
    )


def list_role_requirements(
    db: Session,
    *,
    role_code: str | None = None,
    department_id: UUID | None = None,
) -> list[RoleRequirementResponse]:
    query = select(RoleCompetency).options(joinedload(RoleCompetency.competency))
    if role_code:
        query = query.where(RoleCompetency.role_code == role_code.strip().upper())
    if department_id is not None:
        query = query.where(RoleCompetency.department_id == department_id)
    rows = db.scalars(query.order_by(RoleCompetency.role_code)).all()
    return [
        RoleRequirementResponse(
            id=row.id,
            role_code=row.role_code,
            department_id=row.department_id,
            competency_id=row.competency_id,
            competency_code=row.competency.code if row.competency else "",
            competency_name=row.competency.name if row.competency else "",
            required_score=row.required_score,
            priority=row.priority,
            relevance_weight=row.relevance_weight,
        )
        for row in rows
    ]

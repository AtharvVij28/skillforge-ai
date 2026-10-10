"""Living user profile service (Phase 4)."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.user import Department, User, UserProfile
from app.schemas.profile import (
    DepartmentSummary,
    ProfileCompletionResponse,
    ProfileResponse,
    ProfileUpdateRequest,
)

COMPLETION_FIELDS: tuple[str, ...] = (
    "full_name",
    "department_id",
    "designation",
    "job_role",
    "assignment",
    "education",
    "years_of_experience",
    "technical_skills",
    "statistical_skills",
    "digital_skills",
    "managerial_skills",
    "behavioural_skills",
    "previous_training",
    "career_goals",
)


def _as_str_list(value: object | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [part.strip() for part in value.split(",") if part.strip()]
    return []


def _is_filled(value: object | None) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return len(_as_str_list(value)) > 0
    if isinstance(value, int):
        return True
    return True


def compute_profile_completion(user: User, profile: UserProfile) -> tuple[int, list[str], int, int]:
    values: dict[str, object | None] = {
        "full_name": user.full_name,
        "department_id": user.department_id,
        "designation": profile.designation,
        "job_role": profile.job_role,
        "assignment": profile.assignment,
        "education": profile.education,
        "years_of_experience": profile.years_of_experience,
        "technical_skills": profile.technical_skills,
        "statistical_skills": profile.statistical_skills,
        "digital_skills": profile.digital_skills,
        "managerial_skills": profile.managerial_skills,
        "behavioural_skills": profile.behavioural_skills,
        "previous_training": profile.previous_training,
        "career_goals": profile.career_goals,
    }
    missing = [name for name in COMPLETION_FIELDS if not _is_filled(values.get(name))]
    total = len(COMPLETION_FIELDS)
    filled = total - len(missing)
    pct = round((filled / total) * 100) if total else 0
    return pct, missing, filled, total


def ensure_profile(db: Session, user: User) -> UserProfile:
    if user.profile is not None:
        return user.profile
    profile = UserProfile(user_id=user.id, profile_completion_pct=0)
    db.add(profile)
    db.flush()
    user.profile = profile
    return profile


def _refresh_completion(db: Session, user: User, profile: UserProfile) -> int:
    pct, _, _, _ = compute_profile_completion(user, profile)
    profile.profile_completion_pct = pct
    db.add(profile)
    return pct


def to_profile_response(user: User) -> ProfileResponse:
    profile = user.profile
    assert profile is not None
    department = None
    if user.department is not None:
        department = DepartmentSummary.model_validate(user.department)
    return ProfileResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role_code=user.role.code if user.role else "",
        is_active=user.is_active,
        department=department,
        designation=profile.designation,
        job_role=profile.job_role,
        assignment=profile.assignment,
        education=profile.education,
        years_of_experience=profile.years_of_experience,
        technical_skills=_as_str_list(profile.technical_skills),
        statistical_skills=_as_str_list(profile.statistical_skills),
        digital_skills=_as_str_list(profile.digital_skills),
        managerial_skills=_as_str_list(profile.managerial_skills),
        behavioural_skills=_as_str_list(profile.behavioural_skills),
        previous_training=_as_str_list(profile.previous_training),
        career_goals=profile.career_goals,
        profile_completion_pct=profile.profile_completion_pct,
        updated_at=profile.updated_at,
    )


def _load_user(db: Session, user_id: UUID) -> User | None:
    return db.scalar(
        select(User)
        .options(
            joinedload(User.role),
            joinedload(User.department),
            joinedload(User.profile),
        )
        .where(User.id == user_id)
    )


def get_profile(db: Session, user_id: UUID) -> ProfileResponse:
    user = _load_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    ensure_profile(db, user)
    _refresh_completion(db, user, user.profile)
    db.commit()
    user = _load_user(db, user_id)
    assert user is not None
    return to_profile_response(user)


def get_completion(db: Session, user_id: UUID) -> ProfileCompletionResponse:
    user = _load_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    profile = ensure_profile(db, user)
    pct, missing, filled, total = compute_profile_completion(user, profile)
    profile.profile_completion_pct = pct
    db.add(profile)
    db.commit()
    return ProfileCompletionResponse(
        profile_completion_pct=pct,
        filled_fields=filled,
        total_fields=total,
        missing_fields=missing,
    )


def update_profile(db: Session, user_id: UUID, payload: ProfileUpdateRequest) -> ProfileResponse:
    user = _load_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    profile = ensure_profile(db, user)

    data = payload.model_dump(exclude_unset=True)

    if "full_name" in data and data["full_name"] is not None:
        user.full_name = data["full_name"].strip()

    if "department_id" in data:
        department_id = data["department_id"]
        if department_id is None:
            user.department_id = None
        else:
            department = db.scalar(select(Department).where(Department.id == department_id))
            if department is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unknown department",
                )
            user.department_id = department.id

    for field in (
        "designation",
        "job_role",
        "assignment",
        "education",
        "career_goals",
    ):
        if field in data:
            value = data[field]
            setattr(profile, field, value.strip() if isinstance(value, str) else value)

    if "years_of_experience" in data:
        profile.years_of_experience = data["years_of_experience"]

    for field in (
        "technical_skills",
        "statistical_skills",
        "digital_skills",
        "managerial_skills",
        "behavioural_skills",
        "previous_training",
    ):
        if field in data:
            setattr(profile, field, _as_str_list(data[field]))

    _refresh_completion(db, user, profile)
    db.add(user)
    db.add(profile)
    db.commit()
    user = _load_user(db, user_id)
    assert user is not None
    return to_profile_response(user)


def list_departments(db: Session) -> list[DepartmentSummary]:
    rows = db.scalars(select(Department).order_by(Department.name)).all()
    return [DepartmentSummary.model_validate(row) for row in rows]

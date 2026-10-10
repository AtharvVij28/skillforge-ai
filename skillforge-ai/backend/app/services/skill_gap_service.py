"""Deterministic, explainable skill-gap engine (Phase 5).

Scoring is rule-based. No LLM is used. Raw numeric factors stay in the snapshot
so explanations can be audited later.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.competency import Competency, RoleCompetency, UserCompetency
from app.models.skill_gap import SkillGapSnapshot
from app.models.user import User
from app.schemas.skill_gap import (
    SkillGapAnalysisResponse,
    SkillGapItem,
    UserCompetencyListResponse,
    UserCompetencyScore,
)
from app.services.profile_service import compute_profile_completion, ensure_profile

INTEREST_REQUIRED_SCORE = Decimal("75.00")
TWO_PLACES = Decimal("0.01")


def _q(value: Decimal | float | int) -> Decimal:
    return Decimal(str(value)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def _normalize_role(job_role: str | None) -> str | None:
    if not job_role or not job_role.strip():
        return None
    return job_role.strip().upper().replace(" ", "_")


def _skill_tokens(profile) -> set[str]:
    bags = [
        profile.technical_skills,
        profile.statistical_skills,
        profile.digital_skills,
        profile.managerial_skills,
        profile.behavioural_skills,
        profile.previous_training,
    ]
    tokens: set[str] = set()
    for bag in bags:
        if not isinstance(bag, list):
            continue
        for item in bag:
            text = str(item).strip().lower()
            if text:
                tokens.add(text)
                tokens.update(part for part in text.replace("&", " ").replace("-", " ").split() if len(part) > 2)
    return tokens


def _competency_matches_profile(competency: Competency, tokens: set[str]) -> bool:
    haystack = f"{competency.code} {competency.name}".lower().replace("_", " ").replace("&", " ")
    words = [word for word in haystack.split() if len(word) > 2]
    return any(word in tokens or any(word in token for token in tokens) for word in words)


def _estimate_current_score(
    competency: Competency,
    existing: UserCompetency | None,
    tokens: set[str],
    years: int | None,
    completion_pct: int,
) -> tuple[Decimal, Decimal, str]:
    if existing is not None and existing.source in {"ASSESSMENT", "MANUAL"}:
        return _q(existing.current_score), _q(existing.confidence), existing.source

    if existing is not None and existing.source == "PROFILE" and existing.current_score > 0:
        confidence = max(_q(existing.confidence), _q(completion_pct / 200))
        return _q(existing.current_score), confidence, "PROFILE"

    matched = _competency_matches_profile(competency, tokens)
    years_bonus = min(max(years or 0, 0), 12) * 1.5
    if matched:
        score = min(62.0, 38.0 + years_bonus)
        confidence = min(0.55, 0.25 + completion_pct / 250)
        return _q(score), _q(confidence), "PROFILE"

    score = min(28.0, 12.0 + years_bonus * 0.4)
    confidence = min(0.35, 0.12 + completion_pct / 400)
    return _q(score), _q(confidence), "PROFILE"


def _priority(gap: Decimal, requirement_priority: str, weight: Decimal) -> str:
    if gap <= 0:
        return "LOW"
    weighted = float(gap) * float(weight)
    req = requirement_priority.upper()
    if weighted >= 25 or (req == "HIGH" and gap >= 15):
        return "HIGH"
    if weighted >= 12 or req == "HIGH":
        return "MEDIUM"
    return "LOW"


def _explanation(
    *,
    name: str,
    current: Decimal,
    required: Decimal,
    gap: Decimal,
    job_role: str,
    source: str,
    completion_pct: int,
) -> str:
    if gap <= 0:
        return (
            f"Your current estimate for {name} is {current}, which meets the {required} "
            f"required for {job_role}. Source: {source}. Profile completeness: {completion_pct}%."
        )
    return (
        f"Your current competency estimate for {name} is {current}. The {job_role} role requires "
        f"{required}. The gap is {gap} points. This is a rule-based comparison of required vs current "
        f"score (source: {source}), not an opaque AI judgment. Profile completeness: {completion_pct}%."
    )


def _load_user(db: Session, user_id: UUID) -> User:
    user = db.scalar(
        select(User)
        .options(joinedload(User.profile), joinedload(User.department), joinedload(User.role))
        .where(User.id == user_id)
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    ensure_profile(db, user)
    return user


def _requirements_for_role(
    db: Session, job_role: str, department_id: UUID | None
) -> list[RoleCompetency]:
    rows = db.scalars(
        select(RoleCompetency)
        .options(joinedload(RoleCompetency.competency).joinedload(Competency.category))
        .where(RoleCompetency.role_code == job_role)
    ).all()
    if not rows:
        return []
    if department_id is None:
        return [row for row in rows if row.department_id is None] or list(rows)
    scoped = [row for row in rows if row.department_id == department_id]
    return scoped or [row for row in rows if row.department_id is None]


def get_user_scores(db: Session, user_id: UUID) -> UserCompetencyListResponse:
    user = _load_user(db, user_id)
    profile = user.profile
    assert profile is not None
    pct, _, _, _ = compute_profile_completion(user, profile)
    rows = db.scalars(
        select(UserCompetency)
        .options(joinedload(UserCompetency.competency))
        .where(UserCompetency.user_id == user_id)
    ).all()
    return UserCompetencyListResponse(
        job_role=_normalize_role(profile.job_role),
        profile_completion_pct=pct,
        has_assessment=any(row.source == "ASSESSMENT" for row in rows),
        items=[
            UserCompetencyScore(
                competency_id=row.competency_id,
                competency_code=row.competency.code if row.competency else "",
                competency_name=row.competency.name if row.competency else "",
                current_score=_q(row.current_score),
                confidence=_q(row.confidence),
                source=row.source,
                last_assessed_at=row.last_assessed_at,
            )
            for row in rows
        ],
    )


def _latest_analysis_id(db: Session, user_id: UUID) -> UUID | None:
    latest = db.scalar(
        select(SkillGapSnapshot)
        .where(SkillGapSnapshot.user_id == user_id)
        .order_by(SkillGapSnapshot.computed_at.desc())
        .limit(1)
    )
    return latest.analysis_id if latest else None


def get_latest_gaps(db: Session, user_id: UUID) -> SkillGapAnalysisResponse:
    user = _load_user(db, user_id)
    profile = user.profile
    assert profile is not None
    pct, _, _, _ = compute_profile_completion(user, profile)
    analysis_id = _latest_analysis_id(db, user_id)
    if analysis_id is None:
        return SkillGapAnalysisResponse(
            analysis_id=None,
            user_id=user_id,
            job_role=_normalize_role(profile.job_role),
            profile_completion_pct=pct,
            computed_at=None,
            message="No skill-gap analysis yet. Run analyze to compute gaps against your job role.",
            open_gaps=0,
            items=[],
        )
    rows = db.scalars(
        select(SkillGapSnapshot)
        .options(joinedload(SkillGapSnapshot.competency))
        .where(
            SkillGapSnapshot.user_id == user_id,
            SkillGapSnapshot.analysis_id == analysis_id,
        )
    ).all()
    items = [_snapshot_to_item(row) for row in rows]
    items.sort(key=lambda item: (item.status != "GAP", -float(item.gap), item.competency_name))
    return SkillGapAnalysisResponse(
        analysis_id=analysis_id,
        user_id=user_id,
        job_role=_normalize_role(profile.job_role),
        profile_completion_pct=pct,
        computed_at=rows[0].computed_at if rows else None,
        message=None,
        open_gaps=sum(1 for item in items if item.status == "GAP"),
        items=items,
    )


def analyze_gaps(db: Session, user_id: UUID) -> SkillGapAnalysisResponse:
    user = _load_user(db, user_id)
    profile = user.profile
    assert profile is not None
    pct, _, _, _ = compute_profile_completion(user, profile)
    job_role = _normalize_role(profile.job_role)

    existing_scores = {
        row.competency_id: row
        for row in db.scalars(
            select(UserCompetency)
            .options(joinedload(UserCompetency.competency))
            .where(UserCompetency.user_id == user_id)
        ).all()
    }

    role_requirements = _requirements_for_role(db, job_role, user.department_id) if job_role else []
    assessed = [row for row in existing_scores.values() if row.source == "ASSESSMENT" and row.competency]
    targets: list[tuple[Competency, Decimal, str, Decimal, str]] = []
    if role_requirements:
        for requirement in role_requirements:
            if requirement.competency is None or not requirement.competency.is_active:
                continue
            targets.append(
                (
                    requirement.competency,
                    _q(requirement.required_score),
                    requirement.priority,
                    requirement.relevance_weight,
                    job_role or "role",
                )
            )
    elif assessed:
        for row in assessed:
            targets.append(
                (
                    row.competency,
                    INTEREST_REQUIRED_SCORE,
                    "HIGH",
                    Decimal("1.00"),
                    "selected interests",
                )
            )
    elif job_role:
        return SkillGapAnalysisResponse(
            analysis_id=None,
            user_id=user_id,
            job_role=job_role,
            profile_completion_pct=pct,
            computed_at=datetime.now(timezone.utc),
            message=f"No competency requirements are configured for job role {job_role}.",
            open_gaps=0,
            items=[],
        )
    else:
        return SkillGapAnalysisResponse(
            analysis_id=None,
            user_id=user_id,
            job_role=job_role,
            profile_completion_pct=pct,
            computed_at=datetime.now(timezone.utc),
            message="Complete an assessment on your selected interests so we can calculate competency gaps.",
            open_gaps=0,
            items=[],
        )

    tokens = _skill_tokens(profile)
    analysis_id = uuid4()
    computed_at = datetime.now(timezone.utc)
    items: list[SkillGapItem] = []

    for competency, required, req_priority, weight, target_label in targets:
        existing = existing_scores.get(competency.id)
        if existing is not None and existing.source == "ASSESSMENT":
            current, confidence, source = _q(existing.current_score), _q(existing.confidence), existing.source
        else:
            current, confidence, source = _estimate_current_score(
                competency, existing, tokens, profile.years_of_experience, pct
            )
        gap = _q(max(Decimal("0.00"), required - current))
        priority = _priority(gap, req_priority, weight)
        status_label = "MET" if gap <= 0 else "GAP"
        explanation = _explanation(
            name=competency.name,
            current=current,
            required=required,
            gap=gap,
            job_role=target_label,
            source=source,
            completion_pct=pct,
        )

        if existing is None:
            existing = UserCompetency(
                user_id=user_id,
                competency_id=competency.id,
                source=source,
            )
        if existing.source != "ASSESSMENT":
            existing.current_score = current
            existing.confidence = confidence
            existing.source = source
            existing.explanation = explanation
        db.add(existing)

        snapshot = SkillGapSnapshot(
            analysis_id=analysis_id,
            user_id=user_id,
            competency_id=competency.id,
            job_role=job_role,
            current_score=current,
            required_score=required,
            gap=gap,
            priority=priority,
            confidence=confidence,
            source=source,
            explanation=explanation,
            computed_at=computed_at,
        )
        db.add(snapshot)
        items.append(
            SkillGapItem(
                competency_id=competency.id,
                competency_code=competency.code,
                competency_name=competency.name,
                current_score=current,
                required_score=required,
                gap=gap,
                priority=priority,
                confidence=confidence,
                source=source,
                status=status_label,
                explanation=explanation,
            )
        )

    db.commit()
    items.sort(key=lambda item: (item.status != "GAP", -float(item.gap), item.competency_name))
    return SkillGapAnalysisResponse(
        analysis_id=analysis_id,
        user_id=user_id,
        job_role=job_role,
        profile_completion_pct=pct,
        computed_at=computed_at,
        message=None,
        open_gaps=sum(1 for item in items if item.status == "GAP"),
        items=items,
    )


def _snapshot_to_item(row: SkillGapSnapshot) -> SkillGapItem:
    gap = _q(row.gap)
    return SkillGapItem(
        competency_id=row.competency_id,
        competency_code=row.competency.code if row.competency else "",
        competency_name=row.competency.name if row.competency else "",
        current_score=_q(row.current_score),
        required_score=_q(row.required_score),
        gap=gap,
        priority=row.priority,
        confidence=_q(row.confidence),
        source=row.source,
        status="MET" if gap <= 0 else "GAP",
        explanation=row.explanation,
    )

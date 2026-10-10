"""Rank study materials against current skill gaps."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.competency import Competency
from app.models.learning import LearningResource, Recommendation
from app.models.user import User
from app.schemas.learning import LearningPathResponse, RecommendationOut
from app.services.catalog_seed import ensure_learning_catalog
from app.services.email_service import frontend_base_url, send_learning_recommendation_email
from app.services.profile_service import ensure_profile
from app.services.skill_gap_service import analyze_gaps, get_latest_gaps


def generate_learning_path(db: Session, user_id: UUID) -> LearningPathResponse:
    ensure_learning_catalog(db)
    user = db.get(User, user_id)
    if user is None:
        return LearningPathResponse(items=[], message="User not found")
    ensure_profile(db, user)
    gaps = get_latest_gaps(db, user_id)
    if not gaps.items:
        gaps = analyze_gaps(db, user_id)

    open_gaps = [item for item in gaps.items if item.status == "GAP"]
    if not open_gaps:
        return LearningPathResponse(
            job_role=gaps.job_role,
            message="No open skill gaps right now. Keep practising or set a job role on your profile.",
            items=[],
        )

    resources = db.scalars(
        select(LearningResource).options(joinedload(LearningResource.competency_links))
    ).unique().all()
    competency_rows = {row.id: row for row in db.scalars(select(Competency)).all()}
    gap_by_competency = {item.competency_id: item for item in open_gaps}

    ranked: list[tuple[Decimal, LearningResource, UUID]] = []
    for resource in resources:
        for link in resource.competency_links:
            gap = gap_by_competency.get(link.competency_id)
            if gap is None:
                continue
            relevance = Decimal(str(gap.gap)) * Decimal(str(link.weight))
            ranked.append((relevance, resource, link.competency_id))

    ranked.sort(key=lambda row: row[0], reverse=True)
    seen_resources: set[UUID] = set()
    unique_ranked: list[tuple[Decimal, LearningResource, UUID]] = []
    for relevance, resource, competency_id in ranked:
        if resource.id in seen_resources:
            continue
        seen_resources.add(resource.id)
        unique_ranked.append((relevance, resource, competency_id))

    previous_top = None
    active_rows = db.scalars(
        select(Recommendation).where(
            Recommendation.user_id == user_id,
            Recommendation.status == "ACTIVE",
        )
    ).all()
    if active_rows:
        previous_top = min(active_rows, key=lambda row: row.rank).resource_id
    for row in active_rows:
        row.status = "SUPERSEDED"
        db.add(row)

    items: list[RecommendationOut] = []
    for index, (relevance, resource, competency_id) in enumerate(unique_ranked[:8], start=1):
        gap = gap_by_competency[competency_id]
        competency = competency_rows.get(competency_id)
        reason = (
            f"Recommended because your {gap.competency_name} score is {gap.current_score} "
            f"against a required {gap.required_score} (gap {gap.gap}). This resource targets that competency."
        )
        rec = Recommendation(
            user_id=user_id,
            resource_id=resource.id,
            competency_id=competency_id,
            relevance_score=min(Decimal("99.99"), relevance),
            gap_at_generation=gap.gap,
            expected_benefit=f"Close the {gap.competency_name} gap with structured study.",
            reason=reason,
            estimated_effort_hours=resource.estimated_hours,
            rank=index,
            status="ACTIVE",
        )
        db.add(rec)
        db.flush()
        items.append(
            RecommendationOut(
                id=rec.id,
                rank=index,
                title=resource.title,
                provider=resource.provider,
                url=resource.url,
                competency_code=competency.code if competency else gap.competency_code,
                competency_name=competency.name if competency else gap.competency_name,
                gap_at_generation=gap.gap,
                relevance_score=rec.relevance_score,
                estimated_effort_hours=resource.estimated_hours,
                reason=reason,
                expected_benefit=rec.expected_benefit,
                is_mock=resource.is_mock,
                status="ACTIVE",
            )
        )
    db.commit()
    if items:
        top = items[0]
        top_resource_id = unique_ranked[0][1].id
        if previous_top is None or top_resource_id != previous_top:
            hours = top.estimated_effort_hours
            duration = f"{hours} hours" if hours is not None else None
            gap = gap_by_competency.get(unique_ranked[0][2])
            send_learning_recommendation_email(
                to_email=user.email,
                full_name=user.full_name,
                user_id=user.id,
                learning_title=top.title,
                recommendation_reason=top.reason,
                competency_name=top.competency_name or None,
                current_level=str(gap.current_score) if gap else None,
                target_level=str(gap.required_score) if gap else None,
                estimated_duration=duration,
                next_action=top.expected_benefit,
                learning_url=f"{frontend_base_url()}/path",
            )
    return LearningPathResponse(job_role=gaps.job_role, items=items)


def get_learning_path(db: Session, user_id: UUID) -> LearningPathResponse:
    rows = db.scalars(
        select(Recommendation)
        .options(joinedload(Recommendation.resource), joinedload(Recommendation.competency))
        .where(Recommendation.user_id == user_id, Recommendation.status == "ACTIVE")
        .order_by(Recommendation.rank)
    ).all()
    if not rows:
        return generate_learning_path(db, user_id)
    user = db.get(User, user_id)
    job_role = None
    if user is not None:
        ensure_profile(db, user)
        job_role = user.profile.job_role if user.profile else None
    return LearningPathResponse(
        job_role=job_role,
        items=[
            RecommendationOut(
                id=row.id,
                rank=row.rank,
                title=row.resource.title if row.resource else "Learning resource",
                provider=row.resource.provider if row.resource else "",
                url=row.resource.url if row.resource else None,
                competency_code=row.competency.code if row.competency else "",
                competency_name=row.competency.name if row.competency else "",
                gap_at_generation=row.gap_at_generation,
                relevance_score=row.relevance_score,
                estimated_effort_hours=row.estimated_effort_hours,
                reason=row.reason,
                expected_benefit=row.expected_benefit,
                is_mock=row.resource.is_mock if row.resource else True,
                status=row.status,
            )
            for row in rows
        ],
    )

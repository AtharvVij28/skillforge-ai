"""Create, deliver, score assessments and update competency estimates."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.ai.llm import get_llm_provider
from app.core.config import get_settings
from app.models.assessment import Assessment, AssessmentAnswer, AssessmentAttempt, AssessmentQuestion, Question
from app.models.competency import Competency, UserCompetency
from app.models.user import User
from app.schemas.assessment import (
    AnswerSubmission,
    AssessmentDetail,
    AssessmentQuestionOut,
    AssessmentSummary,
    AttemptResult,
    CompetencyBreakdownItem,
    GenerateAssessmentRequest,
    QuestionOption,
    StartAttemptResponse,
)
from app.services.catalog_seed import ensure_learning_catalog
from app.services.email_service import send_assessment_result_email
from app.services.email_templates import performance_label
from app.services.framework_seed import ensure_competency_framework
from app.services.skill_gap_service import _q, analyze_gaps, get_latest_gaps

TWO = Decimal("0.01")


def _options(raw: object) -> list[QuestionOption]:
    if not isinstance(raw, list):
        return []
    items: list[QuestionOption] = []
    for entry in raw:
        if isinstance(entry, dict) and entry.get("key") and entry.get("text"):
            items.append(QuestionOption(key=str(entry["key"]), text=str(entry["text"])))
    return items


def _question_out(question: Question, points: Decimal, *, reveal: bool) -> AssessmentQuestionOut:
    competency = question.competency
    return AssessmentQuestionOut(
        id=question.id,
        stem=question.stem,
        options=_options(question.options),
        competency_code=competency.code if competency else "",
        competency_name=competency.name if competency else "",
        points=points,
        correct_option=question.correct_option if reveal else None,
        explanation=question.explanation if reveal else None,
    )


def _summary(assessment: Assessment) -> AssessmentSummary:
    method = "MIXED"
    methods = {link.question.generation_method for link in assessment.questions if link.question}
    if methods == {"AI"}:
        method = "AI"
    elif methods == {"MANUAL"}:
        method = "BANK"
    return AssessmentSummary(
        id=assessment.id,
        title=assessment.title,
        description=assessment.description,
        is_published=assessment.is_published,
        question_count=len(assessment.questions),
        generation_method=method,
        created_at=assessment.created_at,
    )


def _load_assessment(db: Session, assessment_id: UUID) -> Assessment:
    item = db.scalar(
        select(Assessment)
        .options(
            joinedload(Assessment.questions)
            .joinedload(AssessmentQuestion.question)
            .joinedload(Question.competency)
        )
        .where(Assessment.id == assessment_id)
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return item


def list_assessments(db: Session, user_id: UUID) -> list[AssessmentSummary]:
    rows = db.scalars(
        select(Assessment)
        .options(joinedload(Assessment.questions).joinedload(AssessmentQuestion.question))
        .where(Assessment.created_by == user_id)
        .order_by(Assessment.created_at.desc())
    ).unique().all()
    return [_summary(row) for row in rows]


def get_assessment(db: Session, user_id: UUID, assessment_id: UUID, *, reveal: bool = False) -> AssessmentDetail:
    assessment = _load_assessment(db, assessment_id)
    if assessment.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to view this assessment")
    questions = [
        _question_out(link.question, link.points, reveal=reveal)
        for link in sorted(assessment.questions, key=lambda item: item.sort_order)
        if link.question is not None
    ]
    summary = _summary(assessment)
    return AssessmentDetail(**summary.model_dump(), questions=questions)


SUBJECT_CODE_ALIASES = {
    "python": "PYTHON",
    "statistics": "STATISTICS",
    "machine-learning": "MACHINE_LEARNING",
    "machine_learning": "MACHINE_LEARNING",
    "artificial-intelligence": "ARTIFICIAL_INTELLIGENCE",
    "artificial_intelligence": "ARTIFICIAL_INTELLIGENCE",
    "data-science": "DATA_SCIENCE",
    "data_science": "DATA_SCIENCE",
    "sql-databases": "SQL_DATABASES",
    "sql_databases": "SQL_DATABASES",
    "sql": "SQL_DATABASES",
    "data-visualization": "DATA_VISUALIZATION",
    "data_visualization": "DATA_VISUALIZATION",
    "computer-networks": "COMPUTER_NETWORKS",
    "computer_networks": "COMPUTER_NETWORKS",
    "operating-systems": "OPERATING_SYSTEMS",
    "operating_systems": "OPERATING_SYSTEMS",
    "web-development": "WEB_DEVELOPMENT",
    "web_development": "WEB_DEVELOPMENT",
    "cloud-computing": "CLOUD_COMPUTING",
    "cloud_computing": "CLOUD_COMPUTING",
    "cybersecurity": "CYBERSECURITY",
    "algorithms-data-structures": "ALGORITHMS",
    "algorithms_data_structures": "ALGORITHMS",
    "algorithms": "ALGORITHMS",
}


def _normalize_competency_code(raw: str) -> str:
    value = raw.strip().lower().replace(" ", "-")
    return SUBJECT_CODE_ALIASES.get(value, value.replace("-", "_").upper())


def _target_competencies(
    db: Session, user_id: UUID, competency_codes: list[str]
) -> list[Competency]:
    query = select(Competency).where(Competency.is_active.is_(True))
    if competency_codes:
        codes = {_normalize_competency_code(code) for code in competency_codes if code.strip()}
        rows = db.scalars(query.where(Competency.code.in_(codes))).all()
        if rows:
            return list(rows)
    gaps = get_latest_gaps(db, user_id)
    open_ids = [item.competency_id for item in gaps.items if item.status == "GAP"]
    if open_ids:
        rows = db.scalars(query.where(Competency.id.in_(open_ids))).all()
        if rows:
            return list(rows)
    preferred = {"PYTHON", "SQL_DATABASES", "STATISTICS", "DATA_GOVERNANCE", "MACHINE_LEARNING"}
    rows = db.scalars(query.where(Competency.code.in_(preferred))).all()
    return list(rows) or list(db.scalars(query.limit(5)).all())


def _parse_generated_questions(payload: dict, fallback_code: str | None = None) -> list[dict]:
    raw_items = payload.get("questions")
    if isinstance(raw_items, list):
        items = raw_items
    else:
        items = [payload]
    parsed: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        options = item.get("options")
        correct = str(item.get("correct_option", "")).upper().strip()
        stem = str(item.get("stem", "")).strip()
        if not stem or not isinstance(options, list) or len(options) < 2 or correct not in {"A", "B", "C", "D"}:
            continue
        parsed.append(
            {
                "stem": stem,
                "options": options,
                "correct_option": correct,
                "explanation": str(item.get("explanation") or ""),
                "competency_code": str(item.get("competency_code") or fallback_code or "").upper(),
            }
        )
    return parsed


def _maybe_generate_ai_questions(db: Session, competencies: list[Competency], user: User) -> None:
    if not competencies:
        return
    settings = get_settings()
    provider = get_llm_provider()
    method = "AI" if settings.uses_live_llm else "AI_MOCK"
    names = ", ".join(f"{item.code} ({item.name})" for item in competencies)
    prompt = (
        "Create one professional multiple-choice question for each of these competencies: "
        f"{names}. Audience: officers in India's official statistical system. Difficulty: medium. "
        "Use four options A-D. Include competency_code on each question matching the code given."
    )
    by_code = {item.code: item for item in competencies}
    saved = False
    try:
        payload = provider.generate_json(prompt)
        parsed = _parse_generated_questions(payload)
        for index, item in enumerate(parsed):
            competency = by_code.get(item["competency_code"])
            if competency is None and index < len(competencies):
                competency = competencies[index]
            if competency is None:
                continue
            db.add(
                Question(
                    stem=item["stem"],
                    options=item["options"],
                    correct_option=item["correct_option"],
                    explanation=item["explanation"],
                    difficulty="MEDIUM",
                    competency_id=competency.id,
                    generation_method=method,
                    is_approved=True,
                    created_by=user.id,
                )
            )
            saved = True
    except Exception:
        saved = False

    if not saved:
        for competency in competencies:
            try:
                payload = provider.generate_json(
                    f"Create one professional multiple-choice question for the competency named {competency.name}."
                )
                parsed = _parse_generated_questions(payload, fallback_code=competency.code)
                if not parsed:
                    continue
                item = parsed[0]
                db.add(
                    Question(
                        stem=item["stem"],
                        options=item["options"],
                        correct_option=item["correct_option"],
                        explanation=item["explanation"],
                        difficulty="MEDIUM",
                        competency_id=competency.id,
                        generation_method=method,
                        is_approved=True,
                        created_by=user.id,
                    )
                )
            except Exception:
                continue
    db.commit()


def generate_assessment(
    db: Session, user: User, payload: GenerateAssessmentRequest
) -> AssessmentDetail:
    ensure_competency_framework(db)
    ensure_learning_catalog(db)
    analyze_gaps(db, user.id)
    targets = _target_competencies(db, user.id, payload.competency_codes)
    if not targets:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No competencies available for assessment")

    _maybe_generate_ai_questions(db, targets, user)

    target_ids = [item.id for item in targets]
    bank = db.scalars(
        select(Question)
        .options(joinedload(Question.competency))
        .where(
            Question.is_approved.is_(True),
            Question.competency_id.in_(target_ids),
        )
        .order_by(Question.created_at.desc())
    ).all()
    if len(bank) < payload.question_count:
        extra = db.scalars(
            select(Question)
            .options(joinedload(Question.competency))
            .where(Question.is_approved.is_(True))
            .order_by(Question.created_at.desc())
        ).all()
        seen = {item.id for item in bank}
        bank.extend(item for item in extra if item.id not in seen)

    grouped: dict = {}
    for question in bank:
        grouped.setdefault(question.competency_id, []).append(question)
    selected: list[Question] = []
    while len(selected) < payload.question_count and any(grouped.values()):
        for competency_id in list(grouped):
            bucket = grouped.get(competency_id) or []
            if bucket:
                selected.append(bucket.pop(0))
            if len(selected) >= payload.question_count:
                break
    if not selected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question bank is empty. Restart the API so catalog seed can run.",
        )

    settings = get_settings()
    title_prefix = "AI" if settings.uses_live_llm else "SkillForge"
    assessment = Assessment(
        title=f"{title_prefix} competency assessment",
        description="Questions are tailored to the subjects you selected.",
        created_by=user.id,
        is_published=True,
        time_limit_minutes=20,
    )
    db.add(assessment)
    db.flush()
    for index, question in enumerate(selected, start=1):
        db.add(
            AssessmentQuestion(
                assessment_id=assessment.id,
                question_id=question.id,
                sort_order=index,
                points=Decimal("1.00"),
            )
        )
    db.commit()
    return get_assessment(db, user.id, assessment.id, reveal=False)


def start_attempt(db: Session, user_id: UUID, assessment_id: UUID) -> StartAttemptResponse:
    assessment = _load_assessment(db, assessment_id)
    if assessment.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to start this assessment")
    existing = db.scalar(
        select(AssessmentAttempt).where(
            AssessmentAttempt.assessment_id == assessment_id,
            AssessmentAttempt.user_id == user_id,
            AssessmentAttempt.status == "IN_PROGRESS",
        )
    )
    if existing is None:
        existing = AssessmentAttempt(
            assessment_id=assessment_id,
            user_id=user_id,
            status="IN_PROGRESS",
        )
        db.add(existing)
        db.commit()
        db.refresh(existing)

    questions = [
        _question_out(link.question, link.points, reveal=False)
        for link in sorted(assessment.questions, key=lambda item: item.sort_order)
        if link.question is not None
    ]
    return StartAttemptResponse(
        attempt_id=existing.id,
        assessment_id=assessment.id,
        status=existing.status,
        questions=questions,
    )


def _blend(old: Decimal, assessment_percent: Decimal, confidence: Decimal) -> Decimal:
    alpha = Decimal("0.50") if confidence < Decimal("0.40") else Decimal("0.35")
    return _q((Decimal("1") - alpha) * old + alpha * assessment_percent)


def submit_attempt(
    db: Session, user_id: UUID, attempt_id: UUID, answers: list[AnswerSubmission]
) -> AttemptResult:
    attempt = db.scalar(
        select(AssessmentAttempt)
        .options(
            joinedload(AssessmentAttempt.assessment)
            .joinedload(Assessment.questions)
            .joinedload(AssessmentQuestion.question)
            .joinedload(Question.competency)
        )
        .where(AssessmentAttempt.id == attempt_id)
    )
    if attempt is None or attempt.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    if attempt.status == "SUBMITTED":
        return get_attempt(db, user_id, attempt_id)

    assessment = attempt.assessment
    links = {link.question_id: link for link in assessment.questions}
    submitted = {item.question_id: item.selected_option.strip().upper() for item in answers}

    total_points = Decimal("0.00")
    earned = Decimal("0.00")
    per_comp: dict[UUID, dict[str, Decimal | str]] = defaultdict(
        lambda: {"correct": Decimal("0"), "total": Decimal("0"), "code": "", "name": ""}
    )

    for question_id, link in links.items():
        question = link.question
        if question is None:
            continue
        selected = submitted.get(question_id, "")
        is_correct = selected == question.correct_option.upper()
        awarded = link.points if is_correct else Decimal("0.00")
        total_points += link.points
        earned += awarded
        bucket = per_comp[question.competency_id]
        bucket["total"] = Decimal(str(bucket["total"])) + Decimal("1")
        if is_correct:
            bucket["correct"] = Decimal(str(bucket["correct"])) + Decimal("1")
        bucket["code"] = question.competency.code if question.competency else ""
        bucket["name"] = question.competency.name if question.competency else ""
        db.add(
            AssessmentAnswer(
                attempt_id=attempt.id,
                question_id=question_id,
                selected_option=selected or "—",
                is_correct=is_correct,
                points_awarded=awarded,
                feedback=question.explanation if is_correct else question.explanation,
            )
        )

    percentage = _q((earned / total_points * 100) if total_points else 0)
    breakdown: list[CompetencyBreakdownItem] = []
    strengths: list[str] = []
    weaknesses: list[str] = []

    for competency_id, stats in per_comp.items():
        total = Decimal(str(stats["total"])) or Decimal("1")
        percent_correct = _q(Decimal(str(stats["correct"])) / total * 100)
        existing = db.scalar(
            select(UserCompetency).where(
                UserCompetency.user_id == user_id,
                UserCompetency.competency_id == competency_id,
            )
        )
        previous = _q(existing.current_score) if existing else Decimal("0.00")
        old_confidence = _q(existing.confidence) if existing else Decimal("0.20")
        updated = _blend(previous, percent_correct, old_confidence)
        if existing is None:
            existing = UserCompetency(user_id=user_id, competency_id=competency_id)
        existing.current_score = updated
        existing.confidence = min(Decimal("0.90"), old_confidence + Decimal("0.15"))
        existing.source = "ASSESSMENT"
        existing.last_assessed_at = datetime.now(timezone.utc)
        existing.explanation = (
            f"Updated from assessment: {percent_correct}% correct on this competency. "
            f"Previous estimate {previous} blended to {updated}."
        )
        db.add(existing)
        name = str(stats["name"])
        if percent_correct >= 70:
            strengths.append(name)
        else:
            weaknesses.append(name)
        breakdown.append(
            CompetencyBreakdownItem(
                competency_id=competency_id,
                competency_code=str(stats["code"]),
                competency_name=name,
                percent_correct=percent_correct,
                previous_score=previous,
                updated_score=updated,
            )
        )

    attempt.total_score = earned
    attempt.percentage = percentage
    attempt.competency_breakdown = [item.model_dump(mode="json") for item in breakdown]
    attempt.strengths = strengths
    attempt.weaknesses = weaknesses
    attempt.status = "SUBMITTED"
    attempt.submitted_at = datetime.now(timezone.utc)
    attempt.feedback_summary = (
        f"You scored {percentage}%. Strengths: {', '.join(strengths) or 'none yet'}. "
        f"Focus next on: {', '.join(weaknesses) or 'keep practising to maintain level'}."
    )
    attempt.next_action = "Open your learning path for study material matched to remaining gaps."
    db.add(attempt)
    db.commit()

    analyze_gaps(db, user_id)
    from app.services.recommendation_service import generate_learning_path

    generate_learning_path(db, user_id)
    result = get_attempt(db, user_id, attempt_id)
    learner = db.get(User, user_id)
    if learner is not None:
        stored_score = result.percentage
        score_text = None if stored_score is None else f"{Decimal(str(stored_score)):.0f}"
        answers = db.scalars(
            select(AssessmentAnswer).where(AssessmentAnswer.attempt_id == attempt.id)
        ).all()
        correct_count = sum(1 for item in answers if item.is_correct)
        total_count = len(answers) or len(result.questions)
        skill_name = None
        if result.competency_breakdown:
            skill_name = result.competency_breakdown[0].competency_name
        elif result.weaknesses:
            skill_name = result.weaknesses[0]
        elif result.strengths:
            skill_name = result.strengths[0]
        send_assessment_result_email(
            to_email=learner.email,
            full_name=learner.full_name,
            user_id=learner.id,
            assessment_title=assessment.title,
            score=score_text,
            correct_answers=str(correct_count) if total_count else None,
            total_questions=str(total_count) if total_count else None,
            performance_label_text=performance_label(float(stored_score)) if stored_score is not None else None,
            competency_name=skill_name,
            result_summary=result.feedback_summary,
            next_step=result.next_action,
        )
    return result


def get_attempt(db: Session, user_id: UUID, attempt_id: UUID) -> AttemptResult:
    attempt = db.scalar(
        select(AssessmentAttempt)
        .options(
            joinedload(AssessmentAttempt.assessment)
            .joinedload(Assessment.questions)
            .joinedload(AssessmentQuestion.question)
            .joinedload(Question.competency)
        )
        .where(AssessmentAttempt.id == attempt_id)
    )
    if attempt is None or attempt.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    reveal = attempt.status == "SUBMITTED"
    questions = [
        _question_out(link.question, link.points, reveal=reveal)
        for link in sorted(attempt.assessment.questions, key=lambda item: item.sort_order)
        if link.question is not None
    ]
    breakdown_raw = attempt.competency_breakdown or []
    breakdown = (
        [CompetencyBreakdownItem.model_validate(item) for item in breakdown_raw] if reveal else []
    )
    return AttemptResult(
        attempt_id=attempt.id,
        assessment_id=attempt.assessment_id,
        status=attempt.status,
        total_score=attempt.total_score,
        percentage=attempt.percentage,
        strengths=list(attempt.strengths or []),
        weaknesses=list(attempt.weaknesses or []),
        feedback_summary=attempt.feedback_summary if reveal else None,
        next_action=attempt.next_action if reveal else None,
        competency_breakdown=breakdown,
        questions=questions,
        submitted_at=attempt.submitted_at,
    )

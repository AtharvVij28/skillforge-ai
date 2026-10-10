"""Assessment scoring, competency update, and learning-path tests."""

from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assessment import Question
from app.services.catalog_seed import ensure_learning_catalog
from app.services.framework_seed import ensure_competency_framework


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_generate_start_submit_updates_competency_and_path(
    client: TestClient, db_session: Session, learner_token: str
) -> None:
    ensure_competency_framework(db_session)
    ensure_learning_catalog(db_session)
    profile = client.put(
        "/api/profile",
        headers=_auth_header(learner_token),
        json={"job_role": "STATISTICAL_OFFICER", "technical_skills": ["Python"], "years_of_experience": 3},
    )
    assert profile.status_code == 200

    generated = client.post(
        "/api/assessments/generate",
        headers=_auth_header(learner_token),
        json={"question_count": 4},
    )
    assert generated.status_code == 200
    assessment_id = generated.json()["id"]
    questions = generated.json()["questions"]
    assert len(questions) >= 3
    assert all(item.get("correct_option") is None for item in questions)

    started = client.post(
        f"/api/assessments/{assessment_id}/start",
        headers=_auth_header(learner_token),
    )
    assert started.status_code == 200
    attempt_id = started.json()["attempt_id"]
    assert all(item.get("correct_option") is None for item in started.json()["questions"])

    answers = []
    for item in started.json()["questions"]:
        question = db_session.get(Question, UUID(item["id"]))
        assert question is not None
        answers.append({"question_id": item["id"], "selected_option": question.correct_option})

    submitted = client.post(
        f"/api/assessments/attempts/{attempt_id}/submit",
        headers=_auth_header(learner_token),
        json={"answers": answers},
    )
    assert submitted.status_code == 200
    result = submitted.json()
    assert result["status"] == "SUBMITTED"
    assert float(result["percentage"]) == 100
    assert result["feedback_summary"]
    assert any(item.get("correct_option") for item in result["questions"])
    assert len(result["competency_breakdown"]) >= 1
    updated = result["competency_breakdown"][0]
    assert float(updated["updated_score"]) >= float(updated["previous_score"] or 0)

    path = client.get("/api/learning/path", headers=_auth_header(learner_token))
    assert path.status_code == 200
    items = path.json()["items"]
    assert len(items) >= 1
    assert items[0]["url"]
    assert "gap" in items[0]["reason"].lower()
    assert "hashed_password" not in submitted.text.lower()


def test_generate_from_interest_codes_then_gaps_without_job_role(
    client: TestClient, db_session: Session, learner_token: str
) -> None:
    ensure_competency_framework(db_session)
    ensure_learning_catalog(db_session)

    generated = client.post(
        "/api/assessments/generate",
        headers=_auth_header(learner_token),
        json={"question_count": 4, "competency_codes": ["python", "statistics"]},
    )
    assert generated.status_code == 200
    codes = {item["competency_code"] for item in generated.json()["questions"]}
    assert codes & {"PYTHON", "STATISTICS"}

    started = client.post(
        f"/api/assessments/{generated.json()['id']}/start",
        headers=_auth_header(learner_token),
    )
    assert started.status_code == 200
    answers = []
    for item in started.json()["questions"]:
        question = db_session.get(Question, UUID(item["id"]))
        assert question is not None
        answers.append({"question_id": item["id"], "selected_option": question.correct_option})

    submitted = client.post(
        f"/api/assessments/attempts/{started.json()['attempt_id']}/submit",
        headers=_auth_header(learner_token),
        json={"answers": answers},
    )
    assert submitted.status_code == 200

    scores = client.get("/api/skills/me", headers=_auth_header(learner_token))
    assert scores.status_code == 200
    assert scores.json()["has_assessment"] is True

    gaps = client.get("/api/skills/gaps", headers=_auth_header(learner_token))
    assert gaps.status_code == 200
    assert gaps.json()["open_gaps"] >= 0
    assert len(gaps.json()["items"]) >= 1
    assert all(float(item["required_score"]) == 75 for item in gaps.json()["items"])

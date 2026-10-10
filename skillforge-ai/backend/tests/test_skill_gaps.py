"""Phase 5 skill-gap engine tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.framework_seed import ensure_competency_framework


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _set_job_role(client: TestClient, token: str, job_role: str, skills: list[str] | None = None) -> None:
    payload: dict = {"job_role": job_role, "designation": "Officer"}
    if skills is not None:
        payload["technical_skills"] = skills
        payload["years_of_experience"] = 4
    response = client.put("/api/profile", headers=_auth_header(token), json=payload)
    assert response.status_code == 200


def test_analyze_without_job_role_explains_missing_input(
    client: TestClient, learner_token: str
) -> None:
    response = client.post("/api/skills/gaps/analyze", headers=_auth_header(learner_token))
    assert response.status_code == 200
    payload = response.json()
    assert payload["items"] == []
    assert payload["open_gaps"] == 0
    assert "assessment" in payload["message"].lower()


def test_analyze_persists_explainable_gaps(
    client: TestClient, db_session: Session, learner_token: str
) -> None:
    ensure_competency_framework(db_session)
    _set_job_role(client, learner_token, "STATISTICAL_OFFICER", ["Python", "SQL"])

    analyzed = client.post("/api/skills/gaps/analyze", headers=_auth_header(learner_token))
    assert analyzed.status_code == 200
    payload = analyzed.json()
    assert payload["job_role"] == "STATISTICAL_OFFICER"
    assert payload["analysis_id"]
    assert payload["open_gaps"] >= 1
    assert len(payload["items"]) >= 5
    python = next(item for item in payload["items"] if item["competency_code"] == "PYTHON")
    assert float(python["required_score"]) == 80
    assert float(python["current_score"]) > 0
    assert float(python["gap"]) == max(0.0, float(python["required_score"]) - float(python["current_score"]))
    assert "required" in python["explanation"].lower()
    assert "opaque" not in python["explanation"].lower() or "not an opaque" in python["explanation"].lower()
    assert python["priority"] in {"HIGH", "MEDIUM", "LOW"}

    stored = client.get("/api/skills/gaps", headers=_auth_header(learner_token))
    assert stored.status_code == 200
    assert stored.json()["analysis_id"] == payload["analysis_id"]
    assert len(stored.json()["items"]) == len(payload["items"])

    scores = client.get("/api/skills/me", headers=_auth_header(learner_token))
    assert scores.status_code == 200
    assert scores.json()["job_role"] == "STATISTICAL_OFFICER"
    assert len(scores.json()["items"]) >= 1
    assert "hashed_password" not in stored.text.lower()


def test_unknown_job_role_returns_empty_with_message(
    client: TestClient, db_session: Session, learner_token: str
) -> None:
    ensure_competency_framework(db_session)
    _set_job_role(client, learner_token, "UNKNOWN_ROLE")
    response = client.post("/api/skills/gaps/analyze", headers=_auth_header(learner_token))
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert "UNKNOWN_ROLE" in response.json()["message"]


def test_learner_cannot_read_another_users_gaps(
    client: TestClient, learner_token: str, registered_learner: dict, admin_token: str
) -> None:
    admin_id = client.get("/api/auth/me", headers=_auth_header(admin_token)).json()["id"]
    response = client.get(f"/api/skills/gaps/{admin_id}", headers=_auth_header(learner_token))
    assert response.status_code == 403


def test_admin_can_read_learner_gaps(
    client: TestClient, db_session: Session, learner_token: str, registered_learner: dict, admin_token: str
) -> None:
    ensure_competency_framework(db_session)
    _set_job_role(client, learner_token, "DATA_ANALYST", ["Python"])
    client.post("/api/skills/gaps/analyze", headers=_auth_header(learner_token))
    response = client.get(
        f"/api/skills/gaps/{registered_learner['id']}",
        headers=_auth_header(admin_token),
    )
    assert response.status_code == 200
    assert response.json()["user_id"] == registered_learner["id"]
    assert response.json()["job_role"] == "DATA_ANALYST"

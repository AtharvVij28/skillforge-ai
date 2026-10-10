"""Phase 4 profile and competency framework tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.framework_seed import ensure_competency_framework


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_unauthenticated_profile_rejected(client: TestClient) -> None:
    response = client.get("/api/profile")
    assert response.status_code == 401


def test_new_user_profile_is_empty_and_incomplete(
    client: TestClient, learner_token: str, learner_credentials: dict
) -> None:
    response = client.get("/api/profile", headers=_auth_header(learner_token))
    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == learner_credentials["email"]
    assert payload["full_name"] == learner_credentials["full_name"]
    assert payload["job_role"] is None
    assert payload["technical_skills"] == []
    assert payload["profile_completion_pct"] < 100
    assert "hashed_password" not in payload


def test_update_own_profile_and_completion(
    client: TestClient, db_session: Session, learner_token: str
) -> None:
    ensure_competency_framework(db_session)
    departments = client.get("/api/profile/departments", headers=_auth_header(learner_token))
    assert departments.status_code == 200
    items = departments.json()["items"]
    assert len(items) >= 1
    department_id = items[0]["id"]

    response = client.put(
        "/api/profile",
        headers=_auth_header(learner_token),
        json={
            "full_name": "Updated Learner",
            "department_id": department_id,
            "designation": "Statistical Officer",
            "job_role": "STATISTICAL_OFFICER",
            "assignment": "Survey operations",
            "education": "M.Stat",
            "years_of_experience": 5,
            "technical_skills": ["Python", "SQL"],
            "statistical_skills": ["Sampling"],
            "digital_skills": ["Excel"],
            "managerial_skills": ["Planning"],
            "behavioural_skills": ["Communication"],
            "previous_training": ["NSSTA induction"],
            "career_goals": "Lead a data analytics cell",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["full_name"] == "Updated Learner"
    assert payload["department"]["id"] == department_id
    assert payload["job_role"] == "STATISTICAL_OFFICER"
    assert payload["technical_skills"] == ["Python", "SQL"]
    assert payload["profile_completion_pct"] == 100

    completion = client.get("/api/profile/completion", headers=_auth_header(learner_token))
    assert completion.status_code == 200
    assert completion.json()["profile_completion_pct"] == 100
    assert completion.json()["missing_fields"] == []


def test_learner_cannot_view_another_profile(
    client: TestClient, learner_token: str, registered_learner: dict, admin_token: str
) -> None:
    me = client.get("/api/auth/me", headers=_auth_header(admin_token))
    assert me.status_code == 200
    admin_id = me.json()["id"]
    response = client.get(f"/api/profile/{admin_id}", headers=_auth_header(learner_token))
    assert response.status_code == 403


def test_admin_can_view_another_profile(
    client: TestClient, admin_token: str, registered_learner: dict
) -> None:
    response = client.get(
        f"/api/profile/{registered_learner['id']}",
        headers=_auth_header(admin_token),
    )
    assert response.status_code == 200
    assert response.json()["email"] == registered_learner["email"]


def test_framework_seed_and_list(
    client: TestClient, db_session: Session, learner_token: str
) -> None:
    ensure_competency_framework(db_session)
    response = client.get("/api/competencies/framework", headers=_auth_header(learner_token))
    assert response.status_code == 200
    categories = response.json()["categories"]
    assert len(categories) >= 5
    codes = {item["code"] for category in categories for item in category["competencies"]}
    assert "PYTHON" in codes
    assert "STATISTICS" in codes

    listing = client.get("/api/competencies", headers=_auth_header(learner_token))
    assert listing.status_code == 200
    assert listing.json()["total"] >= 10


def test_learner_cannot_create_competency(
    client: TestClient, db_session: Session, learner_token: str
) -> None:
    ensure_competency_framework(db_session)
    categories = client.get("/api/competencies/categories", headers=_auth_header(learner_token))
    category_id = categories.json()[0]["id"]
    response = client.post(
        "/api/competencies",
        headers=_auth_header(learner_token),
        json={
            "code": "FORBIDDEN_SKILL",
            "name": "Should not work",
            "category_id": category_id,
        },
    )
    assert response.status_code == 403


def test_admin_can_create_update_and_deactivate_competency(
    client: TestClient, db_session: Session, admin_token: str
) -> None:
    ensure_competency_framework(db_session)
    categories = client.get("/api/competencies/categories", headers=_auth_header(admin_token))
    category_id = categories.json()[0]["id"]

    created = client.post(
        "/api/competencies",
        headers=_auth_header(admin_token),
        json={
            "code": "survey_design",
            "name": "Survey Design",
            "category_id": category_id,
            "description": "Sample design and questionnaire development.",
            "default_priority": "HIGH",
        },
    )
    assert created.status_code == 201
    payload = created.json()
    assert payload["code"] == "SURVEY_DESIGN"
    competency_id = payload["id"]

    updated = client.put(
        f"/api/competencies/{competency_id}",
        headers=_auth_header(admin_token),
        json={"name": "Survey Design & Sampling"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Survey Design & Sampling"

    deleted = client.delete(f"/api/competencies/{competency_id}", headers=_auth_header(admin_token))
    assert deleted.status_code == 200
    assert deleted.json()["is_active"] is False

    visible = client.get("/api/competencies", headers=_auth_header(admin_token))
    codes = {item["code"] for item in visible.json()["items"]}
    assert "SURVEY_DESIGN" not in codes


def test_admin_can_upsert_role_requirements(
    client: TestClient, db_session: Session, admin_token: str
) -> None:
    ensure_competency_framework(db_session)
    listing = client.get("/api/competencies", headers=_auth_header(admin_token))
    python = next(item for item in listing.json()["items"] if item["code"] == "PYTHON")

    response = client.put(
        "/api/competencies/role-requirements",
        headers=_auth_header(admin_token),
        json={
            "items": [
                {
                    "role_code": "STATISTICAL_OFFICER",
                    "competency_id": python["id"],
                    "required_score": 82,
                    "priority": "HIGH",
                    "relevance_weight": 1.5,
                }
            ]
        },
    )
    assert response.status_code == 200
    match = next(item for item in response.json() if item["competency_code"] == "PYTHON")
    assert float(match["required_score"]) == 82
    assert "hashed_password" not in response.text.lower()

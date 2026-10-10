"""Transactional email templates and dispatch tests. Never send live mail."""

from __future__ import annotations

import logging

from fastapi.testclient import TestClient

from app.services import email_templates
from app.services.email_service import EmailDeliveryError, send_email


SECRET_FRAGMENTS = (
    "argon2",
    "hashed_password",
    "JWT_SECRET",
    "RESEND_API_KEY",
    "DATABASE_URL",
    "LearnerPass123!",
)


def _assert_no_secrets(content: email_templates.EmailContent) -> None:
    blob = f"{content.subject}\n{content.html_body}\n{content.text_body}".lower()
    assert "password" not in content.subject.lower() or "reset" in content.subject.lower()
    for fragment in SECRET_FRAGMENTS:
        assert fragment.lower() not in blob
    assert "LearnerPass123!" not in content.html_body
    assert "LearnerPass123!" not in content.text_body


def test_welcome_email_template() -> None:
    content = email_templates.welcome_email(full_name="Atharv Vij", app_url="http://localhost:5173")
    assert content.subject == "Welcome to SkillForge AI 🚀"
    assert "Hi Atharv" in content.text_body
    assert "skill gaps" in content.text_body.lower()
    assert "http://localhost:5173" in content.html_body
    assert "Open SkillForge AI" in content.html_body
    assert "<html" in content.html_body.lower()
    _assert_no_secrets(content)


def test_password_reset_email_template() -> None:
    content = email_templates.password_reset_email(
        full_name="Test Learner",
        reset_url="http://localhost:5173/reset-password?token=abcTOKEN",
        expiry_minutes=30,
    )
    assert content.subject == "Reset your SkillForge AI password"
    assert "30 minutes" in content.text_body
    assert "reset-password?token=abcTOKEN" in content.html_body
    assert "never share" in content.text_body.lower()
    _assert_no_secrets(content)


def test_learning_recommendation_email_omits_missing_fields() -> None:
    content = email_templates.learning_recommendation_email(
        full_name="Test Learner",
        learning_title="SQL for Data Analysis",
        recommendation_reason="Gap in SQL.",
        learning_url="http://localhost:5173/path",
    )
    assert content.subject.startswith("Your SkillForge AI learning recommendation")
    assert "SQL for Data Analysis" in content.text_body
    assert "Current level" not in content.text_body
    assert "Start Learning" in content.html_body
    _assert_no_secrets(content)


def test_assessment_result_email_uses_provided_score_only() -> None:
    content = email_templates.assessment_result_email(
        full_name="Test Learner",
        assessment_title="AI competency assessment",
        score="80",
        correct_answers="4",
        total_questions="5",
        performance_label_text="Strong",
        competency_name="Python",
        result_summary="You scored 80%.",
        next_step="Open your learning path",
        results_url="http://localhost:5173/assess",
    )
    assert content.subject.startswith("Your SkillForge AI assessment results")
    assert "Score: 80%" in content.text_body
    assert "4 / 5" in content.text_body
    assert "81" not in content.text_body
    _assert_no_secrets(content)


def test_send_email_failure_is_delivery_error(monkeypatch) -> None:
    from app.core.config import clear_settings_cache

    monkeypatch.setenv("RESEND_API_KEY", "re_test_not_real")
    monkeypatch.setenv("RESEND_FROM", "SkillForge AI <onboarding@resend.dev>")
    clear_settings_cache()

    class Boom:
        is_error = True

        def json(self):
            return {"message": "simulated outage"}

    def fake_post(*_args, **_kwargs):
        return Boom()

    monkeypatch.setattr("app.services.email_service.httpx.post", fake_post)
    try:
        send_email("learner@example.com", "Test", "<p>Hi</p>", text_body="Hi")
        raise AssertionError("expected EmailDeliveryError")
    except EmailDeliveryError as exc:
        assert "simulated outage" in str(exc)
    finally:
        clear_settings_cache()


def test_welcome_email_failure_does_not_rollback_registration(
    client: TestClient, monkeypatch, learner_credentials: dict
) -> None:
    from app.core.config import clear_settings_cache

    monkeypatch.setenv("EMAIL_VERIFICATION_REQUIRED", "false")
    monkeypatch.setenv("RESEND_API_KEY", "re_test_not_real")
    clear_settings_cache()

    def boom(*_args, **_kwargs):
        raise EmailDeliveryError("simulated outage")

    monkeypatch.setattr("app.services.email_service.send_email", boom)
    response = client.post("/api/auth/register", json=learner_credentials)
    assert response.status_code == 201
    login = client.post(
        "/api/auth/login",
        json={"email": learner_credentials["email"], "password": learner_credentials["password"]},
    )
    assert login.status_code == 200


def test_forgot_password_is_generic_and_reset_works(
    client: TestClient, monkeypatch, registered_learner: dict, learner_credentials: dict, caplog
) -> None:
    from app.core.config import clear_settings_cache

    monkeypatch.setenv("RESEND_API_KEY", "re_test_not_real")
    clear_settings_cache()
    captured: list[dict[str, str]] = []

    def fake_send(
        to_email: str,
        subject: str,
        html_content: str | None = None,
        *,
        text_body: str | None = None,
        html_body: str | None = None,
    ) -> None:
        captured.append(
            {
                "to": to_email,
                "subject": subject,
                "text": text_body or "",
                "html": html_content or html_body or "",
            }
        )

    monkeypatch.setattr("app.services.email_service.send_email", fake_send)
    caplog.set_level(logging.INFO)
    missing = client.post("/api/auth/forgot-password", json={"email": "nobody@example.com"})
    existing = client.post("/api/auth/forgot-password", json={"email": learner_credentials["email"]})
    assert missing.status_code == 200
    assert existing.status_code == 200
    assert missing.json()["message"] == existing.json()["message"]
    assert "if an account exists" in existing.json()["message"].lower()
    assert captured
    mail = captured[-1]
    assert mail["to"] == learner_credentials["email"]
    assert mail["subject"] == "Reset your SkillForge AI password"
    assert "/reset-password?token=" in mail["text"]
    token = mail["text"].split("token=", 1)[1].split()[0]
    assert token not in caplog.text
    assert learner_credentials["password"] not in mail["text"]
    assert learner_credentials["password"] not in mail["html"]

    reset = client.post("/api/auth/reset-password", json={"token": token, "password": "NewPass123!"})
    assert reset.status_code == 200
    old = client.post(
        "/api/auth/login",
        json={"email": learner_credentials["email"], "password": learner_credentials["password"]},
    )
    assert old.status_code == 401
    new = client.post(
        "/api/auth/login",
        json={"email": learner_credentials["email"], "password": "NewPass123!"},
    )
    assert new.status_code == 200

    reused = client.post("/api/auth/reset-password", json={"token": token, "password": "AnotherPass123!"})
    assert reused.status_code == 400

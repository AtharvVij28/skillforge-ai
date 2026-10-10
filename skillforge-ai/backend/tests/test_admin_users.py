"""Admin account directory tests."""

from fastapi.testclient import TestClient


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_learner_cannot_list_registered_accounts(client: TestClient, learner_token: str) -> None:
    response = client.get("/api/admin/users", headers=_auth_header(learner_token))
    assert response.status_code == 403


def test_admin_can_list_registered_accounts(
    client: TestClient, admin_token: str, registered_learner: dict
) -> None:
    response = client.get("/api/admin/users", headers=_auth_header(admin_token))
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 2
    emails = {item["email"] for item in payload["items"]}
    assert registered_learner["email"] in emails
    assert "admin@example.com" in emails
    assert "hashed_password" not in response.text.lower()

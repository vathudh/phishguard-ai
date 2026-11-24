from pathlib import Path

import pytest

from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE_PATH": tmp_path / "test.db"})
    with app.test_client() as client:
        yield client


def test_dashboard_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"PhishGuard" in response.data


def test_scan_rejects_short_email(client):
    response = client.post("/api/scan", json={"email_text": "too short"})
    assert response.status_code == 400


def test_scan_returns_explainable_result(client):
    response = client.post(
        "/api/scan",
        json={
            "subject": "Urgent verification",
            "sender": "Security <notice@gmail.com>",
            "email_text": "URGENT! Verify your password immediately at http://198.51.100.12/login.",
        },
    )
    payload = response.get_json()
    assert response.status_code == 201
    assert payload["risk_score"] >= 0
    assert payload["indicators"]
    assert payload["urls"]


def test_history_and_feedback(client):
    created = client.post("/api/scan", json={"email_text": "Team meeting agenda attached for tomorrow morning."}).get_json()
    history = client.get("/api/history").get_json()
    assert len(history) == 1
    feedback = client.post(f"/api/scans/{created['scan_id']}/feedback", json={"feedback": "safe"})
    assert feedback.status_code == 200

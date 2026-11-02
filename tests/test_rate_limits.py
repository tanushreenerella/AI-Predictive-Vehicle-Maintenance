import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.routes import agent_chat, analyze_route

from conftest import ORIGIN, add_vehicle, signup


def _client_from(ip: str) -> TestClient:
    return TestClient(app, raise_server_exceptions=False, client=(ip, 50000))


def _assert_rate_limited(res):
    assert res.status_code == 429
    assert "Too many requests" in res.json()["detail"]
    assert res.headers["retry-after"] == "60"


# ── auth: 5/min per IP ───────────────────────────────────────────────────────

def test_login_blocks_sixth_attempt_even_with_correct_password(client):
    # Signup has its own bucket, so this does not use up login attempts.
    signup(client, "owner@example.com")

    for _ in range(5):
        res = client.post("/auth/login", json={"email": "owner@example.com", "password": "wrong-password"})
        assert res.status_code == 401

    res = client.post(
        "/auth/login",
        json={"email": "owner@example.com", "password": "test-password"},
        headers={"Origin": ORIGIN},
    )
    _assert_rate_limited(res)
    assert res.headers["access-control-allow-origin"] == ORIGIN


def test_signup_blocks_sixth_attempt(client):
    for i in range(5):
        assert client.post("/auth/signup", json={"email": f"u{i}@example.com", "password": "long-enough"}).status_code == 200

    _assert_rate_limited(client.post("/auth/signup", json={"email": "u5@example.com", "password": "long-enough"}))


def test_login_limit_is_per_ip():
    attacker, bystander = _client_from("10.0.0.1"), _client_from("10.0.0.2")
    signup(bystander, "owner@example.com")

    for _ in range(6):
        attacker.post("/auth/login", json={"email": "owner@example.com", "password": "wrong-password"})
    _assert_rate_limited(attacker.post("/auth/login", json={"email": "owner@example.com", "password": "x"}))

    res = bystander.post("/auth/login", json={"email": "owner@example.com", "password": "test-password"})
    assert res.status_code == 200


# ── chat / analyze: 10/min per IP ────────────────────────────────────────────

@pytest.fixture
def fake_llm(monkeypatch):
    calls = []

    def fake_run_turn(state, message, *args, **kwargs):
        calls.append(message)
        return {"reply": "ok", "state": state}

    class FakeOrchestrator:
        def analyze(self, sensor_data, user_context):
            calls.append(sensor_data)
            return {"status": "ok"}

    monkeypatch.setattr(agent_chat, "run_turn", fake_run_turn)
    monkeypatch.setattr(analyze_route, "_orchestrator", FakeOrchestrator())
    return calls


def test_chat_and_agent_chat_share_one_10_per_minute_bucket(client, fake_llm):
    headers = signup(client, "owner@example.com")

    for i in range(10):
        path = "/chat" if i % 2 == 0 else "/agent/chat"
        assert client.post(path, json={"message": f"m{i}"}, headers=headers).status_code == 200

    _assert_rate_limited(client.post("/chat", json={"message": "m10"}, headers=headers))
    _assert_rate_limited(client.post("/agent/chat", json={"message": "m11"}, headers=headers))
    assert len(fake_llm) == 10


def test_analyze_blocks_eleventh_request(client, fake_llm):
    headers = signup(client, "owner@example.com")
    vid = add_vehicle(client, headers)
    body = {"vehicle_id": vid, "sensor_data": {"engine_rpm": 1}}

    for _ in range(10):
        assert client.post("/analyze", json=body, headers=headers).status_code == 200

    _assert_rate_limited(client.post("/analyze", json=body, headers=headers))
    assert len(fake_llm) == 10


def test_chat_limit_does_not_consume_auth_limit(client, fake_llm):
    headers = signup(client, "owner@example.com")
    for _ in range(11):
        client.post("/chat", json={"message": "hi"}, headers=headers)

    assert client.post("/auth/login", json={"email": "owner@example.com", "password": "test-password"}).status_code == 200

import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from backend.auth.dependencies import require_admin
from backend.models.user import User
from backend.routes import analyze_route
from backend.session import SessionLocal

from conftest import add_vehicle, signup, user_id

REPO_ROOT = Path(__file__).resolve().parent.parent


# ── 1. JWT secret comes from the environment ─────────────────────────────────

def test_jwt_module_refuses_to_load_without_secret():
    # An empty value counts as "set" for load_dotenv, so the real .env cannot
    # fill it in, and the module must still refuse to start.
    env = {**os.environ, "JWT_SECRET_KEY": ""}
    proc = subprocess.run(
        [sys.executable, "-c", "import backend.auth.jwt"],
        cwd=REPO_ROOT, env=env, capture_output=True, text=True,
    )

    assert proc.returncode != 0
    assert "JWT_SECRET_KEY is not set" in proc.stderr


def test_token_signed_with_old_hardcoded_secret_is_rejected(client):
    owner = signup(client, "owner@example.com")
    forged = jwt.encode({"sub": user_id(client, owner)}, "SUPER_SECRET_KEY_CHANGE_ME", algorithm="HS256")

    res = client.get("/auth/me", headers={"Authorization": f"Bearer {forged}"})

    assert res.status_code == 401
    assert res.json() == {"detail": "Invalid token"}


# ── 2. Signup ────────────────────────────────────────────────────────────────

def test_signup_ignores_requested_admin_role(client):
    res = client.post(
        "/auth/signup",
        json={"email": "sneaky@example.com", "password": "long-enough", "role": "admin"},
    )
    assert res.status_code == 200, res.text

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {res.json()['access_token']}"})
    assert me.json()["role"] == "user"


def test_signup_stores_email_lowercased_and_stripped(client):
    res = client.post("/auth/signup", json={"email": "  Mixed.Case@Example.COM ", "password": "long-enough"})
    assert res.status_code == 200, res.text

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {res.json()['access_token']}"})
    assert me.json()["email"] == "mixed.case@example.com"


def test_email_case_variants_are_the_same_account(client):
    assert client.post("/auth/signup", json={"email": "A@x.com", "password": "long-enough"}).status_code == 200

    dup = client.post("/auth/signup", json={"email": " a@X.COM", "password": "long-enough"})
    assert dup.status_code == 400
    assert dup.json() == {"detail": "Email already exists"}

    for variant in ("a@x.com", "A@X.COM", "  a@x.com  "):
        assert client.post("/auth/login", json={"email": variant, "password": "long-enough"}).status_code == 200


def test_login_finds_legacy_account_stored_with_mixed_case(client):
    # Rows written before normalization keep their original casing.
    from backend.auth.security import hash_password

    with SessionLocal() as db:
        db.add(User(email="Legacy@Example.com", hashed_password=hash_password("short"), role="user"))
        db.commit()

    res = client.post("/auth/login", json={"email": "legacy@example.com", "password": "short"})
    assert res.status_code == 200

    dup = client.post("/auth/signup", json={"email": "LEGACY@example.com", "password": "long-enough"})
    assert dup.status_code == 400


@pytest.mark.parametrize(
    "body, bad_field",
    [
        ({"password": "whatever"}, "email"),
        ({"email": "a@example.com"}, "password"),
        ({"email": "", "password": "whatever"}, "email"),
        ({"email": "   ", "password": "whatever"}, "email"),
        ({"email": "a@example.com", "password": ""}, "password"),
        ({"email": 123, "password": "whatever"}, "email"),
    ],
)
def test_login_invalid_body_returns_422(client, body, bad_field):
    res = client.post("/auth/login", json=body)

    assert res.status_code == 422
    assert any(err["loc"][-1] == bad_field for err in res.json()["detail"])


def test_login_wrong_password_returns_401(client):
    signup(client, "owner@example.com")

    res = client.post("/auth/login", json={"email": "owner@example.com", "password": "wrong-password"})

    assert res.status_code == 401
    assert res.json() == {"detail": "Invalid credentials"}


@pytest.mark.parametrize(
    "body, bad_field",
    [
        ({"password": "long-enough"}, "email"),
        ({"email": "a@example.com"}, "password"),
        ({"email": "not-an-email", "password": "long-enough"}, "email"),
        ({"email": "a@example.com", "password": "short"}, "password"),
    ],
)
def test_signup_invalid_body_returns_422(client, body, bad_field):
    res = client.post("/auth/signup", json=body)

    assert res.status_code == 422
    assert any(err["loc"][-1] == bad_field for err in res.json()["detail"])
    with SessionLocal() as db:
        assert db.query(User).count() == 0


# ── 3. Per-user routes ───────────────────────────────────────────────────────

@pytest.mark.parametrize("path", ["/vehicles/{uid}", "/alerts/{uid}"])
def test_user_id_routes_are_gone(client, path):
    owner = signup(client, "owner@example.com")
    uid = user_id(client, owner)
    add_vehicle(client, owner)

    res = client.get(path.format(uid=uid))

    assert res.status_code == 404
    assert "Car" not in res.text


def test_me_routes_still_return_only_own_data(client):
    owner = signup(client, "owner@example.com")
    other = signup(client, "other@example.com")
    add_vehicle(client, owner, "OwnerCar")

    assert [v["name"] for v in client.get("/vehicles/me", headers=owner).json()] == ["OwnerCar"]
    assert client.get("/vehicles/me", headers=other).json() == []
    assert client.get("/alerts/me", headers=other).json() == []


class _FakeOrchestrator:
    def __init__(self):
        self.calls = []

    def analyze(self, sensor_data, user_context):
        self.calls.append(sensor_data)
        return {"status": "ok"}


@pytest.fixture
def fake_orchestrator(monkeypatch):
    fake = _FakeOrchestrator()
    monkeypatch.setattr(analyze_route, "_orchestrator", fake)
    return fake


def test_analyze_requires_auth(client, fake_orchestrator):
    res = client.post("/analyze", json={"vehicle_id": "x", "sensor_data": {}})

    assert res.status_code == 401
    assert fake_orchestrator.calls == []


def test_analyze_rejects_other_users_vehicle(client, fake_orchestrator):
    owner = signup(client, "owner@example.com")
    other = signup(client, "other@example.com")
    vid = add_vehicle(client, owner)

    res = client.post("/analyze", json={"vehicle_id": vid, "sensor_data": {"engine_rpm": 1}}, headers=other)

    assert res.status_code == 404
    assert fake_orchestrator.calls == []


def test_analyze_allows_owner(client, fake_orchestrator):
    owner = signup(client, "owner@example.com")
    vid = add_vehicle(client, owner)

    res = client.post("/analyze", json={"vehicle_id": vid, "sensor_data": {"engine_rpm": 1}}, headers=owner)

    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
    assert fake_orchestrator.calls == [{"engine_rpm": 1}]


# ── 4. require_admin ─────────────────────────────────────────────────────────
# No admin-only routes exist in the backend yet, so the dependency is tested
# on a throwaway app that shares the same database.

@pytest.fixture
def admin_client():
    probe = FastAPI()

    @probe.get("/admin-probe")
    def admin_probe(user: User = Depends(require_admin)):
        return {"email": user.email}

    return TestClient(probe, raise_server_exceptions=False)


def test_require_admin_rejects_missing_token(admin_client):
    assert admin_client.get("/admin-probe").status_code == 401


def test_require_admin_rejects_regular_user(client, admin_client):
    regular = signup(client, "regular@example.com")

    res = admin_client.get("/admin-probe", headers=regular)

    assert res.status_code == 403
    assert res.json() == {"detail": "Admin access required"}


def test_require_admin_allows_admin(client, admin_client):
    headers = signup(client, "boss@example.com")
    with SessionLocal() as db:
        db.query(User).filter(User.email == "boss@example.com").update({"role": "admin"})
        db.commit()

    res = admin_client.get("/admin-probe", headers=headers)

    assert res.status_code == 200
    assert res.json() == {"email": "boss@example.com"}

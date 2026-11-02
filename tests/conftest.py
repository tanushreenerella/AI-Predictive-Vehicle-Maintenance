import os
import tempfile
from pathlib import Path

# Must run before anything imports backend.session: point the app at a
# throwaway SQLite file so tests never touch the real (Neon) database.
# load_dotenv() does not override variables that are already set.
_DB_PATH = Path(tempfile.mkdtemp(prefix="proactiveai-tests-")) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_PATH.as_posix()}"
os.environ["JWT_SECRET_KEY"] = "test-only-jwt-secret-not-for-production"

import pytest
from fastapi.testclient import TestClient

from backend.base import Base
from backend.main import ALLOWED_ORIGINS, app
from backend.rate_limit import limiter
from backend.session import engine

ORIGIN = ALLOWED_ORIGINS[0]


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def fresh_rate_limits():
    # Limits are in-memory and every TestClient shares one IP, so without a
    # reset, requests from earlier tests would count against later ones.
    limiter.reset()
    yield


@pytest.fixture
def client():
    # raise_server_exceptions=False so a server-side crash shows up as the
    # 500 a real client would get, instead of a Python traceback.
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def signup(client: TestClient, email: str) -> dict:
    res = client.post("/auth/signup", json={"email": email, "password": "test-password"})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def user_id(client: TestClient, headers: dict) -> str:
    res = client.get("/auth/me", headers=headers)
    assert res.status_code == 200, res.text
    return res.json()["id"]


def add_vehicle(client: TestClient, headers: dict, name: str = "Car") -> str:
    res = client.post(
        "/vehicles",
        json={"name": name, "model": "M", "year": 2020, "registration_number": f"{name}-1"},
        headers=headers,
    )
    assert res.status_code == 200, res.text
    return res.json()["id"]

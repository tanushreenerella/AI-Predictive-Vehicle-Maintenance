import os
import tempfile
from pathlib import Path

# Must run before anything imports backend.session: point the app at a
# throwaway SQLite file so tests never touch the real (Neon) database.
# load_dotenv() does not override variables that are already set.
_DB_PATH = Path(tempfile.mkdtemp(prefix="proactiveai-tests-")) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_PATH.as_posix()}"

import pytest
from fastapi.testclient import TestClient

from backend.base import Base
from backend.main import ALLOWED_ORIGINS, app
from backend.session import engine

ORIGIN = ALLOWED_ORIGINS[0]


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
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

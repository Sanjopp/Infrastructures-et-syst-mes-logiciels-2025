import os
import sys
from datetime import timedelta
from pathlib import Path

import pytest

from backend.api import tricount as api_tricount
from backend.routes import tricounts as tricount_routes
from backend.utils import auth_storage, tricount_storage
from backend.utils.auth_storage import save_users
from backend.utils.tricount_storage import save_tricounts

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

os.environ.setdefault("JWT_SECRET_KEY", "xxx")


@pytest.fixture
def app(tmp_path_factory):
    data_dir = tmp_path_factory.mktemp("data")
    auth_storage.DATA_FILE = Path(data_dir) / "users.json"
    tricount_storage.DATA_FILE = Path(data_dir) / "tricounts.json"

    tricount_routes.tricounts = []

    api_tricount.app.config.update(
        {
            "TESTING": True,
            "JWT_SECRET_KEY": "xxx",
            "JWT_ACCESS_TOKEN_EXPIRES": timedelta(hours=1),
        }
    )

    save_users([])
    save_tricounts([])

    yield api_tricount.app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "user@test.com",
            "password": "pass123",
            "name": "User",
        },
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "user@test.com", "password": "pass123"},
    )
    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

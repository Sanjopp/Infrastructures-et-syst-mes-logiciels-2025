import os
import sys
from datetime import timedelta

import pytest

# Add the parent directory to the path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from backend.api.tricount import app as flask_app
from backend.extensions import bcrypt, jwt
from backend.utils.auth_storage import save_users
from backend.utils.tricount_storage import save_tricounts


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    flask_app.config.update(
        {
            "TESTING": True,
            "JWT_SECRET_KEY": "test-secret-key-for-testing-only",
            "JWT_ACCESS_TOKEN_EXPIRES": timedelta(hours=1),
        }
    )

    # Clear data files before each test
    save_users([])
    save_tricounts([])

    yield flask_app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """Create a user and return auth headers."""
    # Register a test user
    client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User",
        },
    )

    # Login
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )

    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

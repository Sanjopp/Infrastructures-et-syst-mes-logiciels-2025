import os
import sys
from datetime import timedelta
from pathlib import Path

import pytest

# S’assurer que le projet est sur le PYTHONPATH
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

# Clé JWT pour les tests (avant l’import de l’app)
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only")


@pytest.fixture
def app(tmp_path_factory):
    """Configure une app Flask isolée pour les tests."""
    # Répertoires de données temporaires pour éviter les permissions sur ./data
    data_dir = tmp_path_factory.mktemp("data")
    from backend.utils import auth_storage, tricount_storage

    auth_storage.DATA_FILE = Path(data_dir) / "users.json"
    tricount_storage.DATA_FILE = Path(data_dir) / "tricounts.json"

    # Import de l’app après avoir positionné les chemins de données
    from backend.api import tricount as api_tricount
    from backend.routes import tricounts as tricount_routes

    # Réinitialiser l’état en mémoire
    tricount_routes.tricounts = []

    api_tricount.app.config.update(
        {
            "TESTING": True,
            "JWT_SECRET_KEY": "test-secret-key-for-testing-only",
            "JWT_ACCESS_TOKEN_EXPIRES": timedelta(hours=1),
        }
    )

    # Vider les fichiers de données (dans le répertoire temporaire)
    from backend.utils.auth_storage import save_users
    from backend.utils.tricount_storage import save_tricounts

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
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User",
        },
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

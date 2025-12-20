def test_register_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "user@test.com",
            "password": "pass123",
            "name": "User",
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data


def test_register_missing_fields(client):
    # Missing password
    response = client.post(
        "/api/auth/register",
        json={"email": "user@test.com", "name": "User no password"},
    )
    assert response.status_code == 400

    # Missing email
    response = client.post(
        "/api/auth/register",
        json={"password": "pass123", "name": "User no email"},
    )
    assert response.status_code == 400

    # Missing name
    response = client.post(
        "/api/auth/register",
        json={"email": "usernoname@test.com", "password": "pass123"},
    )
    assert response.status_code == 400


def test_register_duplicate_email(client):
    # Register user
    client.post(
        "/api/auth/register",
        json={
            "email": "user@test.com",
            "password": "pass123",
            "name": "User 1",
        },
    )

    # Try to register with same email
    response = client.post(
        "/api/auth/register",
        json={
            "email": "user@test.com",
            "password": "pass123",
            "name": "User 2",
        },
    )

    assert response.status_code == 409
    data = response.get_json()
    assert "déjà utilisé" in data["error"]


def test_login_success(client):
    # Register user
    client.post(
        "/api/auth/register",
        json={
            "email": "user@test.com",
            "password": "pass123",
            "name": "User",
        },
    )

    # Login
    response = client.post(
        "/api/auth/login",
        json={"email": "user@test.com", "password": "pass123"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert "auth_user" in data
    assert data["auth_user"]["email"] == "user@test.com"
    assert data["auth_user"]["name"] == "User"


def test_login_invalid_credentials(client):
    # Register user
    client.post(
        "/api/auth/register",
        json={
            "email": "user@test.com",
            "password": "pass123",
            "name": "User",
        },
    )

    # Wrong password
    response = client.post(
        "/api/auth/login",
        json={"email": "user@test.com", "password": "wrongpass123"},
    )
    assert response.status_code == 401

    # Non-existent email
    response = client.post(
        "/api/auth/login",
        json={"email": "notuser@test.com", "password": "pass123"},
    )
    assert response.status_code == 401


def test_login_missing_fields(client):
    # Missing email
    response = client.post("/api/auth/login", json={"email": "user@test.com"})
    assert response.status_code == 400

    # Missing password
    response = client.post("/api/auth/login", json={"password": "pass123"})
    assert response.status_code == 400

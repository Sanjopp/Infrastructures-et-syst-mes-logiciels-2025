def test_register_success(client):
    """Test successful user registration."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "securepass123",
            "name": "New User",
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Utilisateur créé avec succès"
    assert "id" in data


def test_register_missing_fields(client):
    """Test registration with missing fields."""
    # Missing password
    response = client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "name": "User"},
    )
    assert response.status_code == 400

    # Missing email
    response = client.post(
        "/api/auth/register", json={"password": "pass123", "name": "User"}
    )
    assert response.status_code == 400

    # Missing name
    response = client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "password": "pass123"},
    )
    assert response.status_code == 400


def test_register_duplicate_email(client):
    """Test registration with duplicate email."""
    # First registration
    client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "pass123",
            "name": "User One",
        },
    )

    # Try to register with same email
    response = client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "pass456",
            "name": "User Two",
        },
    )

    assert response.status_code == 409
    data = response.get_json()
    assert "déjà utilisé" in data["error"]


def test_login_success(client):
    """Test successful login."""
    # Register user first
    client.post(
        "/api/auth/register",
        json={
            "email": "login@example.com",
            "password": "mypass123",
            "name": "Login User",
        },
    )

    # Login
    response = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "mypass123"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert "auth_user" in data
    assert data["auth_user"]["email"] == "login@example.com"
    assert data["auth_user"]["name"] == "Login User"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    # Register user
    client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "password": "correctpass",
            "name": "User",
        },
    )

    # Wrong password
    response = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401

    # Non-existent email
    response = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "somepass"},
    )
    assert response.status_code == 401


def test_login_missing_fields(client):
    """Test login with missing fields."""
    response = client.post(
        "/api/auth/login", json={"email": "user@example.com"}
    )
    assert response.status_code == 400

    response = client.post("/api/auth/login", json={"password": "pass123"})
    assert response.status_code == 400

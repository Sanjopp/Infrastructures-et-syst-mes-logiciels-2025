def test_create_tricount(client, auth_headers):
    response = client.post(
        "/api/tricounts", json={"name": "Tricount"}, headers=auth_headers
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Tricount"
    assert data["currency"] == "EUR"
    assert "id" in data
    assert data["users"] == []
    assert data["expenses"] == []
    assert data["balances"] == {}


def test_create_tricount_missing_name(client, auth_headers):
    response = client.post("/api/tricounts", json={}, headers=auth_headers)
    assert response.status_code == 400


def test_create_tricount_without_auth(client):
    response = client.post("/api/tricounts", json={"name": "Tricount"})
    assert response.status_code == 401


def test_list_tricounts(client, auth_headers):
    # Create two tricounts
    client.post(
        "/api/tricounts", json={"name": "Tricount1"}, headers=auth_headers
    )
    client.post(
        "/api/tricounts", json={"name": "Tricount2"}, headers=auth_headers
    )

    response = client.get("/api/tricounts", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["name"] == "Tricount1"
    assert data[1]["name"] == "Tricount2"


def test_get_tricount(client, auth_headers):
    # Create a tricount
    create_response = client.post(
        "/api/tricounts", json={"name": "Tricount"}, headers=auth_headers
    )
    tricount_id = create_response.get_json()["id"]

    # Get the tricount
    response = client.get(
        f"/api/tricounts/{tricount_id}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Tricount"
    assert data["id"] == tricount_id


def test_get_nonexistent_tricount(client, auth_headers):
    response = client.get("/api/tricounts/nonexistent", headers=auth_headers)
    assert response.status_code == 404


def test_add_user_to_tricount(client, auth_headers):
    # Create tricount
    create_response = client.post(
        "/api/tricounts",
        json={"name": "Tricount"},
        headers=auth_headers,
    )
    tricount_id = create_response.get_json()["id"]

    # Add user
    response = client.post(
        f"/api/tricounts/{tricount_id}/users",
        json={"name": "User", "email": "user@test.com"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "User"
    assert data["email"] == "user@test.com"


def test_add_user_without_name(client, auth_headers):
    create_response = client.post(
        "/api/tricounts", json={"name": "Tricount"}, headers=auth_headers
    )
    tricount_id = create_response.get_json()["id"]

    response = client.post(
        f"/api/tricounts/{tricount_id}/users",
        json={"email": "test@user.com"},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_delete_user_from_tricount(client, auth_headers):
    # Create tricount and add user
    create_response = client.post(
        "/api/tricounts", json={"name": "Tricount"}, headers=auth_headers
    )
    tricount_id = create_response.get_json()["id"]

    user_response = client.post(
        f"/api/tricounts/{tricount_id}/users",
        json={"name": "User"},
        headers=auth_headers,
    )
    user_id = user_response.get_json()["id"]

    # Delete user
    response = client.delete(
        f"/api/tricounts/{tricount_id}/users/{user_id}", headers=auth_headers
    )
    assert response.status_code == 200

    # Verify user is deleted
    get_response = client.get(
        f"/api/tricounts/{tricount_id}/users", headers=auth_headers
    )
    data = get_response.get_json()
    assert len(data) == 0


def test_add_expense(client, auth_headers):
    # Create tricount
    create_response = client.post(
        "/api/tricounts", json={"name": "Tricount"}, headers=auth_headers
    )
    tricount_id = create_response.get_json()["id"]

    # Add users
    user1_response = client.post(
        f"/api/tricounts/{tricount_id}/users",
        json={"name": "User1"},
        headers=auth_headers,
    )
    user1_id = user1_response.get_json()["id"]

    user2_response = client.post(
        f"/api/tricounts/{tricount_id}/users",
        json={"name": "User2"},
        headers=auth_headers,
    )
    user2_id = user2_response.get_json()["id"]

    # Add expense
    response = client.post(
        f"/api/tricounts/{tricount_id}/expenses",
        json={
            "description": "Expense",
            "amount": 100.0,
            "payer_id": user1_id,
            "participants_ids": [user1_id, user2_id],
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.get_json()
    assert len(data["expenses"]) == 1
    assert data["expenses"][0]["description"] == "Expense"
    assert data["expenses"][0]["amount"] == 100.0


def test_add_expense_missing_fields(client, auth_headers):
    create_response = client.post(
        "/api/tricounts", json={"name": "Tricount"}, headers=auth_headers
    )
    tricount_id = create_response.get_json()["id"]

    # Missing description
    response = client.post(
        f"/api/tricounts/{tricount_id}/expenses",
        json={
            "amount": 50.0,
            "payer_id": "User1",
            "participants_ids": ["User1"],
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_unauthorized_access_to_tricount(client):
    # Create user 1 and tricount
    client.post(
        "/api/auth/register",
        json={
            "email": "user1@test.com",
            "password": "pass123",
            "name": "User1",
        },
    )
    login1 = client.post(
        "/api/auth/login",
        json={"email": "user1@test.com", "password": "pass123"},
    )
    token1 = login1.get_json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    create_response = client.post(
        "/api/tricounts", json={"name": "Tricount"}, headers=headers1
    )
    tricount_id = create_response.get_json()["id"]

    # Create user 2
    client.post(
        "/api/auth/register",
        json={
            "email": "user2@test.com",
            "password": "pass123",
            "name": "User2",
        },
    )
    login2 = client.post(
        "/api/auth/login",
        json={"email": "user2@test.com", "password": "pass123"},
    )
    token2 = login2.get_json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # User 2 tries to access User 1's tricount
    response = client.get(f"/api/tricounts/{tricount_id}", headers=headers2)
    assert response.status_code == 404

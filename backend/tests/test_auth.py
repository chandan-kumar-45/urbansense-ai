def test_register_and_login(client):
    res = client.post(
        "/api/auth/register",
        json={"name": "Alice", "email": "alice@test.local", "password": "Password123", "role": "ANALYST"},
    )
    assert res.status_code == 201
    assert res.json()["user"]["email"] == "alice@test.local"

    res = client.post(
        "/api/auth/login", json={"email": "alice@test.local", "password": "Password123"}
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password_rejected(client):
    client.post(
        "/api/auth/register",
        json={"name": "Bob", "email": "bob@test.local", "password": "Password123", "role": "ANALYST"},
    )
    res = client.post("/api/auth/login", json={"email": "bob@test.local", "password": "wrong"})
    assert res.status_code == 401


def test_me_requires_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_me_returns_current_user(client, admin_token):
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert res.json()["role"] == "ADMIN"


def test_duplicate_email_rejected(client):
    payload = {"name": "Carl", "email": "carl@test.local", "password": "Password123", "role": "ANALYST"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    assert client.post("/api/auth/register", json=payload).status_code == 400

def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_create_and_list_event(client, admin_token):
    payload = {
        "event_type": "pothole",
        "latitude": 26.91,
        "longitude": 75.78,
        "confidence": 0.8,
        "severity": "HIGH",
        "model_name": "test_model",
        "model_version": "0.0.1",
        "is_demo": True,
    }
    res = client.post("/api/events", json=payload)
    assert res.status_code == 201
    event_id = res.json()["id"]
    assert res.json()["is_demo"] is True

    res = client.get("/api/events", headers=auth_header(admin_token))
    assert res.status_code == 200
    assert any(e["id"] == event_id for e in res.json())


def test_events_require_auth_to_list(client):
    res = client.get("/api/events")
    assert res.status_code == 401


def test_event_status_update(client, admin_token):
    payload = {
        "event_type": "debris",
        "latitude": 26.9,
        "longitude": 75.8,
        "confidence": 0.6,
        "model_name": "test_model",
        "model_version": "0.0.1",
    }
    event_id = client.post("/api/events", json=payload).json()["id"]

    res = client.patch(
        f"/api/events/{event_id}/status",
        json={"status": "ACKNOWLEDGED"},
        headers=auth_header(admin_token),
    )
    assert res.status_code == 200
    assert res.json()["status"] == "ACKNOWLEDGED"


def test_incidents_require_privileged_role(client):
    # An ANALYST (not Admin/Traffic Officer/Transport Authority) must be
    # rejected — this is the server-side RBAC the frontend also mirrors.
    client.post(
        "/api/auth/register",
        json={"name": "Ana", "email": "ana@test.local", "password": "Password123", "role": "ANALYST"},
    )
    token = client.post(
        "/api/auth/login", json={"email": "ana@test.local", "password": "Password123"}
    ).json()["access_token"]

    res = client.get("/api/incidents", headers=auth_header(token))
    assert res.status_code == 403

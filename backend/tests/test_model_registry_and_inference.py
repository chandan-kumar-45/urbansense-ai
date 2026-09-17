import io

import cv2
import numpy as np


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _synthetic_road_image_bytes() -> bytes:
    """A plain gray image with a dark irregular blob — enough for the
    adaptive-threshold heuristic to have something to find, without needing a
    real photo checked into the test suite."""
    img = np.full((240, 320, 3), 180, dtype=np.uint8)
    cv2.ellipse(img, (160, 120), (40, 25), 15, 0, 360, (40, 40, 40), -1)
    ok, buf = cv2.imencode(".jpg", img)
    assert ok
    return buf.tobytes()


def test_model_registry_seeded_and_active(client, admin_token):
    res = client.get("/api/models", headers=auth_header(admin_token))
    assert res.status_code == 200
    models = res.json()
    road_damage_versions = [m for m in models if m["model_name"] == "road_damage"]
    assert road_damage_versions, "road_damage should be seeded on startup"
    assert any(m["status"] == "ACTIVE" for m in road_damage_versions)
    assert all(m["is_demo"] for m in road_damage_versions if m["status"] == "ACTIVE")


def test_register_and_activate_new_model_version(client, admin_token):
    res = client.post(
        "/api/models/register",
        json={
            "model_name": "road_damage",
            "version": "9.9.9-test",
            "model_type": "classical-cv-heuristic",
            "supported_classes": ["pothole"],
            "framework": "opencv-heuristic",
            "is_demo": True,
        },
        headers=auth_header(admin_token),
    )
    assert res.status_code == 201
    assert res.json()["status"] == "TESTING"

    model_id = res.json()["id"]
    res = client.post(f"/api/models/{model_id}/activate", headers=auth_header(admin_token))
    assert res.status_code == 200
    assert res.json()["status"] == "ACTIVE"


def test_inference_runs_active_road_damage_model(client, admin_token):
    files = {"file": ("test.jpg", _synthetic_road_image_bytes(), "image/jpeg")}
    res = client.post(
        "/api/inference",
        data={"capability": "road_damage"},
        files=files,
        headers=auth_header(admin_token),
    )
    assert res.status_code == 200
    body = res.json()
    assert body["model"] == "road_damage"
    assert body["is_demo"] is True
    assert isinstance(body["detections"], list)


def test_inference_rejects_bad_capability(client, admin_token):
    files = {"file": ("test.jpg", _synthetic_road_image_bytes(), "image/jpeg")}
    res = client.post(
        "/api/inference",
        data={"capability": "does_not_exist"},
        files=files,
        headers=auth_header(admin_token),
    )
    assert res.status_code == 404


def test_inference_rejects_non_image_file(client, admin_token):
    files = {"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
    res = client.post(
        "/api/inference",
        data={"capability": "road_damage"},
        files=files,
        headers=auth_header(admin_token),
    )
    assert res.status_code == 400

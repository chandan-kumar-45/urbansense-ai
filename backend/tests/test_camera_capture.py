def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_camera_capture_runs_real_model_and_tags_camera(client, admin_token):
    bus_id = client.get("/api/buses", headers=auth_header(admin_token)).json()[0]["id"]
    cameras = client.get(
        f"/api/buses/{bus_id}/cameras", headers=auth_header(admin_token)
    ).json()
    assert len(cameras) == 4  # every seeded bus has FRONT/REAR/LEFT/RIGHT

    camera_id = cameras[0]["id"]
    res = client.post(
        f"/api/buses/{bus_id}/cameras/{camera_id}/capture",
        headers=auth_header(admin_token),
    )
    assert res.status_code == 200
    defects = res.json()
    # A capture may or may not find a defect (capture_frame() only sometimes
    # draws a detectable blob) — either outcome is valid. If one was found,
    # it must be correctly tagged to this exact bus + camera.
    for d in defects:
        assert d["bus_id"] == bus_id
        assert d["camera_id"] == camera_id
        assert d["model_name"] == "road_damage"


def test_capture_rejects_camera_not_on_bus(client, admin_token):
    buses = client.get("/api/buses", headers=auth_header(admin_token)).json()
    bus_a, bus_b = buses[0]["id"], buses[1]["id"]
    camera_on_b = client.get(
        f"/api/buses/{bus_b}/cameras", headers=auth_header(admin_token)
    ).json()[0]["id"]

    res = client.post(
        f"/api/buses/{bus_a}/cameras/{camera_on_b}/capture",
        headers=auth_header(admin_token),
    )
    assert res.status_code == 404

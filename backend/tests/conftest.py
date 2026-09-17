"""
Test fixtures. Forces the app onto an isolated in-memory SQLite DB (distinct
from the dev urbansense.db) *before* app.main is imported, so the module-level
engine in app/database/session.py is created against it directly — startup
seeding (app.main.seed_demo_data) and every API request then share the exact
same in-memory database. See the StaticPool note in app/database/session.py:
without it, SQLite's `:memory:` gives every new connection a separate blank
DB, which would make startup seeding invisible to API requests.
"""
import os

os.environ["URBANSENSE_DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient

from app.database.session import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def _fresh_schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def admin_token(client):
    client.post(
        "/api/auth/register",
        json={"name": "Test Admin", "email": "admin@test.local", "password": "Password123", "role": "ADMIN"},
    )
    res = client.post(
        "/api/auth/login", json={"email": "admin@test.local", "password": "Password123"}
    )
    return res.json()["access_token"]

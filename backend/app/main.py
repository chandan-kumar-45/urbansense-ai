import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importing each capability's adapter module registers its factory with the
# AI Model Registry as a side effect (see app/ai/road_damage/adapter.py). New
# capabilities (Phase 9+) get one more import line here — nothing else changes.
import app.ai.road_damage.adapter  # noqa: F401

from app.api import (
    analytics,
    auth,
    buses,
    cameras,
    events,
    incidents,
    inference,
    models_registry,
    reports,
    road_damage,
    simulation,
    traffic,
    video,
)
from app.core.config import settings
from app.core.security import hash_password
from app.database.models import (
    Bus,
    Camera,
    CameraType,
    ModelStatus,
    ModelVersion,
    User,
    UserRole,
)
from app.database.session import SessionLocal, init_db
from app.websocket.routes import router as websocket_router


def seed_demo_data() -> None:
    """
    Creates one login per role (all clearly demo credentials, printed to console
    on first boot) plus a couple of sample buses/cameras so the app isn't empty
    on first run. Safe to call repeatedly — it checks for existing rows first.
    """
    db = SessionLocal()
    try:
        if not db.query(User).first():
            demo_users = [
                ("Admin User", "admin@urbansense.ai", UserRole.ADMIN),
                ("Transport Authority", "authority@urbansense.ai", UserRole.TRANSPORT_AUTHORITY),
                ("Traffic Officer", "traffic@urbansense.ai", UserRole.TRAFFIC_OFFICER),
                ("Maintenance Officer", "maintenance@urbansense.ai", UserRole.MAINTENANCE_OFFICER),
                ("Analyst", "analyst@urbansense.ai", UserRole.ANALYST),
            ]
            for name, email, role in demo_users:
                db.add(
                    User(
                        name=name,
                        email=email,
                        password_hash=hash_password("Demo@123"),
                        role=role,
                    )
                )
            db.commit()
            print("=" * 60)
            print("UrbanSense AI — demo accounts seeded (password: Demo@123)")
            for _, email, role in demo_users:
                print(f"  {role.value:<22} {email}")
            print("=" * 60)

        if not db.query(Bus).first():
            sample_buses = [
                ("RJ14-1234", "Route 12", 26.9124, 75.7873),
                ("RJ14-5678", "Route 7", 26.8850, 75.8040),
            ]
            for bus_number, route, lat, lng in sample_buses:
                bus = Bus(
                    bus_number=bus_number,
                    registration_number=bus_number,
                    route=route,
                    latitude=lat,
                    longitude=lng,
                    is_simulated=True,
                )
                db.add(bus)
                db.flush()
                for cam_type in [CameraType.FRONT, CameraType.REAR, CameraType.LEFT, CameraType.RIGHT]:
                    db.add(Camera(bus_id=bus.id, camera_type=cam_type))
            db.commit()

        if not db.query(ModelVersion).filter(ModelVersion.model_name == "road_damage").first():
            from app.ai.road_damage.config import DEMO_MODEL_VERSION, SUPPORTED_CLASSES

            db.add(
                ModelVersion(
                    model_name="road_damage",
                    version=DEMO_MODEL_VERSION,
                    model_type="classical-cv-heuristic",
                    supported_classes=json.dumps(SUPPORTED_CLASSES),
                    framework="opencv-heuristic",
                    accuracy_metrics=json.dumps({}),
                    is_demo=True,
                    status=ModelStatus.ACTIVE,
                )
            )
            db.commit()
            print(
                "UrbanSense AI — seeded 'road_damage' model registry: "
                f"{DEMO_MODEL_VERSION} (DEMO heuristic, ACTIVE)"
            )
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_demo_data()
    yield


app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Mobile Urban Intelligence Platform — SIH 2026, PS 26124 (BEL)",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(buses.router)
app.include_router(cameras.router)
app.include_router(events.router)
app.include_router(road_damage.router)
app.include_router(traffic.router)
app.include_router(incidents.router)
app.include_router(models_registry.router)
app.include_router(inference.router)
app.include_router(video.router)
app.include_router(simulation.router)
app.include_router(analytics.router)
app.include_router(reports.router)
app.include_router(websocket_router)


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}

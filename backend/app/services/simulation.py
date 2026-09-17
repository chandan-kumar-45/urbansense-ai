"""
The engine behind "Start Live Simulation". This is a real asyncio background
task inside the FastAPI process — not a UI trick. It moves simulated buses
along fixed routes and periodically writes real rows through the same
DB session + WebSocket broadcast path the REST APIs use, so everything
downstream (dashboard, GIS, analytics) is exercised for real.

Road damage detection during simulation runs through the REAL per-camera
pipeline in app/services/capture.py: one of the bus's 4 cameras "captures" a
frame and it's run through whatever model is currently ACTIVE for
"road_damage" via the AI Model Registry — the exact same path the AI
Detection Lab uses. Only the frame itself is synthetic (no live camera feed
in this prototype); the inference is genuine.

Traffic and incident generation, by contrast, have no underlying trained
model in this prototype, so those rows are still tagged
`model_name="simulation_engine"`, `is_demo=True` — honestly labeled as pure
simulation rather than dressed up as AI output they aren't.
"""
from __future__ import annotations

import asyncio
import random
from datetime import datetime

from app.database.models import (
    Bus,
    BusStatus,
    Camera,
    Incident,
    IncidentType,
    Severity,
    TrafficEvent,
)
from app.database.session import SessionLocal
from app.services.capture import capture_and_detect
from app.websocket.manager import manager

# Two illustrative routes around Jaipur (lat/lng waypoints). Real deployments
# would use actual GTFS/route-shape data; these are for demo purposes only.
ROUTES: dict[str, list[tuple[float, float]]] = {
    "Route 12": [
        (26.9124, 75.7873),
        (26.9155, 75.8010),
        (26.9200, 75.8130),
        (26.9260, 75.8250),
    ],
    "Route 7": [
        (26.8850, 75.8040),
        (26.8900, 75.7950),
        (26.8990, 75.7870),
        (26.9050, 75.7790),
    ],
}

LOCATIONS = list(ROUTES.keys())


class SimulationEngine:
    def __init__(self) -> None:
        self._task: asyncio.Task | None = None
        self._running = False
        self._tick_count = 0
        self._events_generated = 0
        self._route_progress: dict[str, float] = {}

        # Simulated bandwidth accounting, per docs/ARCHITECTURE.md §6. These are
        # illustrative constants, not a measured cellular modem.
        self.raw_stream_kbps_per_camera = 625  # ~5 Mbps
        self.avg_event_payload_kb = 4.5  # JSON + no/low-res evidence image

    @property
    def running(self) -> bool:
        return self._running

    def status(self) -> dict:
        elapsed_minutes = max(self._tick_count * 3 / 60, 0.001)  # tick every 3s
        raw_bytes_per_min = self.raw_stream_kbps_per_camera * 1024 / 8 * 60 * 4  # 4 cams/bus
        raw_total_kb = (raw_bytes_per_min * elapsed_minutes * len(ROUTES)) / 1024
        sent_total_kb = self._events_generated * self.avg_event_payload_kb
        saved_pct = 0.0
        if raw_total_kb > 0:
            saved_pct = max(0.0, min(99.9, 100 * (1 - sent_total_kb / raw_total_kb)))

        return {
            "running": self._running,
            "ticks": self._tick_count,
            "events_generated": self._events_generated,
            "bandwidth_saved_percent": round(saved_pct, 1),
            "is_demo": True,
            "note": "Simulated fleet + bandwidth metrics — see docs/ARCHITECTURE.md §6 and §8.",
        }

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None

    async def _loop(self) -> None:
        try:
            while self._running:
                await self._tick()
                self._tick_count += 1
                await asyncio.sleep(3)
        except asyncio.CancelledError:
            pass

    async def _tick(self) -> None:
        db = SessionLocal()
        try:
            buses = db.query(Bus).filter(Bus.is_simulated == True).all()  # noqa: E712
            for bus in buses:
                route = ROUTES.get(bus.route or "", ROUTES[LOCATIONS[0]])
                progress = self._route_progress.get(bus.id, 0.0)
                progress = (progress + 0.08) % (len(route) - 1)
                self._route_progress[bus.id] = progress

                seg = int(progress)
                frac = progress - seg
                lat1, lng1 = route[seg]
                lat2, lng2 = route[min(seg + 1, len(route) - 1)]
                lat = lat1 + (lat2 - lat1) * frac
                lng = lng1 + (lng2 - lng1) * frac

                bus.latitude = lat
                bus.longitude = lng
                bus.speed_kmph = round(random.uniform(18, 42), 1)
                bus.heading_deg = round(random.uniform(0, 359), 1)
                bus.status = BusStatus.ACTIVE
                bus.last_seen = datetime.utcnow()
                db.commit()
                db.refresh(bus)

                await manager.broadcast(
                    "bus_position",
                    {
                        "id": bus.id,
                        "bus_number": bus.bus_number,
                        "latitude": bus.latitude,
                        "longitude": bus.longitude,
                        "speed_kmph": bus.speed_kmph,
                        "heading_deg": bus.heading_deg,
                        "status": bus.status.value,
                        "last_seen": bus.last_seen,
                    },
                )

                # Real per-camera capture-and-detect cycle: one of the bus's 4
                # cameras (FRONT/REAR/LEFT/RIGHT) "captures" a frame and it's
                # run through whatever model is currently ACTIVE for
                # "road_damage" via the same registry the AI Detection Lab
                # uses. See app/services/capture.py for why the frame is
                # synthetic but the inference is real.
                if random.random() < 0.35:
                    cameras = db.query(Camera).filter(Camera.bus_id == bus.id).all()
                    if cameras:
                        camera = random.choice(cameras)
                        created = await capture_and_detect(db, bus, camera)
                        self._events_generated += len(created)

                # Occasionally generate a traffic reading for this route.
                if random.random() < 0.25:
                    congestion = random.choices(
                        ["LOW", "MEDIUM", "HIGH"], weights=[0.5, 0.35, 0.15]
                    )[0]
                    traffic = TrafficEvent(
                        location=bus.route or "Unknown route",
                        latitude=lat,
                        longitude=lng,
                        vehicle_count=random.randint(5, 80),
                        density=round(random.uniform(0.1, 0.95), 2),
                        congestion_level=congestion,
                        average_speed_kmph=round(random.uniform(8, 45), 1),
                        is_demo=True,
                    )
                    db.add(traffic)
                    db.commit()
                    db.refresh(traffic)
                    self._events_generated += 1
                    await manager.broadcast(
                        "traffic_event",
                        {
                            "id": traffic.id,
                            "location": traffic.location,
                            "latitude": traffic.latitude,
                            "longitude": traffic.longitude,
                            "vehicle_count": traffic.vehicle_count,
                            "density": traffic.density,
                            "congestion_level": traffic.congestion_level,
                            "average_speed_kmph": traffic.average_speed_kmph,
                            "timestamp": traffic.timestamp,
                            "is_demo": True,
                        },
                    )

                # Rarely, generate an incident.
                if random.random() < 0.04:
                    incident_type = random.choice(list(IncidentType))
                    incident = Incident(
                        incident_type=incident_type,
                        severity=random.choice([Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]),
                        confidence=round(random.uniform(0.6, 0.93), 2),
                        latitude=lat,
                        longitude=lng,
                        bus_id=bus.id,
                        model_name="simulation_engine",
                        model_version="sim-1.0",
                        is_demo=True,
                    )
                    db.add(incident)
                    db.commit()
                    db.refresh(incident)
                    self._events_generated += 1
                    await manager.broadcast(
                        "incident",
                        {
                            "id": incident.id,
                            "incident_type": incident.incident_type.value,
                            "severity": incident.severity.value,
                            "confidence": incident.confidence,
                            "latitude": incident.latitude,
                            "longitude": incident.longitude,
                            "timestamp": incident.timestamp,
                            "bus_id": incident.bus_id,
                            "model_name": incident.model_name,
                            "model_version": incident.model_version,
                            "is_demo": True,
                            "status": incident.status.value,
                        },
                    )
        finally:
            db.close()


engine = SimulationEngine()

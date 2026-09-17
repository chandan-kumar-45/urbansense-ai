"""
UrbanSense AI — Database Models
================================

Default target: SQLite (zero-install local/demo use — set in .env as
`DATABASE_URL=sqlite:///./urbansense.db`).

Production target: PostgreSQL + PostGIS (set `DATABASE_URL=postgresql+psycopg2://...`
and change `Latitude/Longitude Float columns` to `Geometry('POINT', srid=4326)` via
GeoAlchemy2 — see docs/AI_MODEL_INTEGRATION.md and docs/ARCHITECTURE.md §9). We keep
lat/lng as plain floats here so the exact same models run on SQLite with no extra
system dependencies during an SIH demo; the migration to PostGIS geometry columns is
a follow-up, documented step, not a hidden requirement.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def gen_uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    TRANSPORT_AUTHORITY = "TRANSPORT_AUTHORITY"
    TRAFFIC_OFFICER = "TRAFFIC_OFFICER"
    MAINTENANCE_OFFICER = "MAINTENANCE_OFFICER"
    ANALYST = "ANALYST"


class BusStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    DELAYED = "DELAYED"
    INCIDENT = "INCIDENT"
    OFFLINE = "OFFLINE"


class CameraType(str, enum.Enum):
    FRONT = "FRONT"
    REAR = "REAR"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    CABIN = "CABIN"


class CameraStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    FAULT = "FAULT"


class Severity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EventStatus(str, enum.Enum):
    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class IncidentType(str, enum.Enum):
    HIT_AND_RUN = "HIT_AND_RUN"
    RASH_DRIVING = "RASH_DRIVING"
    ACCIDENT = "ACCIDENT"
    PEDESTRIAN_RISK = "PEDESTRIAN_RISK"
    ROAD_HAZARD = "ROAD_HAZARD"
    WATERLOGGING = "WATERLOGGING"
    TRAFFIC_CONGESTION = "TRAFFIC_CONGESTION"


class ModelStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    TESTING = "TESTING"
    INACTIVE = "INACTIVE"


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.ANALYST)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# Fleet
# ---------------------------------------------------------------------------

class Bus(Base):
    __tablename__ = "buses"

    id = Column(String, primary_key=True, default=gen_uuid)
    bus_number = Column(String, unique=True, nullable=False)
    registration_number = Column(String, unique=True, nullable=False)
    route = Column(String, nullable=True)
    status = Column(Enum(BusStatus), default=BusStatus.OFFLINE)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    speed_kmph = Column(Float, default=0.0)
    heading_deg = Column(Float, default=0.0)
    last_seen = Column(DateTime, nullable=True)
    is_simulated = Column(Boolean, default=True)  # honesty flag: real telemetry vs demo

    cameras = relationship("Camera", back_populates="bus")


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(String, primary_key=True, default=gen_uuid)
    bus_id = Column(String, ForeignKey("buses.id"), nullable=False)
    camera_type = Column(Enum(CameraType), nullable=False)
    status = Column(Enum(CameraStatus), default=CameraStatus.ONLINE)

    bus = relationship("Bus", back_populates="cameras")


# ---------------------------------------------------------------------------
# Detection Events (generic — every AI capability writes here)
# ---------------------------------------------------------------------------

class DetectionEvent(Base):
    __tablename__ = "detection_events"

    id = Column(String, primary_key=True, default=gen_uuid)
    event_type = Column(String, nullable=False)  # e.g. "pothole", "waterlogging", "rash_driving"
    bus_id = Column(String, ForeignKey("buses.id"), nullable=True)
    camera_id = Column(String, ForeignKey("cameras.id"), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    confidence = Column(Float, nullable=False)
    severity = Column(Enum(Severity), default=Severity.LOW)
    image_path = Column(String, nullable=True)
    video_path = Column(String, nullable=True)
    vehicle_id = Column(String, nullable=True)
    license_plate = Column(String, nullable=True)
    model_name = Column(String, nullable=False)
    model_version = Column(String, nullable=False)
    is_demo = Column(Boolean, default=True, nullable=False)  # honesty flag
    status = Column(Enum(EventStatus), default=EventStatus.NEW)


# ---------------------------------------------------------------------------
# Road Defects
# ---------------------------------------------------------------------------

class RoadDefect(Base):
    __tablename__ = "road_defects"

    id = Column(String, primary_key=True, default=gen_uuid)
    defect_type = Column(String, nullable=False)  # pothole, cracked_road, damaged_asphalt, ...
    severity = Column(Enum(Severity), default=Severity.LOW)
    confidence = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    detected_at = Column(DateTime, default=datetime.utcnow)
    bus_id = Column(String, ForeignKey("buses.id"), nullable=True)
    camera_id = Column(String, ForeignKey("cameras.id"), nullable=True)
    image = Column(String, nullable=True)
    model_name = Column(String, default="road_damage")
    model_version = Column(String, nullable=True)
    is_demo = Column(Boolean, default=True, nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.NEW)

    bus = relationship("Bus")
    camera = relationship("Camera")


# ---------------------------------------------------------------------------
# Traffic
# ---------------------------------------------------------------------------

class TrafficEvent(Base):
    __tablename__ = "traffic_events"

    id = Column(String, primary_key=True, default=gen_uuid)
    location = Column(String, nullable=False)  # human-readable / route segment name
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    vehicle_count = Column(Integer, default=0)
    density = Column(Float, default=0.0)  # 0..1
    congestion_level = Column(String, default="LOW")  # LOW / MEDIUM / HIGH
    average_speed_kmph = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_demo = Column(Boolean, default=True, nullable=False)


# ---------------------------------------------------------------------------
# Incidents
# ---------------------------------------------------------------------------

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, default=gen_uuid)
    incident_type = Column(Enum(IncidentType), nullable=False)
    severity = Column(Enum(Severity), default=Severity.MEDIUM)
    vehicle_number = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    evidence_image = Column(String, nullable=True)
    evidence_video = Column(String, nullable=True)
    bus_id = Column(String, ForeignKey("buses.id"), nullable=True)
    camera_id = Column(String, ForeignKey("cameras.id"), nullable=True)
    model_name = Column(String, nullable=True)
    model_version = Column(String, nullable=True)
    is_demo = Column(Boolean, default=True, nullable=False)
    assigned_officer_id = Column(String, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(EventStatus), default=EventStatus.NEW)


# ---------------------------------------------------------------------------
# AI Model Registry
# ---------------------------------------------------------------------------

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(String, primary_key=True, default=gen_uuid)
    model_name = Column(String, nullable=False)  # e.g. "road_damage"
    version = Column(String, nullable=False)  # e.g. "1.0.0-demo"
    model_type = Column(String, nullable=False)  # e.g. "heuristic", "yolov8", "onnx"
    supported_classes = Column(Text, nullable=True)  # JSON-encoded list
    framework = Column(String, nullable=True)  # pytorch / onnx / tensorrt / none
    accuracy_metrics = Column(Text, nullable=True)  # JSON-encoded metrics dict
    is_demo = Column(Boolean, default=True, nullable=False)
    status = Column(Enum(ModelStatus), default=ModelStatus.INACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = ()

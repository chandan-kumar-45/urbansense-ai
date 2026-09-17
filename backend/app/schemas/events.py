from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.database.models import EventStatus, Severity


class DetectionEventCreate(BaseModel):
    """What an edge node / simulator posts to /api/events for any detection."""
    model_config = ConfigDict(protected_namespaces=())

    event_type: str = Field(..., description='e.g. "pothole", "waterlogging", "rash_driving"')
    bus_id: Optional[str] = None
    camera_id: Optional[str] = None
    latitude: float
    longitude: float
    timestamp: Optional[datetime] = None
    confidence: float
    severity: Severity = Severity.LOW
    image_path: Optional[str] = None
    video_path: Optional[str] = None
    vehicle_id: Optional[str] = None
    license_plate: Optional[str] = None
    model_name: str
    model_version: str
    is_demo: bool = True


class DetectionEventOut(BaseModel):
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)

    id: str
    event_type: str
    bus_id: Optional[str]
    camera_id: Optional[str]
    latitude: float
    longitude: float
    timestamp: datetime
    confidence: float
    severity: Severity
    image_path: Optional[str]
    video_path: Optional[str]
    vehicle_id: Optional[str]
    license_plate: Optional[str]
    model_name: str
    model_version: str
    is_demo: bool
    status: EventStatus


class EventStatusUpdate(BaseModel):
    status: EventStatus

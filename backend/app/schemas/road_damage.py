from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.database.models import EventStatus, Severity


class RoadDefectCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    defect_type: str  # pothole | cracked_road | damaged_asphalt | road_depression | debris
    severity: Severity = Severity.LOW
    confidence: float
    latitude: float
    longitude: float
    detected_at: Optional[datetime] = None
    bus_id: Optional[str] = None
    camera_id: Optional[str] = None
    image: Optional[str] = None
    model_name: str = "road_damage"
    model_version: Optional[str] = None
    is_demo: bool = True


class RoadDefectOut(BaseModel):
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)

    id: str
    defect_type: str
    severity: Severity
    confidence: float
    latitude: float
    longitude: float
    detected_at: datetime
    bus_id: Optional[str]
    camera_id: Optional[str]
    image: Optional[str]
    model_name: str
    model_version: Optional[str]
    is_demo: bool
    status: EventStatus


class RoadDefectStatusUpdate(BaseModel):
    status: EventStatus

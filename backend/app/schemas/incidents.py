from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.database.models import EventStatus, IncidentType, Severity


class IncidentCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    incident_type: IncidentType
    severity: Severity = Severity.MEDIUM
    vehicle_number: Optional[str] = None
    confidence: Optional[float] = None
    latitude: float
    longitude: float
    timestamp: Optional[datetime] = None
    evidence_image: Optional[str] = None
    evidence_video: Optional[str] = None
    bus_id: Optional[str] = None
    camera_id: Optional[str] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    is_demo: bool = True


class IncidentOut(BaseModel):
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)

    id: str
    incident_type: IncidentType
    severity: Severity
    vehicle_number: Optional[str]
    confidence: Optional[float]
    latitude: float
    longitude: float
    timestamp: datetime
    evidence_image: Optional[str]
    evidence_video: Optional[str]
    bus_id: Optional[str]
    camera_id: Optional[str]
    model_name: Optional[str]
    model_version: Optional[str]
    is_demo: bool
    assigned_officer_id: Optional[str]
    status: EventStatus



class IncidentUpdate(BaseModel):
    status: Optional[EventStatus] = None
    assigned_officer_id: Optional[str] = None

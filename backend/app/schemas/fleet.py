from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.database.models import BusStatus, CameraStatus, CameraType


class CameraCreate(BaseModel):
    camera_type: CameraType


class CameraOut(BaseModel):
    id: str
    bus_id: str
    camera_type: CameraType
    status: CameraStatus

    class Config:
        from_attributes = True


class BusCreate(BaseModel):
    bus_number: str
    registration_number: str
    route: Optional[str] = None
    is_simulated: bool = True


class BusUpdatePosition(BaseModel):
    latitude: float
    longitude: float
    speed_kmph: float = 0.0
    heading_deg: float = 0.0
    status: Optional[BusStatus] = None


class BusOut(BaseModel):
    id: str
    bus_number: str
    registration_number: str
    route: Optional[str]
    status: BusStatus
    latitude: Optional[float]
    longitude: Optional[float]
    speed_kmph: float
    heading_deg: float
    last_seen: Optional[datetime]
    is_simulated: bool
    cameras: list[CameraOut] = []

    class Config:
        from_attributes = True

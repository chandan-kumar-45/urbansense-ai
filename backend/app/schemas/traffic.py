from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TrafficEventCreate(BaseModel):
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    vehicle_count: int = 0
    density: float = 0.0
    congestion_level: str = "LOW"  # LOW | MEDIUM | HIGH
    average_speed_kmph: Optional[float] = None
    timestamp: Optional[datetime] = None
    is_demo: bool = True


class TrafficEventOut(BaseModel):
    id: str
    location: str
    latitude: Optional[float]
    longitude: Optional[float]
    vehicle_count: int
    density: float
    congestion_level: str
    average_speed_kmph: Optional[float]
    timestamp: datetime
    is_demo: bool

    class Config:
        from_attributes = True

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.models import TrafficEvent, User
from app.database.session import get_db
from app.schemas.traffic import TrafficEventCreate, TrafficEventOut
from app.websocket.manager import manager

router = APIRouter(prefix="/api/traffic", tags=["traffic"])


@router.get("", response_model=list[TrafficEventOut])
def list_traffic_events(
    congestion_level: str | None = None,
    location: str | None = None,
    limit: int = Query(default=200, le=2000),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(TrafficEvent)
    if congestion_level:
        q = q.filter(TrafficEvent.congestion_level == congestion_level)
    if location:
        q = q.filter(TrafficEvent.location == location)
    return q.order_by(TrafficEvent.timestamp.desc()).offset(offset).limit(limit).all()


@router.post("", response_model=TrafficEventOut, status_code=201)
async def create_traffic_event(payload: TrafficEventCreate, db: Session = Depends(get_db)):
    """Posted by the traffic-detection AI adapter or the fleet simulator."""
    data = payload.model_dump()
    if data.get("timestamp") is None:
        data.pop("timestamp")
    event = TrafficEvent(**data)
    db.add(event)
    db.commit()
    db.refresh(event)

    out = TrafficEventOut.model_validate(event)
    await manager.broadcast("traffic_event", out.model_dump())
    return event

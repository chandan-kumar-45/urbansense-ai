from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.models import DetectionEvent, User
from app.database.session import get_db
from app.schemas.events import DetectionEventCreate, DetectionEventOut, EventStatusUpdate
from app.websocket.manager import manager

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=list[DetectionEventOut])
def list_events(
    event_type: str | None = None,
    bus_id: str | None = None,
    severity: str | None = None,
    limit: int = Query(default=100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(DetectionEvent)
    if event_type:
        q = q.filter(DetectionEvent.event_type == event_type)
    if bus_id:
        q = q.filter(DetectionEvent.bus_id == bus_id)
    if severity:
        q = q.filter(DetectionEvent.severity == severity)
    return (
        q.order_by(DetectionEvent.timestamp.desc()).offset(offset).limit(limit).all()
    )


@router.get("/{event_id}", response_model=DetectionEventOut)
def get_event(event_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event = db.query(DetectionEvent).filter(DetectionEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    return event


@router.post("", response_model=DetectionEventOut, status_code=201)
async def create_event(payload: DetectionEventCreate, db: Session = Depends(get_db)):
    """
    This is the single ingestion point every AI adapter / the edge simulator posts
    to. No authentication is required from edge nodes in this prototype (they'd use
    a service API key in production — see docs/ARCHITECTURE.md limitations); the
    dashboard reads via the authenticated GET endpoints above.
    """
    data = payload.model_dump()
    if data.get("timestamp") is None:
        data.pop("timestamp")
    event = DetectionEvent(**data)
    db.add(event)
    db.commit()
    db.refresh(event)

    out = DetectionEventOut.model_validate(event)
    await manager.broadcast("detection_event", out.model_dump())
    return event


@router.patch("/{event_id}/status", response_model=DetectionEventOut)
def update_event_status(
    event_id: str,
    payload: EventStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(DetectionEvent).filter(DetectionEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    event.status = payload.status
    db.commit()
    db.refresh(event)
    return event

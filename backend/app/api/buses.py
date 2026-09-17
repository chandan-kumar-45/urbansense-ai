from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.database.models import Bus, User, UserRole
from app.database.session import get_db
from app.schemas.fleet import BusCreate, BusOut, BusUpdatePosition
from app.websocket.manager import manager

router = APIRouter(prefix="/api/buses", tags=["buses"])


@router.get("", response_model=list[BusOut])
def list_buses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Bus).all()


@router.get("/{bus_id}", response_model=BusOut)
def get_bus(bus_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found.")
    return bus


@router.post("", response_model=BusOut, status_code=201)
def create_bus(
    payload: BusCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.TRANSPORT_AUTHORITY)),
):
    if db.query(Bus).filter(Bus.registration_number == payload.registration_number).first():
        raise HTTPException(status_code=400, detail="Registration number already exists.")
    bus = Bus(**payload.model_dump())
    db.add(bus)
    db.commit()
    db.refresh(bus)
    return bus


async def _broadcast_position(bus: Bus) -> None:
    await manager.broadcast(
        "bus_position",
        {
            "id": bus.id,
            "bus_number": bus.bus_number,
            "latitude": bus.latitude,
            "longitude": bus.longitude,
            "speed_kmph": bus.speed_kmph,
            "heading_deg": bus.heading_deg,
            "status": bus.status.value if bus.status else None,
            "last_seen": bus.last_seen,
        },
    )


@router.patch("/{bus_id}/position", response_model=BusOut)
async def update_bus_position(
    bus_id: str, payload: BusUpdatePosition, db: Session = Depends(get_db)
):
    """
    Called by the edge simulator (or a real telematics feed) to push GPS updates.
    Broadcasts to connected dashboards over WebSocket so the Live Fleet map moves
    in real time.
    """
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found.")

    bus.latitude = payload.latitude
    bus.longitude = payload.longitude
    bus.speed_kmph = payload.speed_kmph
    bus.heading_deg = payload.heading_deg
    if payload.status:
        bus.status = payload.status
    bus.last_seen = datetime.utcnow()

    db.commit()
    db.refresh(bus)
    await _broadcast_position(bus)
    return bus

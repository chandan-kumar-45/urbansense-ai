from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.database.models import Incident, User, UserRole
from app.database.session import get_db
from app.schemas.incidents import IncidentCreate, IncidentOut, IncidentUpdate
from app.websocket.manager import manager

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentOut])
def list_incidents(
    incident_type: str | None = None,
    status_: str | None = Query(default=None, alias="status"),
    severity: str | None = None,
    limit: int = Query(default=200, le=2000),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN, UserRole.TRAFFIC_OFFICER, UserRole.TRANSPORT_AUTHORITY)
    ),
):
    q = db.query(Incident)
    if incident_type:
        q = q.filter(Incident.incident_type == incident_type)
    if status_:
        q = q.filter(Incident.status == status_)
    if severity:
        q = q.filter(Incident.severity == severity)
    return q.order_by(Incident.timestamp.desc()).offset(offset).limit(limit).all()


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN, UserRole.TRAFFIC_OFFICER, UserRole.TRANSPORT_AUTHORITY)
    ),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found.")
    return incident


@router.post("", response_model=IncidentOut, status_code=201)
async def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    """
    Posted by rash-driving / hit-and-run / pedestrian-risk adapters (or the
    simulator). Evidence fields (image/video paths) are stored as references;
    access to them is gated to authorized roles at read time (see
    docs/ARCHITECTURE.md §7 and the license-plate/evidence privacy notes).
    """
    data = payload.model_dump()
    if data.get("timestamp") is None:
        data.pop("timestamp")
    incident = Incident(**data)
    db.add(incident)
    db.commit()
    db.refresh(incident)

    out = IncidentOut.model_validate(incident)
    await manager.broadcast("incident", out.model_dump())
    return incident


@router.patch("/{incident_id}", response_model=IncidentOut)
def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN, UserRole.TRAFFIC_OFFICER, UserRole.TRANSPORT_AUTHORITY)
    ),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found.")
    if payload.status is not None:
        incident.status = payload.status
    if payload.assigned_officer_id is not None:
        incident.assigned_officer_id = payload.assigned_officer_id
    db.commit()
    db.refresh(incident)
    return incident

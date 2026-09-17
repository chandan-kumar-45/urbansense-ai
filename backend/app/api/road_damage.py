from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.database.models import RoadDefect, User, UserRole
from app.database.session import get_db
from app.schemas.road_damage import RoadDefectCreate, RoadDefectOut, RoadDefectStatusUpdate
from app.websocket.manager import manager

router = APIRouter(prefix="/api/road-damage", tags=["road-damage"])


@router.get("", response_model=list[RoadDefectOut])
def list_defects(
    defect_type: str | None = None,
    severity: str | None = None,
    bus_id: str | None = None,
    limit: int = Query(default=200, le=2000),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(RoadDefect)
    if defect_type:
        q = q.filter(RoadDefect.defect_type == defect_type)
    if severity:
        q = q.filter(RoadDefect.severity == severity)
    if bus_id:
        q = q.filter(RoadDefect.bus_id == bus_id)
    return q.order_by(RoadDefect.detected_at.desc()).offset(offset).limit(limit).all()


@router.get("/{defect_id}", response_model=RoadDefectOut)
def get_defect(defect_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    defect = db.query(RoadDefect).filter(RoadDefect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=404, detail="Road defect not found.")
    return defect


@router.post("", response_model=RoadDefectOut, status_code=201)
async def create_defect(payload: RoadDefectCreate, db: Session = Depends(get_db)):
    """
    Called by the road-damage AI adapter (backend/app/ai/road_damage/adapter.py)
    after it produces a detection — real or demo. `is_demo` is always carried
    through from the adapter's output; this endpoint never overrides it to True
    on its own, since that could hide a real detection as fake but could also
    silently launder a demo detection as real — both are unacceptable.
    """
    data = payload.model_dump()
    if data.get("detected_at") is None:
        data.pop("detected_at")
    defect = RoadDefect(**data)
    db.add(defect)
    db.commit()
    db.refresh(defect)

    out = RoadDefectOut.model_validate(defect)
    await manager.broadcast("road_defect", out.model_dump())
    return defect


@router.patch("/{defect_id}/status", response_model=RoadDefectOut)
def update_defect_status(
    defect_id: str,
    payload: RoadDefectStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN, UserRole.MAINTENANCE_OFFICER)
    ),
):
    defect = db.query(RoadDefect).filter(RoadDefect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=404, detail="Road defect not found.")
    defect.status = payload.status
    db.commit()
    db.refresh(defect)
    return defect

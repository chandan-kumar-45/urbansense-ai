from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.database.models import Bus, Camera, User, UserRole
from app.database.session import get_db
from app.schemas.fleet import CameraCreate, CameraOut
from app.services.capture import capture_and_detect
from app.schemas.road_damage import RoadDefectOut

router = APIRouter(prefix="/api/buses/{bus_id}/cameras", tags=["cameras"])


@router.get("", response_model=list[CameraOut])
def list_cameras(
    bus_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found.")
    return db.query(Camera).filter(Camera.bus_id == bus_id).all()


@router.post("", response_model=CameraOut, status_code=201)
def add_camera(
    bus_id: str,
    payload: CameraCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.TRANSPORT_AUTHORITY)),
):
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found.")
    camera = Camera(bus_id=bus_id, camera_type=payload.camera_type)
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


@router.post("/{camera_id}/capture", response_model=list[RoadDefectOut])
async def trigger_camera_capture(
    bus_id: str,
    camera_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN, UserRole.TRANSPORT_AUTHORITY, UserRole.MAINTENANCE_OFFICER)
    ),
):
    """
    Manually trigger one capture-and-detect cycle for a single camera —
    useful for a live demo ("watch this exact camera detect something") and
    for testing a newly-activated model version against one camera at a
    time, outside the full fleet simulation. Runs through the exact same
    app/services/capture.py pipeline the simulation engine uses.
    """
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found.")
    camera = db.query(Camera).filter(Camera.id == camera_id, Camera.bus_id == bus_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found on this bus.")

    return await capture_and_detect(db, bus, camera)

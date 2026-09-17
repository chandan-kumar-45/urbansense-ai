from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.models import User
from app.database.session import get_db
from app.services.analytics import (
    compute_congestion_summary,
    compute_road_health_by_route,
    compute_route_delays,
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/congestion")
def congestion(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return compute_congestion_summary(db)


@router.get("/routes")
def routes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return compute_route_delays(db)


@router.get("/road-health")
def road_health(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return compute_road_health_by_route(db)


@router.get("/origin-destination")
def origin_destination(current_user: User = Depends(get_current_user)):
    """
    Prototype stub: real origin-destination analysis needs ticketing/GPS trip
    data we don't have in this demo. Returns a clearly-labeled simulated
    dataset shaped the way the real thing would be, so the frontend chart
    component doesn't need to change once real trip data exists.
    """
    return {
        "is_demo": True,
        "note": "Simulated O-D data — no real ticketing/trip dataset connected in this prototype.",
        "zones": [
            {"zone": "City Center", "originating_trips": 420, "destination_trips": 510},
            {"zone": "Railway Station", "originating_trips": 380, "destination_trips": 340},
            {"zone": "Industrial Area", "originating_trips": 260, "destination_trips": 190},
            {"zone": "University", "originating_trips": 300, "destination_trips": 275},
        ],
        "peak_hours": ["08:00-10:00", "17:30-19:30"],
    }

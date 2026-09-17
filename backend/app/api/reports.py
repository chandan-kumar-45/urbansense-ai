import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.models import Bus, Incident, RoadDefect, TrafficEvent, User
from app.database.session import get_db

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _csv_response(rows: list[dict], filename: str) -> StreamingResponse:
    buf = io.StringIO()
    if rows:
        writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/road-damage")
def road_damage_report(
    format: str = Query(default="json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    defects = db.query(RoadDefect).order_by(RoadDefect.detected_at.desc()).all()
    rows = [
        {
            "id": d.id,
            "defect_type": d.defect_type,
            "severity": d.severity.value,
            "confidence": d.confidence,
            "latitude": d.latitude,
            "longitude": d.longitude,
            "detected_at": d.detected_at.isoformat(),
            "bus_id": d.bus_id,
            "is_demo": d.is_demo,
            "status": d.status.value,
        }
        for d in defects
    ]
    if format == "csv":
        return _csv_response(rows, "road_damage_report.csv")

    by_type: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    for d in defects:
        by_type[d.defect_type] = by_type.get(d.defect_type, 0) + 1
        by_severity[d.severity.value] = by_severity.get(d.severity.value, 0) + 1

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "total_defects": len(defects),
        "by_type": by_type,
        "by_severity": by_severity,
        "rows": rows,
    }


@router.get("/traffic-congestion")
def traffic_report(
    format: str = Query(default="json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    events = db.query(TrafficEvent).order_by(TrafficEvent.timestamp.desc()).all()
    rows = [
        {
            "id": e.id,
            "location": e.location,
            "vehicle_count": e.vehicle_count,
            "density": e.density,
            "congestion_level": e.congestion_level,
            "average_speed_kmph": e.average_speed_kmph,
            "timestamp": e.timestamp.isoformat(),
            "is_demo": e.is_demo,
        }
        for e in events
    ]
    if format == "csv":
        return _csv_response(rows, "traffic_congestion_report.csv")
    return {"generated_at": datetime.utcnow().isoformat(), "total_samples": len(events), "rows": rows}


@router.get("/incidents")
def incidents_report(
    format: str = Query(default="json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incidents = db.query(Incident).order_by(Incident.timestamp.desc()).all()
    rows = [
        {
            "id": i.id,
            "incident_type": i.incident_type.value,
            "severity": i.severity.value,
            "vehicle_number": i.vehicle_number,
            "confidence": i.confidence,
            "latitude": i.latitude,
            "longitude": i.longitude,
            "timestamp": i.timestamp.isoformat(),
            "is_demo": i.is_demo,
            "status": i.status.value,
        }
        for i in incidents
    ]
    if format == "csv":
        return _csv_response(rows, "incidents_report.csv")

    by_type: dict[str, int] = {}
    for i in incidents:
        by_type[i.incident_type.value] = by_type.get(i.incident_type.value, 0) + 1
    return {
        "generated_at": datetime.utcnow().isoformat(),
        "total_incidents": len(incidents),
        "by_type": by_type,
        "rows": rows,
    }


@router.get("/fleet")
def fleet_report(
    format: str = Query(default="json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    buses = db.query(Bus).all()
    rows = [
        {
            "id": b.id,
            "bus_number": b.bus_number,
            "route": b.route,
            "status": b.status.value,
            "speed_kmph": b.speed_kmph,
            "last_seen": b.last_seen.isoformat() if b.last_seen else None,
            "is_simulated": b.is_simulated,
        }
        for b in buses
    ]
    if format == "csv":
        return _csv_response(rows, "fleet_report.csv")
    return {"generated_at": datetime.utcnow().isoformat(), "total_buses": len(buses), "rows": rows}


@router.get("/infrastructure")
def infrastructure_report(
    format: str = Query(default="json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    defects = (
        db.query(RoadDefect)
        .filter(RoadDefect.defect_type != "pothole")
        .order_by(RoadDefect.detected_at.desc())
        .all()
    )
    rows = [
        {
            "id": d.id,
            "defect_type": d.defect_type,
            "severity": d.severity.value,
            "latitude": d.latitude,
            "longitude": d.longitude,
            "detected_at": d.detected_at.isoformat(),
            "status": d.status.value,
        }
        for d in defects
    ]
    if format == "csv":
        return _csv_response(rows, "infrastructure_report.csv")
    return {
        "generated_at": datetime.utcnow().isoformat(),
        "total_issues": len(defects),
        "rows": rows,
    }

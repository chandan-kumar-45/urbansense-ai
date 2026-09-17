"""
Analytics computed directly from stored events — no separate analytics
database or offline job in this prototype. Road Health Score and route delay
are explicitly documented as conceptual/analytical scores, not official
government road ratings, per the SIH problem statement's instructions.
"""
from __future__ import annotations

from collections import defaultdict

from sqlalchemy.orm import Session

from app.database.models import RoadDefect, TrafficEvent

SEVERITY_WEIGHT = {"LOW": 1, "MEDIUM": 2, "HIGH": 4, "CRITICAL": 7}

# Illustrative scheduled durations per route, used only to compute a delay
# comparison against simulated/observed average speed. Real deployments would
# source this from an actual GTFS schedule.
SCHEDULED_MINUTES = {"Route 12": 42, "Route 7": 35}
ROUTE_DISTANCE_KM = {"Route 12": 14, "Route 7": 11}


def compute_road_health_by_route(db: Session) -> list[dict]:
    defects = db.query(RoadDefect).all()
    by_route: dict[str, list[RoadDefect]] = defaultdict(list)
    for d in defects:
        route = d.bus.route if d.bus else "Unassigned"
        by_route[route].append(d)

    results = []
    for route, items in by_route.items():
        penalty = sum(SEVERITY_WEIGHT.get(d.severity.value, 1) for d in items)
        score = max(0, 100 - min(penalty * 2, 100))
        results.append(
            {
                "route": route,
                "defect_count": len(items),
                "road_health_score": score,
                "is_analytical_score": True,
                "note": "Analytical score derived from defect count/severity — not an official road rating.",
            }
        )
    return results


def compute_route_delays(db: Session) -> list[dict]:
    traffic = db.query(TrafficEvent).all()
    by_route: dict[str, list[TrafficEvent]] = defaultdict(list)
    for t in traffic:
        by_route[t.location].append(t)

    results = []
    for route, scheduled_min in SCHEDULED_MINUTES.items():
        events = by_route.get(route, [])
        if events:
            avg_speed = sum(e.average_speed_kmph or 0 for e in events) / len(events)
        else:
            avg_speed = 0
        distance = ROUTE_DISTANCE_KM.get(route, 12)
        current_min = round((distance / avg_speed) * 60, 1) if avg_speed > 0 else scheduled_min
        results.append(
            {
                "route": route,
                "scheduled_minutes": scheduled_min,
                "current_estimated_minutes": current_min,
                "delay_minutes": round(current_min - scheduled_min, 1),
                "average_speed_kmph": round(avg_speed, 1) if avg_speed else None,
                "sample_size": len(events),
                "is_demo": len(events) == 0,
            }
        )
    return results


def compute_congestion_summary(db: Session) -> dict:
    events = db.query(TrafficEvent).all()
    if not events:
        return {"low": 0, "medium": 0, "high": 0, "total_samples": 0, "is_demo": True}
    counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for e in events:
        counts[e.congestion_level] = counts.get(e.congestion_level, 0) + 1
    return {
        "low": counts["LOW"],
        "medium": counts["MEDIUM"],
        "high": counts["HIGH"],
        "total_samples": len(events),
        "is_demo": any(e.is_demo for e in events),
    }

from __future__ import annotations

from app.ai.registry.base import Detection
from app.ai.road_damage.config import MIN_CONFIDENCE, SEVERITY_BY_CONFIDENCE


def assign_severity(confidence: float) -> str:
    for threshold, label in SEVERITY_BY_CONFIDENCE:
        if confidence >= threshold:
            return label
    return "LOW"


def filter_and_finalize(detections: list[Detection]) -> list[Detection]:
    """Drop low-confidence detections, ensure every detection has a severity set."""
    out: list[Detection] = []
    for d in detections:
        if d.confidence < MIN_CONFIDENCE:
            continue
        if not d.severity or d.severity == "LOW" and d.confidence >= SEVERITY_BY_CONFIDENCE[1][0]:
            d.severity = assign_severity(d.confidence)
        out.append(d)
    return out

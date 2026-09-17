"""
The real "camera → AI model → detection" pipeline for a single bus camera.

This is deliberately separate from app/services/simulation.py's traffic/
incident generation (which has no underlying AI model yet, so it stays
labeled as pure simulation). Road damage DOES have a real, working detector
(DemoRoadDamageDetector — a classical CV heuristic, or a real trained model
once registered/activated), so every road-defect event should be produced by
actually running that model through the registry — not fabricated directly.

Because there is no live camera feed in this prototype, `capture_frame()`
generates a synthetic frame standing in for "what this camera currently
sees." This is clearly documented: the CAPTURE is synthetic, but the
DETECTION is real — whatever model is currently ACTIVE for "road_damage"
actually runs on that frame, exactly as it would on a real photo uploaded
through the AI Detection Lab. Swap `capture_frame()` for a real camera/RTSP
read and nothing else in this pipeline needs to change.
"""
from __future__ import annotations

import random

import cv2
import numpy as np
from sqlalchemy.orm import Session

from app.ai.registry.registry import registry
from app.database.models import Bus, Camera, RoadDefect
from app.websocket.manager import manager


def capture_frame(camera: Camera) -> np.ndarray:
    """
    Stand-in for a real camera/RTSP frame grab. Produces a plausible road
    surface with an occasional dark, irregular patch — roughly half the time
    a genuine "pothole-like" region for the heuristic to find, roughly half
    the time a clean road (so not every capture produces a false detection,
    which would be dishonest in the other direction).
    """
    frame = np.full((240, 320, 3), random.randint(150, 200), dtype=np.uint8)
    noise = np.random.randint(-15, 15, frame.shape, dtype=np.int16)
    frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    if random.random() < 0.5:
        cx, cy = random.randint(60, 260), random.randint(60, 180)
        w, h = random.randint(20, 55), random.randint(15, 40)
        angle = random.randint(0, 180)
        shade = random.randint(20, 70)
        cv2.ellipse(frame, (cx, cy), (w, h), angle, 0, 360, (shade, shade, shade), -1)

    return frame


async def capture_and_detect(db: Session, bus: Bus, camera: Camera) -> list[RoadDefect]:
    """
    Runs one capture-and-detect cycle for a single camera. Returns the
    RoadDefect rows created (empty list if the active model found nothing —
    which is the honest, expected outcome most of the time).
    """
    frame = capture_frame(camera)

    try:
        model = registry.get_active_model(db, "road_damage")
    except LookupError:
        return []  # no active model registered — nothing to run

    try:
        raw = model.predict(frame)
        detections = model.postprocess(raw)
    except NotImplementedError:
        # Active version is registered but not yet implemented (e.g. the
        # teammate's trained model before load()/predict() are filled in).
        # Fail silently for this capture cycle rather than crashing the sim.
        return []

    created: list[RoadDefect] = []
    for d in detections:
        defect = RoadDefect(
            defect_type=d.cls,
            severity=d.severity,
            confidence=d.confidence,
            latitude=(bus.latitude or 0) + random.uniform(-0.0006, 0.0006),
            longitude=(bus.longitude or 0) + random.uniform(-0.0006, 0.0006),
            bus_id=bus.id,
            camera_id=camera.id,
            model_name="road_damage",
            model_version=model.version,
            is_demo=model.is_demo,
        )
        db.add(defect)
        db.commit()
        db.refresh(defect)
        created.append(defect)

        await manager.broadcast(
            "road_defect",
            {
                "id": defect.id,
                "defect_type": defect.defect_type,
                "severity": defect.severity.value,
                "confidence": defect.confidence,
                "latitude": defect.latitude,
                "longitude": defect.longitude,
                "detected_at": defect.detected_at,
                "bus_id": defect.bus_id,
                "camera_id": defect.camera_id,
                "model_name": defect.model_name,
                "model_version": defect.model_version,
                "is_demo": defect.is_demo,
                "status": defect.status.value,
            },
        )

    return created

import tempfile
import time
from pathlib import Path

import cv2
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.ai.registry.registry import registry
from app.ai.road_damage.config import SAMPLE_FPS
from app.api.deps import get_current_user
from app.core.config import settings
from app.database.models import User
from app.database.session import get_db

router = APIRouter(prefix="/api/video", tags=["video"])

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/webm"}
MAX_FRAMES_ANALYZED = 40  # hard cap so an SIH demo laptop doesn't hang on a long clip


@router.post("/analyze")
async def analyze_video(
    capability: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Samples frames at SAMPLE_FPS (see app/ai/road_damage/config.py — this is the
    same rate the edge simulator would use, which is what gives the bandwidth
    savings claimed in docs/ARCHITECTURE.md §6: we do not run inference on every
    single frame of the video). Runs the capability's ACTIVE model on each
    sampled frame and returns per-frame + aggregated detections.
    """
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: {sorted(ALLOWED_VIDEO_TYPES)}",
        )

    contents = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024 * 4  # allow larger for video
    if len(contents) > max_bytes:
        raise HTTPException(status_code=413, detail="Video file too large for this prototype.")

    try:
        model = registry.get_active_model(db, capability)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    suffix = Path(file.filename or "video.mp4").suffix or ".mp4"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
        tmp.write(contents)
        tmp.flush()

        cap = cv2.VideoCapture(tmp.name)
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="Could not decode video file.")

        source_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        frame_interval = max(1, round(source_fps / SAMPLE_FPS))

        frame_results = []
        frame_idx = 0
        start = time.perf_counter()

        while len(frame_results) < MAX_FRAMES_ANALYZED:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % frame_interval == 0:
                try:
                    raw = model.predict(frame)
                    detections = model.postprocess(raw)
                except NotImplementedError as exc:
                    cap.release()
                    raise HTTPException(
                        status_code=501,
                        detail=f"The active '{capability}' model is not yet implemented: {exc}",
                    )
                frame_results.append(
                    {
                        "frame_index": frame_idx,
                        "timestamp_s": round(frame_idx / source_fps, 2),
                        "detections": [
                            {
                                "class": d.cls,
                                "confidence": d.confidence,
                                "bbox": d.bbox,
                                "severity": d.severity,
                            }
                            for d in detections
                        ],
                    }
                )
            frame_idx += 1

        cap.release()

    elapsed_ms = (time.perf_counter() - start) * 1000
    total_detections = sum(len(f["detections"]) for f in frame_results)

    return {
        "model": capability,
        "model_version": model.version,
        "is_demo": model.is_demo,
        "source_fps": round(source_fps, 2),
        "sampled_fps": SAMPLE_FPS,
        "frames_analyzed": len(frame_results),
        "frames_capped_at": MAX_FRAMES_ANALYZED,
        "total_processing_time_ms": round(elapsed_ms, 2),
        "total_detections": total_detections,
        "frames": frame_results,
    }

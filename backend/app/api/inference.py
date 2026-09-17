import time

import cv2
import numpy as np
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.ai.registry.registry import registry
from app.api.deps import get_current_user
from app.core.config import settings
from app.database.models import User
from app.database.session import get_db

router = APIRouter(prefix="/api/inference", tags=["inference"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("")
async def run_inference(
    capability: str = Form(..., description='e.g. "road_damage"'),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    The single entry point the AI Detection Lab (Phase 7) calls, and the one you
    can curl directly to sanity-check any registered model. Looks up whichever
    ModelVersion is ACTIVE for `capability` via the registry, runs it on the
    uploaded image, and returns the standardized detection contract
    (docs/ARCHITECTURE.md §2) — including `is_demo` and `model_version` so the
    caller always knows exactly what produced the result.
    """
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: {sorted(ALLOWED_IMAGE_TYPES)}",
        )

    contents = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_upload_size_mb}MB limit.")

    np_arr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="Could not decode image file.")

    try:
        model = registry.get_active_model(db, capability)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    start = time.perf_counter()
    try:
        raw = model.predict(frame)
        detections = model.postprocess(raw)
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=501,
            detail=f"The active '{capability}' model version is registered but not "
            f"yet implemented: {exc}",
        )
    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "model": capability,
        "model_version": model.version,
        "is_demo": model.is_demo,
        "processing_time_ms": round(elapsed_ms, 2),
        "detections": [
            {
                "class": d.cls,
                "confidence": d.confidence,
                "bbox": d.bbox,
                "severity": d.severity,
                **({"extra": d.extra} if d.extra else {}),
            }
            for d in detections
        ],
    }

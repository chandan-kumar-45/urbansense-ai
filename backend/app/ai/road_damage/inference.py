"""
Two detector implementations for the "road_damage" capability:

1. DemoRoadDamageDetector — a classical computer-vision heuristic (no neural
   network, no training data). It looks for dark, irregular blobs against the
   road surface using adaptive thresholding + contour analysis, which is a
   genuine (if crude) image-processing technique — not a random number
   generator pretending to be AI. It is always reported with `is_demo=True`
   and `framework="opencv-heuristic"` so nobody can mistake it for a trained
   model's output.

2. TeammateRoadDamageModel — the swap-in point for your teammate's actual
   trained model once `manvendrasrathore11/ai-urban-intelligence` has real
   weights + inference code in `src/road_damage/{model,detector}.py`. Until
   then this raises NotImplementedError with a clear message rather than
   silently falling back to the demo detector — silently falling back would
   be exactly the kind of dishonesty the project rules forbid.
"""
from __future__ import annotations

import cv2
import numpy as np

from app.ai.registry.base import BaseDetectionModel, Detection
from app.ai.road_damage.config import DEMO_MODEL_VERSION, SUPPORTED_CLASSES
from app.ai.road_damage.postprocessing import filter_and_finalize
from app.ai.road_damage.preprocessing import resize_keep_aspect, to_grayscale


class DemoRoadDamageDetector(BaseDetectionModel):
    capability = "road_damage"
    version = DEMO_MODEL_VERSION
    is_demo = True

    def load(self) -> None:
        # No weights to load — this is a deterministic classical-CV heuristic.
        self._loaded = True

    def predict(self, frame: np.ndarray) -> list[Detection]:
        frame = resize_keep_aspect(frame)
        gray = to_grayscale(frame)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)

        # Potholes/damaged patches tend to be locally darker than surrounding
        # road surface — adaptive thresholding highlights those regions
        # regardless of overall lighting.
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 8
        )
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        frame_area = frame.shape[0] * frame.shape[1]
        detections: list[Detection] = []

        for c in contours:
            area = cv2.contourArea(c)
            # Ignore tiny noise specks and implausibly huge regions (e.g. shadows
            # covering most of the frame).
            if area < frame_area * 0.002 or area > frame_area * 0.25:
                continue

            x, y, w, h = cv2.boundingRect(c)
            aspect = w / float(h) if h else 0
            perimeter = cv2.arcLength(c, True)
            circularity = (4 * np.pi * area / (perimeter**2)) if perimeter > 0 else 0

            # Heuristic confidence: irregular (non-circular), moderately-sized,
            # roughly road-proportioned blobs score higher. This is intentionally
            # simple and documented as such — it is NOT a calibrated probability
            # from a trained classifier.
            size_score = min(area / (frame_area * 0.06), 1.0)
            shape_score = 1.0 - min(circularity, 1.0)  # more irregular -> higher
            aspect_score = 1.0 if 0.4 <= aspect <= 2.5 else 0.5
            confidence = float(np.clip(0.3 + 0.4 * size_score + 0.3 * shape_score, 0.0, 0.97) * aspect_score)

            cls = "pothole" if circularity > 0.35 else "cracked_road"

            detections.append(
                Detection(
                    cls=cls,
                    confidence=round(confidence, 3),
                    bbox=[float(x), float(y), float(x + w), float(y + h)],
                    extra={"heuristic": "adaptive_threshold_contour", "area_px": float(area)},
                )
            )

        return detections

    def postprocess(self, raw_detections: list[Detection]) -> list[Detection]:
        return filter_and_finalize(raw_detections)

    def get_metadata(self) -> dict:
        return {
            "name": "road_damage",
            "version": self.version,
            "type": "classical-cv-heuristic",
            "supported_classes": SUPPORTED_CLASSES,
            "framework": "opencv-heuristic",
            "is_demo": True,
            "notes": (
                "Demo detector using adaptive-threshold contour analysis. "
                "Not a trained neural network. Replace with TeammateRoadDamageModel "
                "once real weights exist — see docs/AI_MODEL_INTEGRATION.md."
            ),
        }


class TeammateRoadDamageModel(BaseDetectionModel):
    """
    Swap-in point for the real trained model from
    github.com/manvendrasrathore11/ai-urban-intelligence.

    Expected integration once that repo has real content (per its own README's
    "Next Steps"):
        from teammate_road_damage.src.road_damage.model import load_model
        from teammate_road_damage.src.road_damage.detector import run_inference

    Until then, this class exists so the registry/API/frontend contract is
    already in place — activating a ModelVersion row pointing at this class
    before it's implemented will fail loudly (NotImplementedError), not
    silently serve fake results.
    """

    capability = "road_damage"
    is_demo = False

    def __init__(self, model_version_row) -> None:
        self.version = model_version_row.version

    def load(self) -> None:
        raise NotImplementedError(
            "TeammateRoadDamageModel.load() is not implemented yet — the "
            "teammate repo does not contain trained weights/inference code. "
            "See docs/AI_MODEL_INTEGRATION.md for the integration steps."
        )

    def predict(self, frame: np.ndarray) -> list[Detection]:
        raise NotImplementedError

    def postprocess(self, raw_detections: list[Detection]) -> list[Detection]:
        raise NotImplementedError

    def get_metadata(self) -> dict:
        return {
            "name": "road_damage",
            "version": self.version,
            "type": "pending-integration",
            "supported_classes": SUPPORTED_CLASSES,
            "framework": "unknown",
            "is_demo": False,
            "notes": "Not yet implemented — placeholder for the teammate's trained model.",
        }

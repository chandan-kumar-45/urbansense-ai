"""
The contract every AI capability (road_damage, traffic, pedestrian, traffic_sign,
waterlogging, license_plate, rash_driving) must implement. The rest of the platform
(events API, dashboard, GIS) only ever talks to this interface — never to a specific
model's internals. This is what makes "swap in a real trained model later" a one-file
change instead of a rewrite. See docs/ARCHITECTURE.md §2 and §4.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class Detection:
    cls: str
    confidence: float
    bbox: list[float]  # [x1, y1, x2, y2] in pixel coords of the input frame
    severity: str = "LOW"
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class InferenceResult:
    model: str
    model_version: str
    is_demo: bool
    processing_time_ms: float
    detections: list[Detection]

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "model_version": self.model_version,
            "is_demo": self.is_demo,
            "processing_time_ms": round(self.processing_time_ms, 2),
            "detections": [
                {
                    "class": d.cls,
                    "confidence": round(d.confidence, 4),
                    "bbox": d.bbox,
                    "severity": d.severity,
                    **({"extra": d.extra} if d.extra else {}),
                }
                for d in self.detections
            ],
        }


class BaseDetectionModel(ABC):
    """
    Every adapter (real or demo) implements this four-method interface, as
    required by the problem statement's model-plug-in architecture.
    """

    capability: str = "unknown"
    version: str = "0.0.0"
    is_demo: bool = True

    @abstractmethod
    def load(self) -> None:
        """Load weights / initialize the underlying detector. Called once by the registry."""

    @abstractmethod
    def predict(self, frame: np.ndarray) -> list[Detection]:
        """Run inference on a single BGR frame (as returned by cv2.imread/VideoCapture)."""

    @abstractmethod
    def postprocess(self, raw_detections: list[Detection]) -> list[Detection]:
        """Filter/threshold/assign severity. Given raw detections, return the final list."""

    @abstractmethod
    def get_metadata(self) -> dict:
        """Returns {name, version, type, supported_classes, framework, is_demo, ...}."""

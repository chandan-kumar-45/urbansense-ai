"""Preprocessing shared by both the demo heuristic detector and (later) a real
trained model — resize/normalize should stay identical across both so results
are comparable when you A/B test a new model version."""
from __future__ import annotations

import cv2
import numpy as np

TARGET_WIDTH = 640


def resize_keep_aspect(frame: np.ndarray, target_width: int = TARGET_WIDTH) -> np.ndarray:
    h, w = frame.shape[:2]
    if w == target_width:
        return frame
    scale = target_width / float(w)
    new_size = (target_width, int(h * scale))
    return cv2.resize(frame, new_size, interpolation=cv2.INTER_AREA)


def to_grayscale(frame: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

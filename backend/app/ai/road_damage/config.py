"""
Configuration for the road-damage capability. Mirrors the config responsibility
that the teammate repo's (currently empty) `src/road_damage/config.py` is meant to
hold — once that file has real content, values here should be sourced from there
instead of being duplicated. See docs/AI_MODEL_INTEGRATION.md.
"""

SUPPORTED_CLASSES = [
    "pothole",
    "cracked_road",
    "damaged_asphalt",
    "road_depression",
    "debris",
]

# Confidence below this is dropped entirely (postprocessing.py)
MIN_CONFIDENCE = 0.35

# Severity thresholds by confidence, used only when the detector itself doesn't
# already provide a severity (the demo heuristic estimates severity from the
# detected region's size instead — see inference.py)
SEVERITY_BY_CONFIDENCE = [
    (0.85, "CRITICAL"),
    (0.65, "HIGH"),
    (0.45, "MEDIUM"),
    (0.0, "LOW"),
]

# Frame sampling: how many frames per second of video the adapter analyzes.
# Kept low deliberately — this is what gives the edge bandwidth savings claimed
# in docs/ARCHITECTURE.md §6 (we don't run inference on every single frame).
SAMPLE_FPS = 2

DEMO_MODEL_VERSION = "1.0.0-demo"

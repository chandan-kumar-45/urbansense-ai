"""
Registers the road_damage capability with the AI Model Registry. Given a
ModelVersion DB row, decides which concrete detector class to instantiate:
- model_type == "classical-cv-heuristic" (or is_demo=True) -> DemoRoadDamageDetector
- anything else (a real trained model version) -> TeammateRoadDamageModel

This is the ONLY place that needs to change when the teammate's model is ready:
add a new model_type branch (e.g. "yolov8") pointing at a real implementation.
"""
from app.ai.registry.base import BaseDetectionModel
from app.ai.registry.registry import register_adapter_factory
from app.ai.road_damage.inference import DemoRoadDamageDetector, TeammateRoadDamageModel


def build_road_damage_adapter(model_version_row) -> BaseDetectionModel:
    if model_version_row.is_demo:
        return DemoRoadDamageDetector()
    return TeammateRoadDamageModel(model_version_row)


register_adapter_factory("road_damage", build_road_damage_adapter)

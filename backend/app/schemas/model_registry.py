from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.database.models import ModelStatus


class ModelVersionCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_name: str  # e.g. "road_damage"
    version: str  # e.g. "1.1.0"
    model_type: str  # e.g. "classical-cv-heuristic", "yolov8", "onnx"
    supported_classes: list[str] = []
    framework: Optional[str] = None  # pytorch / onnx / tensorrt / opencv-heuristic / none
    accuracy_metrics: dict = {}
    is_demo: bool = True


class ModelVersionOut(BaseModel):
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)

    id: str
    model_name: str
    version: str
    model_type: str
    supported_classes: list[str]
    framework: Optional[str]
    accuracy_metrics: dict
    is_demo: bool
    status: ModelStatus
    created_at: datetime


"""
The AI Model Registry. This is the piece that makes model updates possible without
touching the frontend or backend business logic: it looks up which *version* of a
capability (e.g. "road_damage") is currently ACTIVE in the database, and hands back
a loaded adapter instance for it.

Adding a brand-new model version later is:
  1. Implement/point to the new weights.
  2. POST /api/models/register (writes a ModelVersion row, status=TESTING).
  3. POST /api/models/{id}/activate (flips status=ACTIVE, deactivates the old one).
No redeploy of the API or the UI is required.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.ai.registry.base import BaseDetectionModel
from app.database.models import ModelStatus, ModelVersion

# Factory: capability name -> adapter class. Each adapter class knows how to
# instantiate itself for a given ModelVersion row (e.g. which weights file to load).
_ADAPTER_FACTORIES: dict[str, type] = {}


def register_adapter_factory(capability: str, adapter_cls: type) -> None:
    _ADAPTER_FACTORIES[capability] = adapter_cls


class ModelRegistry:
    def __init__(self) -> None:
        self._loaded_cache: dict[str, BaseDetectionModel] = {}

    def get_active_model(self, db: Session, capability: str) -> BaseDetectionModel:
        """Returns a loaded adapter for whichever version is ACTIVE for `capability`.
        Caches the loaded instance per (capability, version) so we don't reload
        weights on every request; the cache key changes automatically when a
        different version is activated."""
        version_row = (
            db.query(ModelVersion)
            .filter(ModelVersion.model_name == capability, ModelVersion.status == ModelStatus.ACTIVE)
            .order_by(ModelVersion.created_at.desc())
            .first()
        )

        if version_row is None:
            raise LookupError(
                f"No ACTIVE model version registered for capability '{capability}'. "
                f"Use POST /api/models/register then /api/models/{{id}}/activate."
            )

        cache_key = f"{capability}:{version_row.version}"
        if cache_key in self._loaded_cache:
            return self._loaded_cache[cache_key]

        adapter_cls = _ADAPTER_FACTORIES.get(capability)
        if adapter_cls is None:
            raise LookupError(f"No adapter factory registered for capability '{capability}'.")

        adapter: BaseDetectionModel = adapter_cls(version_row)
        adapter.load()
        self._loaded_cache[cache_key] = adapter
        return adapter

    def invalidate(self, capability: str) -> None:
        """Call this after activating a different version so the next request
        loads the newly-active one instead of a stale cached instance."""
        self._loaded_cache = {
            k: v for k, v in self._loaded_cache.items() if not k.startswith(f"{capability}:")
        }


registry = ModelRegistry()

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.registry.registry import registry
from app.api.deps import get_current_user, require_role
from app.database.models import ModelStatus, ModelVersion, User, UserRole
from app.database.session import get_db
from app.schemas.model_registry import ModelVersionCreate, ModelVersionOut

router = APIRouter(prefix="/api/models", tags=["model-registry"])


def _to_out(row: ModelVersion) -> ModelVersionOut:
    return ModelVersionOut(
        id=row.id,
        model_name=row.model_name,
        version=row.version,
        model_type=row.model_type,
        supported_classes=json.loads(row.supported_classes or "[]"),
        framework=row.framework,
        accuracy_metrics=json.loads(row.accuracy_metrics or "{}"),
        is_demo=row.is_demo,
        status=row.status,
        created_at=row.created_at,
    )


@router.get("", response_model=list[ModelVersionOut])
def list_models(
    model_name: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(ModelVersion)
    if model_name:
        q = q.filter(ModelVersion.model_name == model_name)
    rows = q.order_by(ModelVersion.model_name, ModelVersion.created_at.desc()).all()
    return [_to_out(r) for r in rows]


@router.get("/{model_id}", response_model=ModelVersionOut)
def get_model(model_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(ModelVersion).filter(ModelVersion.id == model_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Model version not found.")
    return _to_out(row)


@router.post("/register", response_model=ModelVersionOut, status_code=201)
def register_model(
    payload: ModelVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """New versions always start as TESTING — they must be explicitly activated
    via /api/models/{id}/activate before they serve live traffic. This prevents
    an unvetted model from silently going live."""
    row = ModelVersion(
        model_name=payload.model_name,
        version=payload.version,
        model_type=payload.model_type,
        supported_classes=json.dumps(payload.supported_classes),
        framework=payload.framework,
        accuracy_metrics=json.dumps(payload.accuracy_metrics),
        is_demo=payload.is_demo,
        status=ModelStatus.TESTING,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_out(row)


@router.post("/{model_id}/activate", response_model=ModelVersionOut)
def activate_model(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    row = db.query(ModelVersion).filter(ModelVersion.id == model_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Model version not found.")

    # Deactivate any other ACTIVE version for the same capability.
    others = (
        db.query(ModelVersion)
        .filter(
            ModelVersion.model_name == row.model_name,
            ModelVersion.status == ModelStatus.ACTIVE,
            ModelVersion.id != row.id,
        )
        .all()
    )
    for o in others:
        o.status = ModelStatus.INACTIVE

    row.status = ModelStatus.ACTIVE
    db.commit()
    db.refresh(row)

    registry.invalidate(row.model_name)
    return _to_out(row)

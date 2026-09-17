from fastapi import APIRouter, Depends

from app.api.deps import require_role
from app.database.models import User, UserRole
from app.services.simulation import engine

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


@router.post("/start")
async def start_simulation(
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.TRANSPORT_AUTHORITY)),
):
    await engine.start()
    return engine.status()


@router.post("/stop")
async def stop_simulation(
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.TRANSPORT_AUTHORITY)),
):
    await engine.stop()
    return engine.status()


@router.get("/status")
def simulation_status():
    return engine.status()

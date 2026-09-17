from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/events")
async def events_ws(websocket: WebSocket):
    """
    Dashboard clients connect here to receive live events as they're created:
    {"channel": "detection_event" | "road_defect" | "traffic_event" | "incident" | "bus_position",
     "data": {...}}
    """
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect client -> server messages, but must keep the
            # receive loop alive to detect disconnects.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

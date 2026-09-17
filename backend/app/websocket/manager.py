"""
Minimal WebSocket hub. Any REST endpoint that creates a detection-type record
(events, road-damage, traffic, incidents) calls `manager.broadcast(...)` so every
connected dashboard client gets it live, matching the required pipeline:

Video → AI Detection → Event Generator → Event Queue → Backend → WebSocket → Dashboard

For an SIH prototype a single in-process manager is sufficient (no Redis pub/sub
needed) since the backend runs as one process. Documented as a scaling note in
docs/ARCHITECTURE.md for anyone extending this to multiple backend instances.
"""
import json
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, channel: str, payload: dict[str, Any]) -> None:
        message = json.dumps({"channel": channel, "data": payload}, default=str)
        stale: list[WebSocket] = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                stale.append(connection)
        for conn in stale:
            self.disconnect(conn)


manager = ConnectionManager()

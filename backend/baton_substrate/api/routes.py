from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    ok: bool = True
    service: str = "baton-substrate"
    version: str = "0.1.0"


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@router.websocket("/ws")
async def ws(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        # Placeholder: server will push events here.
        while True:
            _ = await websocket.receive_text()
            await websocket.send_text("{"type":"noop"}")
    except WebSocketDisconnect:
        return

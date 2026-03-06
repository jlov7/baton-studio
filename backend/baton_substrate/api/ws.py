from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from baton_substrate.ws.manager import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{mission_id}")
async def mission_ws(websocket: WebSocket, mission_id: str) -> None:
    await manager.connect(mission_id, websocket)
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(mission_id, websocket)

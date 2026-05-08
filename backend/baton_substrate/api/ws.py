from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, WebSocketException, status

from baton_substrate.api.security import authorize_websocket
import baton_substrate.db.engine as db_engine
from baton_substrate.services import mission_service
from baton_substrate.ws.manager import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{mission_id}")
async def mission_ws(websocket: WebSocket, mission_id: str) -> None:
    await authorize_websocket(websocket)
    async with db_engine.get_db() as db:
        if not await mission_service.mission_exists(db, mission_id):
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason=f"Mission {mission_id} not found",
            )
    await manager.connect(mission_id, websocket)
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(mission_id, websocket)

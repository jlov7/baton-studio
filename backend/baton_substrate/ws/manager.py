from __future__ import annotations

import asyncio
import logging
from collections import defaultdict

from fastapi import WebSocket

logger = logging.getLogger("baton_substrate.ws")


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def connect(self, mission_id: str, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._connections[mission_id].append(ws)

    async def disconnect(self, mission_id: str, ws: WebSocket) -> None:
        async with self._lock:
            conns = self._connections.get(mission_id, [])
            if ws in conns:
                conns.remove(ws)
                if not conns:
                    del self._connections[mission_id]

    async def broadcast(self, mission_id: str, message: dict[str, object]) -> None:
        async with self._lock:
            conns = list(self._connections.get(mission_id, []))
        dead: list[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_json(message)
            except Exception as exc:
                logger.warning(
                    "websocket_broadcast_failed",
                    extra={"mission_id": mission_id, "error": str(exc)},
                )
                dead.append(ws)
        for ws in dead:
            await self.disconnect(mission_id, ws)


manager = ConnectionManager()

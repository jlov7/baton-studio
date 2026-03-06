from __future__ import annotations

import asyncio
from collections import defaultdict

from fastapi import WebSocket


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

    async def broadcast(self, mission_id: str, message: dict) -> None:
        async with self._lock:
            conns = list(self._connections.get(mission_id, []))
        dead: list[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(mission_id, ws)


manager = ConnectionManager()

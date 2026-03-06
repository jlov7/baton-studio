from __future__ import annotations

from baton_substrate.models.common import EventEnvelope
from baton_substrate.ws.manager import manager


async def broadcast_event(event: EventEnvelope) -> None:
    await manager.broadcast(event.mission_id, event.model_dump())

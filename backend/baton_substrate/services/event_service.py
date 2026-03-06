from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.db.schema import EventRow
from baton_substrate.models.common import Actor, EventEnvelope
from baton_substrate.ws.broadcaster import broadcast_event


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _event_id() -> str:
    return f"evt_{uuid.uuid4().hex[:12]}"


async def emit(
    db: AsyncSession,
    mission_id: str,
    event_type: str,
    actor: Actor,
    payload: dict[str, Any] | None = None,
) -> EventEnvelope:
    eid = _event_id()
    ts = _now()
    envelope = EventEnvelope(
        event_id=eid,
        ts=ts,
        mission_id=mission_id,
        type=event_type,
        actor=actor,
        payload=payload or {},
    )
    row = EventRow(
        event_id=eid,
        mission_id=mission_id,
        ts=ts,
        type=event_type,
        actor_json=actor.model_dump_json(),
        payload_json=envelope.model_dump_json(include={"payload"}),
    )
    db.add(row)
    await db.flush()
    await broadcast_event(envelope)
    return envelope


async def query(
    db: AsyncSession,
    mission_id: str,
    after: str | None = None,
    event_type: str | None = None,
    limit: int = 100,
) -> tuple[list[EventEnvelope], str | None]:
    import orjson

    stmt = select(EventRow).where(EventRow.mission_id == mission_id)
    if after:
        stmt = stmt.where(EventRow.ts > after)
    if event_type:
        stmt = stmt.where(EventRow.type == event_type)
    stmt = stmt.order_by(EventRow.ts).limit(limit + 1)
    result = await db.execute(stmt)
    rows = list(result.scalars().all())

    cursor: str | None = None
    if len(rows) > limit:
        rows = rows[:limit]
        cursor = rows[-1].ts

    events: list[EventEnvelope] = []
    for r in rows:
        actor_data = orjson.loads(r.actor_json)
        payload_data = orjson.loads(r.payload_json) if r.payload_json else {}
        if "payload" in payload_data:
            payload_data = payload_data["payload"]
        events.append(
            EventEnvelope(
                event_id=r.event_id,
                ts=r.ts,
                mission_id=r.mission_id,
                type=r.type,
                actor=Actor(**actor_data),
                payload=payload_data,
            )
        )
    return events, cursor

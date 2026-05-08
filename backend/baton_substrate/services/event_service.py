from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.config import settings
from baton_substrate.db.schema import EventRow
from baton_substrate.models.common import Actor, EventEnvelope
from baton_substrate.ws.broadcaster import broadcast_event


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _event_id() -> str:
    return f"evt_{uuid.uuid4().hex[:12]}"


def _encode_cursor(ts: str, event_id: str) -> str:
    return f"{ts}|{event_id}"


def _decode_cursor(cursor: str) -> tuple[str, str | None]:
    if "|" not in cursor:
        return cursor, None
    ts, event_id = cursor.split("|", 1)
    return ts, event_id or None


def parse_payload(raw: str) -> dict[str, Any]:
    if not raw:
        return {}
    payload = json.loads(raw)
    if isinstance(payload, dict) and "payload" in payload and len(payload) == 1:
        nested = payload["payload"]
        return nested if isinstance(nested, dict) else {}
    return payload if isinstance(payload, dict) else {}


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
        payload_json=json.dumps(payload or {}),
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

    limit = max(1, min(limit, settings.event_page_limit_max))
    stmt = select(EventRow).where(EventRow.mission_id == mission_id)
    if after:
        after_ts, after_event_id = _decode_cursor(after)
        if after_event_id:
            stmt = stmt.where(
                or_(
                    EventRow.ts > after_ts,
                    and_(EventRow.ts == after_ts, EventRow.event_id > after_event_id),
                )
            )
        else:
            stmt = stmt.where(EventRow.ts > after_ts)
    if event_type:
        stmt = stmt.where(EventRow.type == event_type)
    stmt = stmt.order_by(EventRow.ts, EventRow.event_id).limit(limit + 1)
    result = await db.execute(stmt)
    rows = list(result.scalars().all())

    cursor: str | None = None
    if len(rows) > limit:
        rows = rows[:limit]
        cursor = _encode_cursor(rows[-1].ts, rows[-1].event_id)

    events: list[EventEnvelope] = []
    for r in rows:
        actor_data = orjson.loads(r.actor_json)
        payload_data = parse_payload(r.payload_json)
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

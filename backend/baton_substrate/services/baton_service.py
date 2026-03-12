from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.db.schema import BatonStateRow
from baton_substrate.models.baton import BatonStateResponse
from baton_substrate.models.common import Actor
from baton_substrate.services import event_service


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


async def _get_state(db: AsyncSession, mission_id: str) -> BatonStateRow:
    result = await db.execute(select(BatonStateRow).where(BatonStateRow.mission_id == mission_id))
    row = result.scalar_one_or_none()
    if not row:
        raise ValueError(f"No baton state for mission {mission_id}")
    return row


def _parse_queue(row: BatonStateRow) -> list[str]:
    return json.loads(row.queue_json) if row.queue_json else []


def _is_expired(row: BatonStateRow) -> bool:
    if not row.lease_expires_at:
        return False
    expires = datetime.fromisoformat(row.lease_expires_at)
    return _now() >= expires


async def _auto_release_if_expired(db: AsyncSession, row: BatonStateRow) -> bool:
    if row.holder_actor_id and _is_expired(row):
        old_holder = row.holder_actor_id
        queue = _parse_queue(row)
        if queue:
            next_holder = queue.pop(0)
            row.holder_actor_id = next_holder
            row.queue_json = json.dumps(queue)
            row.lease_expires_at = _iso(_now() + timedelta(milliseconds=20_000))
        else:
            row.holder_actor_id = None
            row.queue_json = "[]"
            row.lease_expires_at = None
        await db.flush()
        actor = Actor(actor_id="system", actor_type="system", display_name="System")
        await event_service.emit(
            db,
            row.mission_id,
            "baton.timeout",
            actor,
            {"expired_holder": old_holder, "new_holder": row.holder_actor_id},
        )
        return True
    return False


async def claim(
    db: AsyncSession,
    mission_id: str,
    actor_id: str,
    lease_ms: int = 20_000,
) -> BatonStateResponse:
    row = await _get_state(db, mission_id)
    await _auto_release_if_expired(db, row)

    actor = Actor(actor_id=actor_id, actor_type="agent", display_name=actor_id)

    if row.holder_actor_id is None:
        row.holder_actor_id = actor_id
        row.lease_expires_at = _iso(_now() + timedelta(milliseconds=lease_ms))
        await db.flush()
        await event_service.emit(
            db,
            mission_id,
            "baton.claimed",
            actor,
            {"holder": actor_id},
        )
    elif row.holder_actor_id != actor_id:
        queue = _parse_queue(row)
        if actor_id not in queue:
            queue.append(actor_id)
            row.queue_json = json.dumps(queue)
            await db.flush()
            await event_service.emit(
                db,
                mission_id,
                "baton.queued",
                actor,
                {"position": len(queue)},
            )

    queue = _parse_queue(row)
    return BatonStateResponse(
        holder=row.holder_actor_id,
        queue=queue,
        lease_expires_at=row.lease_expires_at,
    )


async def release(
    db: AsyncSession,
    mission_id: str,
    actor_id: str,
) -> BatonStateResponse:
    row = await _get_state(db, mission_id)
    await _auto_release_if_expired(db, row)

    if row.holder_actor_id != actor_id:
        queue = _parse_queue(row)
        return BatonStateResponse(
            holder=row.holder_actor_id,
            queue=queue,
            lease_expires_at=row.lease_expires_at,
        )

    actor = Actor(actor_id=actor_id, actor_type="agent", display_name=actor_id)
    queue = _parse_queue(row)

    if queue:
        next_holder = queue.pop(0)
        row.holder_actor_id = next_holder
        row.queue_json = json.dumps(queue)
        row.lease_expires_at = _iso(_now() + timedelta(milliseconds=20_000))
        await event_service.emit(
            db,
            mission_id,
            "baton.transferred",
            actor,
            {"from": actor_id, "to": next_holder},
        )
    else:
        row.holder_actor_id = None
        row.queue_json = "[]"
        row.lease_expires_at = None

    await db.flush()
    await event_service.emit(
        db,
        mission_id,
        "baton.released",
        actor,
        {"released_by": actor_id, "new_holder": row.holder_actor_id},
    )

    queue = _parse_queue(row)
    return BatonStateResponse(
        holder=row.holder_actor_id,
        queue=queue,
        lease_expires_at=row.lease_expires_at,
    )


async def get_state(db: AsyncSession, mission_id: str) -> BatonStateResponse:
    row = await _get_state(db, mission_id)
    await _auto_release_if_expired(db, row)
    queue = _parse_queue(row)
    return BatonStateResponse(
        holder=row.holder_actor_id,
        queue=queue,
        lease_expires_at=row.lease_expires_at,
    )

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.db.schema import AgentRow
from baton_substrate.models.agent import AgentDetail
from baton_substrate.models.common import Actor
from baton_substrate.services import event_service


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def register(
    db: AsyncSession,
    mission_id: str,
    actor_id: str,
    display_name: str = "",
    role: str = "agent",
) -> AgentDetail:
    now = _now()
    row = AgentRow(
        mission_id=mission_id,
        actor_id=actor_id,
        display_name=display_name or actor_id,
        role=role,
        joined_at=now,
        last_seen_at=now,
        status="active",
    )
    db.add(row)
    await db.flush()
    actor = Actor(actor_id=actor_id, actor_type="agent", display_name=display_name or actor_id)
    await event_service.emit(
        db,
        mission_id,
        "agent.joined",
        actor,
        {"role": role},
    )
    return AgentDetail(
        actor_id=actor_id,
        display_name=display_name or actor_id,
        role=role,
        joined_at=now,
        last_seen_at=now,
        status="active",
        energy_balance=0,
    )


async def list_agents(db: AsyncSession, mission_id: str) -> list[AgentDetail]:
    result = await db.execute(select(AgentRow).where(AgentRow.mission_id == mission_id))
    rows = result.scalars().all()
    return [
        AgentDetail(
            actor_id=r.actor_id,
            display_name=r.display_name,
            role=r.role,
            joined_at=r.joined_at,
            last_seen_at=r.last_seen_at,
            status=r.status,
        )
        for r in rows
    ]


async def touch(db: AsyncSession, mission_id: str, actor_id: str) -> None:
    result = await db.execute(
        select(AgentRow).where(
            AgentRow.mission_id == mission_id,
            AgentRow.actor_id == actor_id,
        )
    )
    row = result.scalar_one_or_none()
    if row:
        row.last_seen_at = _now()
        await db.flush()

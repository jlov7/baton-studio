from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.db.schema import BatonStateRow, MissionRow
from baton_substrate.models.common import Actor
from baton_substrate.models.mission import MissionResponse
from baton_substrate.services import event_service

SYSTEM_ACTOR = Actor(actor_id="system", actor_type="system", display_name="System")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def create_mission(
    db: AsyncSession,
    title: str,
    goal: str = "",
    energy_budget: int = 1000,
) -> MissionResponse:
    mid = f"mis_{uuid.uuid4().hex[:12]}"
    now = _now()
    row = MissionRow(
        mission_id=mid,
        created_at=now,
        title=title,
        goal=goal,
        energy_budget=energy_budget,
        status="idle",
    )
    db.add(row)
    baton = BatonStateRow(mission_id=mid, holder_actor_id=None, queue_json="[]")
    db.add(baton)
    await db.flush()
    await event_service.emit(
        db, mid, "mission.created", SYSTEM_ACTOR,
        {"title": title, "goal": goal, "energy_budget": energy_budget},
    )
    return MissionResponse(
        mission_id=mid,
        created_at=now,
        title=title,
        goal=goal,
        energy_budget=energy_budget,
        status="idle",
    )


async def get_mission(db: AsyncSession, mission_id: str) -> MissionResponse | None:
    result = await db.execute(select(MissionRow).where(MissionRow.mission_id == mission_id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    return MissionResponse(
        mission_id=row.mission_id,
        created_at=row.created_at,
        title=row.title,
        goal=row.goal,
        energy_budget=row.energy_budget,
        status=row.status,
    )


async def update_status(db: AsyncSession, mission_id: str, status: str) -> MissionResponse:
    result = await db.execute(select(MissionRow).where(MissionRow.mission_id == mission_id))
    row = result.scalar_one_or_none()
    if not row:
        raise ValueError(f"Mission {mission_id} not found")
    row.status = status
    await db.flush()
    await event_service.emit(
        db, mission_id, "mission.status_changed", SYSTEM_ACTOR,
        {"status": status},
    )
    return MissionResponse(
        mission_id=row.mission_id,
        created_at=row.created_at,
        title=row.title,
        goal=row.goal,
        energy_budget=row.energy_budget,
        status=row.status,
    )

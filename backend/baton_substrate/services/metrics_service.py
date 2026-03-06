from __future__ import annotations

import math

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.db.schema import CausalNodeRow, EventRow, PatchRow
from baton_substrate.models.metrics import SCMetricResponse, SCPoint

ALPHA = 0.3
BETA = 0.2
GAMMA = 0.1


async def compute_sc(db: AsyncSession, mission_id: str) -> SCMetricResponse:
    violations_result = await db.execute(
        select(func.count())
        .select_from(PatchRow)
        .where(PatchRow.mission_id == mission_id, PatchRow.status == "rejected")
    )
    v_count = violations_result.scalar_one()

    stale_result = await db.execute(
        select(func.count())
        .select_from(CausalNodeRow)
        .where(CausalNodeRow.mission_id == mission_id, CausalNodeRow.status == "stale")
    )
    i_count = stale_result.scalar_one()

    total_patches = await db.execute(
        select(func.count())
        .select_from(PatchRow)
        .where(PatchRow.mission_id == mission_id)
    )
    total = total_patches.scalar_one()
    r_count = max(0, total - v_count * 2) if total > 0 else 0

    sc_value = math.exp(-ALPHA * v_count - BETA * i_count - GAMMA * r_count)
    sc_value = round(sc_value, 4)

    event_result = await db.execute(
        select(EventRow)
        .where(
            EventRow.mission_id == mission_id,
            EventRow.type.in_(["patch.committed", "patch.rejected", "causal.invalidation"]),
        )
        .order_by(EventRow.ts)
    )
    events = event_result.scalars().all()

    history: list[SCPoint] = []
    running_v = 0
    running_i = 0
    running_r = 0
    for evt in events:
        if evt.type == "patch.rejected":
            running_v += 1
        elif evt.type == "causal.invalidation":
            running_i += 1
        elif evt.type == "patch.committed":
            running_r += 1
        sc_t = math.exp(-ALPHA * running_v - BETA * running_i - GAMMA * running_r)
        history.append(SCPoint(ts=evt.ts, value=round(sc_t, 4)))

    return SCMetricResponse(sc_current=sc_value, sc_history=history)

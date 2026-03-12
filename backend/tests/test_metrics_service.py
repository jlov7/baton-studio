"""Tests for SC metric computation."""

from __future__ import annotations

import math
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.db.schema import BatonStateRow, MissionRow
from baton_substrate.models.common import Patch, PatchOp
from baton_substrate.services import causal_service, metrics_service, patch_service, world_service


async def _seed(db: AsyncSession, mid: str = "mis_test") -> str:
    db.add(
        MissionRow(
            mission_id=mid,
            created_at=datetime.now(timezone.utc).isoformat(),
            title="Test",
            goal="",
            energy_budget=1000,
            status="idle",
        )
    )
    db.add(BatonStateRow(mission_id=mid, holder_actor_id=None, queue_json="[]"))
    await db.flush()
    await world_service.register_entity_type(
        db,
        mid,
        "Evidence",
        json_schema={
            "type": "object",
            "properties": {"claim": {"type": "string"}},
            "required": ["claim"],
        },
        invariants=[{"rule": "required_fields", "fields": ["claim"], "severity": "hard"}],
    )
    return mid


async def test_sc_empty_mission(db: AsyncSession) -> None:
    mid = await _seed(db)
    result = await metrics_service.compute_sc(db, mid)
    assert result.sc_current == 1.0
    assert result.sc_history == []


async def test_sc_after_rejection(db: AsyncSession) -> None:
    mid = await _seed(db)
    patch = Patch(ops=[PatchOp(op="upsert", type="Evidence", id="ev-1", value={})])
    await patch_service.propose(db, mid, "agent-a", patch)
    result = await metrics_service.compute_sc(db, mid)
    # SC = exp(-0.3 * 1 - 0.2 * 0 - 0.1 * max(0, 1 - 2))
    # r_count = max(0, 1 - 1*2) = 0
    expected = round(math.exp(-0.3), 4)
    assert result.sc_current == expected


async def test_sc_after_commit(db: AsyncSession) -> None:
    mid = await _seed(db)
    patch = Patch(ops=[PatchOp(op="upsert", type="Evidence", id="ev-1", value={"claim": "ok"})])
    r = await patch_service.propose(db, mid, "agent-a", patch)
    await patch_service.commit(db, mid, "agent-a", r.proposal_id)
    result = await metrics_service.compute_sc(db, mid)
    # 0 rejections, 0 stale, total=1, r_count = max(0, 1 - 0) = 1
    expected = round(math.exp(-0.1 * 1), 4)
    assert result.sc_current == expected


async def test_sc_history_tracks_events(db: AsyncSession) -> None:
    mid = await _seed(db)
    # Commit one patch
    patch = Patch(ops=[PatchOp(op="upsert", type="Evidence", id="ev-1", value={"claim": "ok"})])
    r = await patch_service.propose(db, mid, "agent-a", patch)
    await patch_service.commit(db, mid, "agent-a", r.proposal_id)
    # Reject another
    bad_patch = Patch(ops=[PatchOp(op="upsert", type="Evidence", id="ev-2", value={})])
    await patch_service.propose(db, mid, "agent-a", bad_patch)

    result = await metrics_service.compute_sc(db, mid)
    assert len(result.sc_history) >= 2


async def test_sc_with_stale_nodes(db: AsyncSession) -> None:
    mid = await _seed(db)
    await causal_service.add_edge(db, mid, "a", "A", "B", "depends_on")
    await causal_service.invalidate_downstream(db, mid, "A", "a")
    result = await metrics_service.compute_sc(db, mid)
    # 0 rejections, 1 stale, 0 patches
    expected = round(math.exp(-0.2 * 1), 4)
    assert result.sc_current == expected

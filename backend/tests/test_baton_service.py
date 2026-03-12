"""Tests for baton claim/release/queue/expiration logic."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.db.schema import BatonStateRow, MissionRow
from baton_substrate.services import baton_service


async def _seed_mission(db: AsyncSession, mid: str = "mis_test") -> str:
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
    return mid


async def test_claim_empty(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    state = await baton_service.claim(db, mid, "agent-a")
    assert state.holder == "agent-a"
    assert state.queue == []
    assert state.lease_expires_at is not None


async def test_claim_queues_second_agent(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    await baton_service.claim(db, mid, "agent-a")
    state = await baton_service.claim(db, mid, "agent-b")
    assert state.holder == "agent-a"
    assert state.queue == ["agent-b"]


async def test_claim_same_agent_idempotent(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    await baton_service.claim(db, mid, "agent-a")
    state = await baton_service.claim(db, mid, "agent-a")
    assert state.holder == "agent-a"
    assert state.queue == []


async def test_release_clears_holder(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    await baton_service.claim(db, mid, "agent-a")
    state = await baton_service.release(db, mid, "agent-a")
    assert state.holder is None
    assert state.queue == []


async def test_release_promotes_next_in_queue(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    await baton_service.claim(db, mid, "agent-a")
    await baton_service.claim(db, mid, "agent-b")
    await baton_service.claim(db, mid, "agent-c")
    state = await baton_service.release(db, mid, "agent-a")
    assert state.holder == "agent-b"
    assert state.queue == ["agent-c"]


async def test_release_non_holder_is_noop(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    await baton_service.claim(db, mid, "agent-a")
    state = await baton_service.release(db, mid, "agent-b")
    assert state.holder == "agent-a"


async def test_get_state_empty(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    state = await baton_service.get_state(db, mid)
    assert state.holder is None
    assert state.queue == []


async def test_auto_release_on_expired_lease(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    await baton_service.claim(db, mid, "agent-a")
    # Manually expire the lease
    from sqlalchemy import select

    result = await db.execute(select(BatonStateRow).where(BatonStateRow.mission_id == mid))
    row = result.scalar_one()
    row.lease_expires_at = (datetime.now(timezone.utc) - timedelta(seconds=5)).isoformat()
    await db.flush()

    state = await baton_service.get_state(db, mid)
    assert state.holder is None


async def test_auto_release_promotes_queued_on_timeout(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    await baton_service.claim(db, mid, "agent-a")
    await baton_service.claim(db, mid, "agent-b")
    # Expire agent-a's lease
    from sqlalchemy import select

    result = await db.execute(select(BatonStateRow).where(BatonStateRow.mission_id == mid))
    row = result.scalar_one()
    row.lease_expires_at = (datetime.now(timezone.utc) - timedelta(seconds=5)).isoformat()
    await db.flush()

    state = await baton_service.get_state(db, mid)
    assert state.holder == "agent-b"
    assert state.queue == []

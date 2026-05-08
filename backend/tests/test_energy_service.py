"""Tests for energy allocation, spending, and balance checks."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.db.schema import MissionRow
from baton_substrate.services import energy_service


async def _seed_mission(db: AsyncSession, mid: str = "mis_test", budget: int = 1000) -> str:
    db.add(
        MissionRow(
            mission_id=mid,
            created_at=datetime.now(timezone.utc).isoformat(),
            title="Test",
            goal="",
            energy_budget=budget,
            status="idle",
        )
    )
    await db.flush()
    return mid


async def test_get_or_create_account(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    acct = await energy_service.get_or_create_account(db, mid, "agent-a")
    assert acct.balance == 0
    assert acct.actor_id == "agent-a"


async def test_get_or_create_returns_existing(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    await energy_service.get_or_create_account(db, mid, "agent-a")
    await energy_service.allocate(db, mid, "agent-a", 100)
    acct2 = await energy_service.get_or_create_account(db, mid, "agent-a")
    assert acct2.balance == 100


async def test_allocate(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    balance = await energy_service.allocate(db, mid, "agent-a", 500)
    assert balance == 500


async def test_allocate_adds_to_existing(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    await energy_service.allocate(db, mid, "agent-a", 300)
    balance = await energy_service.allocate(db, mid, "agent-a", 200)
    assert balance == 500


async def test_auto_allocate_first_agent(db: AsyncSession) -> None:
    mid = await _seed_mission(db, budget=1000)
    balance = await energy_service.auto_allocate(db, mid, "agent-a")
    assert balance == 1000  # 1000 // (0 existing + 1)


async def test_auto_allocate_second_agent(db: AsyncSession) -> None:
    mid = await _seed_mission(db, budget=1000)
    await energy_service.auto_allocate(db, mid, "agent-a")
    balance = await energy_service.auto_allocate(db, mid, "agent-b")
    assert balance == 500  # 1000 // (1 existing + 1)


async def test_auto_allocate_rebalances_without_exceeding_budget(db: AsyncSession) -> None:
    mid = await _seed_mission(db, budget=1000)
    for actor_id in ["agent-a", "agent-b", "agent-c", "agent-d"]:
        await energy_service.auto_allocate(db, mid, actor_id)

    balances = [
        (await energy_service.get_balance(db, mid, actor_id)).balance
        for actor_id in ["agent-a", "agent-b", "agent-c", "agent-d"]
    ]
    assert balances == [250, 250, 250, 250]
    assert sum(balances) == 1000


async def test_spend(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    await energy_service.allocate(db, mid, "agent-a", 100)
    result = await energy_service.spend(db, mid, "agent-a", 30, "test op")
    assert result.new_balance == 70


async def test_spend_insufficient_raises(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    await energy_service.allocate(db, mid, "agent-a", 10)
    with pytest.raises(ValueError, match="Insufficient energy"):
        await energy_service.spend(db, mid, "agent-a", 50, "too much")


async def test_get_balance(db: AsyncSession) -> None:
    mid = await _seed_mission(db, budget=1000)
    await energy_service.allocate(db, mid, "agent-a", 250)
    result = await energy_service.get_balance(db, mid, "agent-a")
    assert result.balance == 250
    assert result.mission_budget == 1000
    assert result.actor_id == "agent-a"

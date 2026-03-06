from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.db.schema import EnergyAccountRow, MissionRow
from baton_substrate.models.common import Actor
from baton_substrate.models.energy import EnergyBalanceResponse, EnergySpendResponse
from baton_substrate.services import event_service


async def get_or_create_account(
    db: AsyncSession, mission_id: str, actor_id: str,
) -> EnergyAccountRow:
    result = await db.execute(
        select(EnergyAccountRow).where(
            EnergyAccountRow.mission_id == mission_id,
            EnergyAccountRow.actor_id == actor_id,
        )
    )
    row = result.scalar_one_or_none()
    if row:
        return row
    row = EnergyAccountRow(mission_id=mission_id, actor_id=actor_id, balance=0)
    db.add(row)
    await db.flush()
    return row


async def allocate(
    db: AsyncSession, mission_id: str, actor_id: str, amount: int,
) -> int:
    acct = await get_or_create_account(db, mission_id, actor_id)
    acct.balance += amount
    await db.flush()
    actor = Actor(actor_id="system", actor_type="system", display_name="System")
    await event_service.emit(
        db, mission_id, "energy.allocated", actor,
        {"actor_id": actor_id, "amount": amount, "new_balance": acct.balance},
    )
    return acct.balance


async def auto_allocate(db: AsyncSession, mission_id: str, actor_id: str) -> int:
    result = await db.execute(select(MissionRow).where(MissionRow.mission_id == mission_id))
    mission = result.scalar_one_or_none()
    if not mission:
        raise ValueError(f"Mission {mission_id} not found")
    count_result = await db.execute(
        select(EnergyAccountRow).where(EnergyAccountRow.mission_id == mission_id)
    )
    existing = list(count_result.scalars().all())
    share = mission.energy_budget // (len(existing) + 1)
    new_balance = await allocate(db, mission_id, actor_id, share)
    return new_balance


async def get_balance(
    db: AsyncSession, mission_id: str, actor_id: str,
) -> EnergyBalanceResponse:
    acct = await get_or_create_account(db, mission_id, actor_id)
    result = await db.execute(select(MissionRow).where(MissionRow.mission_id == mission_id))
    mission = result.scalar_one_or_none()
    budget = mission.energy_budget if mission else 0
    return EnergyBalanceResponse(
        actor_id=actor_id,
        balance=acct.balance,
        mission_budget=budget,
    )


async def spend(
    db: AsyncSession, mission_id: str, actor_id: str, amount: int, reason: str = "",
) -> EnergySpendResponse:
    acct = await get_or_create_account(db, mission_id, actor_id)
    if acct.balance < amount:
        raise ValueError(f"Insufficient energy: have {acct.balance}, need {amount}")
    acct.balance -= amount
    await db.flush()
    actor = Actor(actor_id=actor_id, actor_type="agent", display_name=actor_id)
    await event_service.emit(
        db, mission_id, "energy.spent", actor,
        {"amount": amount, "reason": reason, "new_balance": acct.balance},
    )
    return EnergySpendResponse(new_balance=acct.balance)

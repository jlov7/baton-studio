from __future__ import annotations

from fastapi import APIRouter, HTTPException

from baton_substrate.db import get_db
from baton_substrate.models.energy import (
    EnergyBalanceResponse,
    EnergySpendRequest,
    EnergySpendResponse,
)
from baton_substrate.services import energy_service

router = APIRouter(prefix="/missions/{mission_id}/energy", tags=["energy"])


@router.get("/{actor_id}", response_model=EnergyBalanceResponse)
async def get_balance(mission_id: str, actor_id: str) -> EnergyBalanceResponse:
    async with get_db() as db:
        return await energy_service.get_balance(db, mission_id, actor_id)


@router.post("/spend", response_model=EnergySpendResponse)
async def spend_energy(
    mission_id: str, req: EnergySpendRequest,
) -> EnergySpendResponse:
    async with get_db() as db:
        try:
            return await energy_service.spend(
                db, mission_id, req.actor_id, req.amount, req.reason,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

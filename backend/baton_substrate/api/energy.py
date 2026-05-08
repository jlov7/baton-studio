from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from baton_substrate.api.dependencies import require_existing_mission
import baton_substrate.db.engine as db_engine
from baton_substrate.models.energy import (
    EnergyBalanceResponse,
    EnergySpendRequest,
    EnergySpendResponse,
)
from baton_substrate.services import energy_service

router = APIRouter(
    prefix="/missions/{mission_id}/energy",
    tags=["energy"],
    dependencies=[Depends(require_existing_mission)],
)


@router.get("/{actor_id}", response_model=EnergyBalanceResponse)
async def get_balance(mission_id: str, actor_id: str) -> EnergyBalanceResponse:
    async with db_engine.get_db() as db:
        try:
            return await energy_service.get_balance(db, mission_id, actor_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/spend", response_model=EnergySpendResponse)
async def spend_energy(
    mission_id: str,
    req: EnergySpendRequest,
) -> EnergySpendResponse:
    async with db_engine.get_db() as db:
        try:
            return await energy_service.spend(
                db,
                mission_id,
                req.actor_id,
                req.amount,
                req.reason,
            )
        except ValueError as e:
            status_code = 409 if "Insufficient energy" in str(e) else 400
            raise HTTPException(status_code=status_code, detail=str(e)) from e

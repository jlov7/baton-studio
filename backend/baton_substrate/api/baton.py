from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from baton_substrate.api.dependencies import require_existing_mission
import baton_substrate.db.engine as db_engine
from baton_substrate.models.baton import (
    BatonStateResponse,
    ClaimBatonRequest,
    ReleaseBatonRequest,
)
from baton_substrate.services import baton_service

router = APIRouter(
    prefix="/missions/{mission_id}/baton",
    tags=["baton"],
    dependencies=[Depends(require_existing_mission)],
)


@router.post("/claim", response_model=BatonStateResponse)
async def claim_baton(
    mission_id: str,
    req: ClaimBatonRequest,
) -> BatonStateResponse:
    async with db_engine.get_db() as db:
        try:
            return await baton_service.claim(
                db,
                mission_id,
                req.actor_id,
                req.lease_ms,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/release", response_model=BatonStateResponse)
async def release_baton(
    mission_id: str,
    req: ReleaseBatonRequest,
) -> BatonStateResponse:
    async with db_engine.get_db() as db:
        try:
            return await baton_service.release(db, mission_id, req.actor_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=BatonStateResponse)
async def get_baton(mission_id: str) -> BatonStateResponse:
    async with db_engine.get_db() as db:
        try:
            return await baton_service.get_state(db, mission_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

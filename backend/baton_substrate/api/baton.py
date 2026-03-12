from __future__ import annotations

from fastapi import APIRouter

from baton_substrate.db import get_db
from baton_substrate.models.baton import (
    BatonStateResponse,
    ClaimBatonRequest,
    ReleaseBatonRequest,
)
from baton_substrate.services import baton_service

router = APIRouter(prefix="/missions/{mission_id}/baton", tags=["baton"])


@router.post("/claim", response_model=BatonStateResponse)
async def claim_baton(
    mission_id: str,
    req: ClaimBatonRequest,
) -> BatonStateResponse:
    async with get_db() as db:
        return await baton_service.claim(
            db,
            mission_id,
            req.actor_id,
            req.lease_ms,
        )


@router.post("/release", response_model=BatonStateResponse)
async def release_baton(
    mission_id: str,
    req: ReleaseBatonRequest,
) -> BatonStateResponse:
    async with get_db() as db:
        return await baton_service.release(db, mission_id, req.actor_id)


@router.get("", response_model=BatonStateResponse)
async def get_baton(mission_id: str) -> BatonStateResponse:
    async with get_db() as db:
        return await baton_service.get_state(db, mission_id)

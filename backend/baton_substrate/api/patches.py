from __future__ import annotations

from fastapi import APIRouter, HTTPException

from baton_substrate.db import get_db
from baton_substrate.models.patch import (
    CommitPatchRequest,
    CommitPatchResponse,
    ProposePatchRequest,
    ProposePatchResponse,
)
from baton_substrate.services import baton_service, energy_service, patch_service

router = APIRouter(prefix="/missions/{mission_id}/patches", tags=["patches"])


@router.post("/propose", response_model=ProposePatchResponse)
async def propose_patch(
    mission_id: str,
    req: ProposePatchRequest,
) -> ProposePatchResponse:
    async with get_db() as db:
        return await patch_service.propose(
            db,
            mission_id,
            req.actor_id,
            req.patch,
        )


@router.post("/commit", response_model=CommitPatchResponse)
async def commit_patch(
    mission_id: str,
    req: CommitPatchRequest,
) -> CommitPatchResponse:
    async with get_db() as db:
        state = await baton_service.get_state(db, mission_id)
        if state.holder != req.actor_id:
            raise HTTPException(
                status_code=403,
                detail=f"Actor {req.actor_id} does not hold the baton (holder: {state.holder})",
            )
        result = await patch_service.commit(
            db,
            mission_id,
            req.actor_id,
            req.proposal_id,
        )
        if result.committed:
            energy_cost = len(result.new_versions) * 10
            try:
                await energy_service.spend(
                    db,
                    mission_id,
                    req.actor_id,
                    energy_cost,
                    "patch_commit",
                )
            except ValueError:
                pass
        return result

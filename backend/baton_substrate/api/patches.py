from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from baton_substrate.api.dependencies import require_existing_mission
import baton_substrate.db.engine as db_engine
from baton_substrate.models.patch import (
    CommitPatchRequest,
    CommitPatchResponse,
    ProposePatchRequest,
    ProposePatchResponse,
)
from baton_substrate.services import baton_service, energy_service, patch_service

router = APIRouter(
    prefix="/missions/{mission_id}/patches",
    tags=["patches"],
    dependencies=[Depends(require_existing_mission)],
)


@router.post("/propose", response_model=ProposePatchResponse)
async def propose_patch(
    mission_id: str,
    req: ProposePatchRequest,
) -> ProposePatchResponse:
    async with db_engine.get_db() as db:
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
    async with db_engine.get_db() as db:
        state = await baton_service.get_state(db, mission_id)
        if state.holder != req.actor_id:
            raise HTTPException(
                status_code=403,
                detail=f"Actor {req.actor_id} does not hold the baton (holder: {state.holder})",
            )
        energy_cost = await patch_service.estimate_commit_energy_cost(
            db,
            mission_id,
            req.proposal_id,
        )
        try:
            if energy_cost:
                await energy_service.ensure_can_spend(db, mission_id, req.actor_id, energy_cost)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        result = await patch_service.commit(
            db,
            mission_id,
            req.actor_id,
            req.proposal_id,
        )
        if result.committed:
            try:
                await energy_service.spend(
                    db,
                    mission_id,
                    req.actor_id,
                    energy_cost,
                    "patch_commit",
                )
            except ValueError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
        return result

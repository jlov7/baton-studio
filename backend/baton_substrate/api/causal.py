from __future__ import annotations

from fastapi import APIRouter

from baton_substrate.db import get_db
from baton_substrate.models.causal import (
    AddEdgeRequest,
    AddEdgeResponse,
    CausalGraphSnapshot,
)
from baton_substrate.services import causal_service

router = APIRouter(prefix="/missions/{mission_id}/causal", tags=["causal"])


@router.post("/edge", response_model=AddEdgeResponse)
async def add_edge(mission_id: str, req: AddEdgeRequest) -> AddEdgeResponse:
    async with get_db() as db:
        return await causal_service.add_edge(
            db, mission_id, req.actor_id,
            req.from_id, req.to_id, req.type, req.metadata,
        )


@router.get("/graph", response_model=CausalGraphSnapshot)
async def get_graph(mission_id: str) -> CausalGraphSnapshot:
    async with get_db() as db:
        return await causal_service.get_graph(db, mission_id)

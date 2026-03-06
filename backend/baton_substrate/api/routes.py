from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from baton_substrate.api import (
    agents,
    baton,
    causal,
    demo,
    energy,
    events,
    export,
    metrics,
    missions,
    patches,
    world,
    ws,
)

router = APIRouter()


class HealthResponse(BaseModel):
    ok: bool = True
    service: str = "baton-substrate"
    version: str = "0.1.0"


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


router.include_router(missions.router)
router.include_router(agents.router)
router.include_router(world.router)
router.include_router(patches.router)
router.include_router(baton.router)
router.include_router(causal.router)
router.include_router(energy.router)
router.include_router(events.router)
router.include_router(metrics.router)
router.include_router(export.router)
router.include_router(demo.router)
router.include_router(ws.router)

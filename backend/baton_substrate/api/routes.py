from __future__ import annotations

from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from sqlalchemy import text

from baton_substrate.api.observability import runtime_metrics
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
from baton_substrate.api.security import auth_ready
from baton_substrate.config import settings
import baton_substrate.db.engine as db_engine

router = APIRouter()


class HealthResponse(BaseModel):
    ok: bool = True
    service: str = "baton-substrate"
    version: str = "0.1.0"
    mode: str = "local"
    auth_required: bool = False
    ready: bool = True
    auth_modes: list[str] = []


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        mode=settings.environment,
        auth_required=settings.environment == "production",
        ready=auth_ready(),
        auth_modes=["bearer"],
    )


class ReadyResponse(BaseModel):
    ok: bool
    database: bool
    auth: bool


@router.get("/ready", response_model=ReadyResponse)
async def ready(response: Response) -> ReadyResponse:
    database_ready = True
    try:
        async with db_engine.get_db() as db:
            await db.execute(text("SELECT 1"))
    except Exception:
        database_ready = False

    auth = auth_ready()
    ok = database_ready and auth
    if not ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadyResponse(ok=ok, database=database_ready, auth=auth)


@router.get("/metrics")
async def runtime_metrics_endpoint() -> Response:
    return Response(
        content=runtime_metrics.render_prometheus(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


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

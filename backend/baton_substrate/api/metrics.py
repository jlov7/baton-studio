from __future__ import annotations

from fastapi import APIRouter, Depends

from baton_substrate.api.dependencies import require_existing_mission
import baton_substrate.db.engine as db_engine
from baton_substrate.models.metrics import SCMetricResponse
from baton_substrate.services import metrics_service

router = APIRouter(
    prefix="/missions/{mission_id}/metrics",
    tags=["metrics"],
    dependencies=[Depends(require_existing_mission)],
)


@router.get("/sc", response_model=SCMetricResponse)
async def get_sc_metric(mission_id: str) -> SCMetricResponse:
    async with db_engine.get_db() as db:
        return await metrics_service.compute_sc(db, mission_id)

from __future__ import annotations

from fastapi import APIRouter

from baton_substrate.db import get_db
from baton_substrate.models.metrics import SCMetricResponse
from baton_substrate.services import metrics_service

router = APIRouter(prefix="/missions/{mission_id}/metrics", tags=["metrics"])


@router.get("/sc", response_model=SCMetricResponse)
async def get_sc_metric(mission_id: str) -> SCMetricResponse:
    async with get_db() as db:
        return await metrics_service.compute_sc(db, mission_id)

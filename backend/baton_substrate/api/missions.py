from __future__ import annotations

from fastapi import APIRouter, HTTPException

from baton_substrate.db import get_db
from baton_substrate.models.mission import (
    CreateMissionRequest,
    MissionResponse,
    MissionStatusUpdate,
)
from baton_substrate.services import mission_service

router = APIRouter(prefix="/missions", tags=["missions"])


@router.post("", response_model=MissionResponse)
async def create_mission(req: CreateMissionRequest) -> MissionResponse:
    async with get_db() as db:
        return await mission_service.create_mission(
            db,
            req.title,
            req.goal,
            req.energy_budget,
        )


@router.get("/{mission_id}", response_model=MissionResponse)
async def get_mission(mission_id: str) -> MissionResponse:
    async with get_db() as db:
        m = await mission_service.get_mission(db, mission_id)
        if not m:
            raise HTTPException(status_code=404, detail="Mission not found")
        return m


@router.post("/{mission_id}/status", response_model=MissionResponse)
async def update_status(mission_id: str, req: MissionStatusUpdate) -> MissionResponse:
    async with get_db() as db:
        try:
            return await mission_service.update_status(db, mission_id, req.status)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

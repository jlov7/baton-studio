from __future__ import annotations

from fastapi import APIRouter, Depends

from baton_substrate.api.dependencies import require_existing_mission
import baton_substrate.db.engine as db_engine
from baton_substrate.models.world import EntityTypeSchema, WorldSnapshot
from baton_substrate.services import world_service

router = APIRouter(
    prefix="/missions/{mission_id}",
    tags=["world"],
    dependencies=[Depends(require_existing_mission)],
)


@router.get("/world", response_model=WorldSnapshot)
async def get_world(mission_id: str) -> WorldSnapshot:
    async with db_engine.get_db() as db:
        return await world_service.get_world_snapshot(db, mission_id)


@router.get("/types", response_model=list[EntityTypeSchema])
async def list_types(mission_id: str) -> list[EntityTypeSchema]:
    async with db_engine.get_db() as db:
        return await world_service.list_entity_types(db, mission_id)

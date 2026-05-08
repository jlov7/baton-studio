from __future__ import annotations

from fastapi import HTTPException

import baton_substrate.db.engine as db_engine
from baton_substrate.services import mission_service


async def require_existing_mission(mission_id: str) -> None:
    async with db_engine.get_db() as db:
        if not await mission_service.mission_exists(db, mission_id):
            raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")

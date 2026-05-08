from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from baton_substrate.api.dependencies import require_existing_mission
from baton_substrate.config import settings
import baton_substrate.db.engine as db_engine
from baton_substrate.models.event import EventListResponse
from baton_substrate.services import event_service

router = APIRouter(
    prefix="/missions/{mission_id}/events",
    tags=["events"],
    dependencies=[Depends(require_existing_mission)],
)


@router.get("", response_model=EventListResponse)
async def get_events(
    mission_id: str,
    after: str | None = None,
    type: str | None = None,
    limit: int = Query(default=100, ge=1),
) -> EventListResponse:
    bounded_limit = min(limit, settings.event_page_limit_max)
    async with db_engine.get_db() as db:
        events, cursor = await event_service.query(
            db,
            mission_id,
            after=after,
            event_type=type,
            limit=bounded_limit,
        )
        return EventListResponse(events=events, cursor=cursor)

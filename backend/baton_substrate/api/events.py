from __future__ import annotations

from fastapi import APIRouter

from baton_substrate.db import get_db
from baton_substrate.models.event import EventListResponse, EventQuery
from baton_substrate.services import event_service

router = APIRouter(prefix="/missions/{mission_id}/events", tags=["events"])


@router.get("", response_model=EventListResponse)
async def get_events(
    mission_id: str,
    after: str | None = None,
    type: str | None = None,
    limit: int = 100,
) -> EventListResponse:
    async with get_db() as db:
        events, cursor = await event_service.query(
            db, mission_id, after=after, event_type=type, limit=limit,
        )
        return EventListResponse(events=events, cursor=cursor)

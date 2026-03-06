from __future__ import annotations

from pydantic import BaseModel

from baton_substrate.models.common import EventEnvelope


class EventQuery(BaseModel):
    after: str | None = None
    limit: int = 100
    type: str | None = None


class EventListResponse(BaseModel):
    events: list[EventEnvelope]
    cursor: str | None = None

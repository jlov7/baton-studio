from __future__ import annotations

from pydantic import BaseModel, Field


class ClaimBatonRequest(BaseModel):
    actor_id: str = Field(min_length=1)
    lease_ms: int = Field(default=20_000, gt=0, le=300_000)


class BatonStateResponse(BaseModel):
    holder: str | None
    queue: list[str]
    lease_expires_at: str | None


class ReleaseBatonRequest(BaseModel):
    actor_id: str = Field(min_length=1)

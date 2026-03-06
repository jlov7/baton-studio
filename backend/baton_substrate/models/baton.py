from __future__ import annotations

from pydantic import BaseModel


class ClaimBatonRequest(BaseModel):
    actor_id: str
    lease_ms: int = 20_000


class BatonStateResponse(BaseModel):
    holder: str | None
    queue: list[str]
    lease_expires_at: str | None


class ReleaseBatonRequest(BaseModel):
    actor_id: str

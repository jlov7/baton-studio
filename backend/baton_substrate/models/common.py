from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Actor(BaseModel):
    actor_id: str
    actor_type: Literal["agent", "human", "system"] = "agent"
    display_name: str = ""


class PatchOp(BaseModel):
    op: Literal["upsert", "delete"] = "upsert"
    type: str
    id: str
    value: dict[str, Any] = Field(default_factory=dict)


class Patch(BaseModel):
    ops: list[PatchOp]


class CausalEdgeInput(BaseModel):
    from_id: str = Field(alias="from")
    to_id: str = Field(alias="to")
    type: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class Violation(BaseModel):
    severity: Literal["hard", "soft"]
    code: str
    message: str


class EventEnvelope(BaseModel):
    event_id: str
    ts: str
    mission_id: str
    type: str
    actor: Actor
    payload: dict[str, Any] = Field(default_factory=dict)

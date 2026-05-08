from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AddEdgeRequest(BaseModel):
    actor_id: str = Field(min_length=1)
    from_id: str = Field(min_length=1)
    to_id: str = Field(min_length=1)
    type: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AddEdgeResponse(BaseModel):
    edge_id: str


class CausalNodeDetail(BaseModel):
    node_id: str
    node_type: str
    label: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: str = "valid"


class CausalEdgeDetail(BaseModel):
    edge_id: str
    from_id: str
    to_id: str
    edge_type: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class CausalGraphSnapshot(BaseModel):
    mission_id: str
    nodes: list[CausalNodeDetail]
    edges: list[CausalEdgeDetail]

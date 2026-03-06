from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AddEdgeRequest(BaseModel):
    actor_id: str
    from_id: str
    to_id: str
    type: str
    metadata: dict[str, Any] = {}


class AddEdgeResponse(BaseModel):
    edge_id: str


class CausalNodeDetail(BaseModel):
    node_id: str
    node_type: str
    label: str
    metadata: dict[str, Any] = {}
    status: str = "valid"


class CausalEdgeDetail(BaseModel):
    edge_id: str
    from_id: str
    to_id: str
    edge_type: str
    metadata: dict[str, Any] = {}


class CausalGraphSnapshot(BaseModel):
    mission_id: str
    nodes: list[CausalNodeDetail]
    edges: list[CausalEdgeDetail]

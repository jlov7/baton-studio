from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class EntityTypeSchema(BaseModel):
    type_name: str
    json_schema: dict[str, Any]
    invariants: list[dict[str, Any]]


class EntityVersionDetail(BaseModel):
    version: int
    created_at: str
    actor_id: str
    value: dict[str, Any]


class EntityDetail(BaseModel):
    entity_id: str
    type_name: str
    latest_version: int
    value: dict[str, Any]
    versions: list[EntityVersionDetail] = []


class WorldSnapshot(BaseModel):
    mission_id: str
    entity_types: list[EntityTypeSchema]
    entities: list[EntityDetail]
    pending_proposals: int = 0

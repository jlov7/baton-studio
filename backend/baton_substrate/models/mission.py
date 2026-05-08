from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CreateMissionRequest(BaseModel):
    title: str = Field(min_length=1)
    goal: str = ""
    energy_budget: int = Field(default=1000, gt=0)
    schema_pack: str = "default"


class MissionResponse(BaseModel):
    mission_id: str
    created_at: str
    title: str
    goal: str
    energy_budget: int
    status: str = "idle"


class MissionStatusUpdate(BaseModel):
    status: Literal["idle", "running", "paused", "exported"]

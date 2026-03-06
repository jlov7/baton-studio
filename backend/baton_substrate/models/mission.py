from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class CreateMissionRequest(BaseModel):
    title: str
    goal: str = ""
    energy_budget: int = 1000
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

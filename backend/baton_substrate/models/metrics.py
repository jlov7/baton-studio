from __future__ import annotations

from pydantic import BaseModel, Field


class SCPoint(BaseModel):
    ts: str
    value: float


class SCMetricResponse(BaseModel):
    sc_current: float
    sc_history: list[SCPoint] = Field(default_factory=list)

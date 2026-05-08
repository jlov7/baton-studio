from __future__ import annotations

from pydantic import BaseModel, Field


class EnergyBalanceResponse(BaseModel):
    actor_id: str
    balance: int
    mission_budget: int


class EnergySpendRequest(BaseModel):
    actor_id: str = Field(min_length=1)
    amount: int = Field(gt=0)
    reason: str = ""


class EnergySpendResponse(BaseModel):
    new_balance: int


class EnergyAllocateRequest(BaseModel):
    actor_id: str = Field(min_length=1)
    amount: int = Field(gt=0)

from __future__ import annotations

from pydantic import BaseModel


class EnergyBalanceResponse(BaseModel):
    actor_id: str
    balance: int
    mission_budget: int


class EnergySpendRequest(BaseModel):
    actor_id: str
    amount: int
    reason: str = ""


class EnergySpendResponse(BaseModel):
    new_balance: int


class EnergyAllocateRequest(BaseModel):
    actor_id: str
    amount: int

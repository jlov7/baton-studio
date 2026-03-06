from __future__ import annotations

from pydantic import BaseModel


class RegisterAgentRequest(BaseModel):
    actor_id: str
    display_name: str = ""
    role: str = "agent"


class AgentDetail(BaseModel):
    actor_id: str
    display_name: str
    role: str
    joined_at: str
    last_seen_at: str
    status: str
    energy_balance: int = 0

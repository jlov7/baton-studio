from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AgentProfile:
    actor_id: str
    display_name: str
    role: str


AGENTS = [
    AgentProfile("atlas", "Atlas", "researcher"),
    AgentProfile("meridian", "Meridian", "planner"),
    AgentProfile("sentinel", "Sentinel", "critic"),
    AgentProfile("forge", "Forge", "implementer"),
]

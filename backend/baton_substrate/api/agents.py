from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from baton_substrate.api.dependencies import require_existing_mission
import baton_substrate.db.engine as db_engine
from baton_substrate.models.agent import AgentDetail, RegisterAgentRequest
from baton_substrate.services import agent_service, energy_service

router = APIRouter(
    prefix="/missions/{mission_id}/agents",
    tags=["agents"],
    dependencies=[Depends(require_existing_mission)],
)


@router.get("", response_model=list[AgentDetail])
async def list_agents(mission_id: str) -> list[AgentDetail]:
    async with db_engine.get_db() as db:
        return await agent_service.list_agents(db, mission_id)


@router.post("", response_model=AgentDetail)
async def register_agent(mission_id: str, req: RegisterAgentRequest) -> AgentDetail:
    async with db_engine.get_db() as db:
        try:
            agent = await agent_service.register(
                db,
                mission_id,
                req.actor_id,
                req.display_name,
                req.role,
            )
            await energy_service.auto_allocate(db, mission_id, req.actor_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        bal = await energy_service.get_balance(db, mission_id, req.actor_id)
        agent.energy_balance = bal.balance
        return agent

from __future__ import annotations

from fastapi import APIRouter

from baton_substrate.demo.simulator import run_demo

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/start")
async def start_demo() -> dict[str, str]:
    mission_id = await run_demo(delay=0.1)
    return {"mission_id": mission_id, "status": "completed"}

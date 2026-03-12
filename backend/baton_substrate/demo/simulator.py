from __future__ import annotations

import asyncio

from baton_substrate.db import get_db, init_db
from baton_substrate.demo.agent_behaviors import AGENTS
from baton_substrate.demo.schema_pack import ENTITY_TYPES
from baton_substrate.models.common import Patch, PatchOp
from baton_substrate.services import (
    agent_service,
    baton_service,
    causal_service,
    energy_service,
    mission_service,
    patch_service,
    world_service,
)


class DemoSimulator:
    def __init__(self, delay: float = 0.3) -> None:
        self.delay = delay
        self.mission_id: str = ""

    async def run(self) -> str:
        await init_db()
        async with get_db() as db:
            mission = await mission_service.create_mission(
                db,
                "Substrate-Native Agent Coordination",
                "Design and implement a multi-agent coordination framework",
                1000,
            )
            self.mission_id = mission.mission_id
            await mission_service.update_status(db, self.mission_id, "running")

            for et in ENTITY_TYPES:
                await world_service.register_entity_type(
                    db,
                    self.mission_id,
                    et["type_name"],
                    et["json_schema"],
                    et["invariants"],
                )

            for agent in AGENTS:
                await agent_service.register(
                    db,
                    self.mission_id,
                    agent.actor_id,
                    agent.display_name,
                    agent.role,
                )
                await energy_service.auto_allocate(db, self.mission_id, agent.actor_id)

        await self._step_1_research()
        await self._step_2_planning()
        await self._step_3_contention()
        await self._step_4_critique()
        await self._step_5_implementation()
        await self._step_6_invalidation()
        await self._step_7_energy_depletion()

        return self.mission_id

    async def _pause(self) -> None:
        await asyncio.sleep(self.delay)

    async def _step_1_research(self) -> None:
        """Atlas proposes Evidence entities."""
        async with get_db() as db:
            # Atlas claims baton
            await baton_service.claim(db, self.mission_id, "atlas")
            await self._pause()

            # Propose evidence
            patch = Patch(
                ops=[
                    PatchOp(
                        op="upsert",
                        type="Evidence",
                        id="ev-001",
                        value={
                            "claim": "Multi-agent systems benefit from shared state over message-passing",
                            "source": "coordination-theory-2024",
                            "confidence": 0.85,
                        },
                    ),
                    PatchOp(
                        op="upsert",
                        type="Evidence",
                        id="ev-002",
                        value={
                            "claim": "Causal graphs reduce redundant work by 40%",
                            "source": "agent-efficiency-study",
                            "confidence": 0.72,
                        },
                    ),
                ]
            )
            result = await patch_service.propose(db, self.mission_id, "atlas", patch)
            if result.accepted:
                await patch_service.commit(db, self.mission_id, "atlas", result.proposal_id)

            # Add causal edges
            await causal_service.add_edge(
                db,
                self.mission_id,
                "atlas",
                "ev-001",
                "ev-002",
                "supports",
            )

            await baton_service.release(db, self.mission_id, "atlas")
        await self._pause()

    async def _step_2_planning(self) -> None:
        """Meridian creates PlanSteps based on Evidence."""
        async with get_db() as db:
            await baton_service.claim(db, self.mission_id, "meridian")
            await self._pause()

            patch = Patch(
                ops=[
                    PatchOp(
                        op="upsert",
                        type="PlanStep",
                        id="ps-001",
                        value={
                            "title": "Design shared world model schema",
                            "description": "Define entity types and invariants for the coordination substrate",
                            "status": "active",
                            "priority": 1,
                        },
                    ),
                    PatchOp(
                        op="upsert",
                        type="PlanStep",
                        id="ps-002",
                        value={
                            "title": "Implement causal graph engine",
                            "description": "Build dependency tracking with BFS invalidation",
                            "status": "draft",
                            "priority": 2,
                        },
                    ),
                    PatchOp(
                        op="upsert",
                        type="PlanStep",
                        id="ps-003",
                        value={
                            "title": "Build energy accounting system",
                            "description": "Fair allocation and spend tracking per agent",
                            "status": "draft",
                            "priority": 3,
                        },
                    ),
                ]
            )
            result = await patch_service.propose(db, self.mission_id, "meridian", patch)
            if result.accepted:
                await patch_service.commit(db, self.mission_id, "meridian", result.proposal_id)

            # Causal links: evidence -> plan steps
            await causal_service.add_edge(
                db,
                self.mission_id,
                "meridian",
                "ev-001",
                "ps-001",
                "derived_from",
            )
            await causal_service.add_edge(
                db,
                self.mission_id,
                "meridian",
                "ev-002",
                "ps-002",
                "derived_from",
            )

            await baton_service.release(db, self.mission_id, "meridian")
        await self._pause()

    async def _step_3_contention(self) -> None:
        """Atlas and Sentinel both try to claim the baton — contention."""
        async with get_db() as db:
            await baton_service.claim(db, self.mission_id, "atlas")
            await self._pause()
            # Sentinel tries to claim — gets queued
            await baton_service.claim(db, self.mission_id, "sentinel")
            await self._pause()

            # Atlas proposes more evidence
            patch = Patch(
                ops=[
                    PatchOp(
                        op="upsert",
                        type="Evidence",
                        id="ev-003",
                        value={
                            "claim": "Baton-based write arbitration prevents conflicting updates",
                            "source": "mutex-patterns-survey",
                            "confidence": 0.91,
                        },
                    ),
                ]
            )
            result = await patch_service.propose(db, self.mission_id, "atlas", patch)
            if result.accepted:
                await patch_service.commit(db, self.mission_id, "atlas", result.proposal_id)

            # Atlas releases — Sentinel gets baton automatically
            await baton_service.release(db, self.mission_id, "atlas")
        await self._pause()

    async def _step_4_critique(self) -> None:
        """Sentinel adds contradicting evidence and triggers a hard invariant violation."""
        async with get_db() as db:
            # Sentinel should now hold baton (from contention step)
            state = await baton_service.get_state(db, self.mission_id)
            if state.holder != "sentinel":
                await baton_service.claim(db, self.mission_id, "sentinel")

            # Sentinel adds contradicting evidence
            patch = Patch(
                ops=[
                    PatchOp(
                        op="upsert",
                        type="Evidence",
                        id="ev-004",
                        value={
                            "claim": "Message-passing may outperform shared state in loosely-coupled systems",
                            "source": "distributed-systems-review",
                            "confidence": 0.65,
                        },
                    ),
                ]
            )
            result = await patch_service.propose(db, self.mission_id, "sentinel", patch)
            if result.accepted:
                await patch_service.commit(db, self.mission_id, "sentinel", result.proposal_id)

            # Add contradicts edge
            await causal_service.add_edge(
                db,
                self.mission_id,
                "sentinel",
                "ev-004",
                "ev-001",
                "contradicts",
            )

            # Sentinel tries a patch with hard invariant violation (missing required field)
            bad_patch = Patch(
                ops=[
                    PatchOp(
                        op="upsert",
                        type="PlanStep",
                        id="ps-bad",
                        value={
                            "description": "This plan step is missing a required title",
                            "status": "invalid_status",
                        },
                    ),
                ]
            )
            await patch_service.propose(db, self.mission_id, "sentinel", bad_patch)

            await baton_service.release(db, self.mission_id, "sentinel")
        await self._pause()

    async def _step_5_implementation(self) -> None:
        """Forge creates CodeArtifacts."""
        async with get_db() as db:
            await baton_service.claim(db, self.mission_id, "forge")
            await self._pause()

            patch = Patch(
                ops=[
                    PatchOp(
                        op="upsert",
                        type="CodeArtifact",
                        id="code-001",
                        value={
                            "filename": "world_model.py",
                            "language": "python",
                            "content_hash": "a1b2c3d4e5f6",
                            "lines_of_code": 245,
                            "description": "Core world model with entity types and versioning",
                        },
                    ),
                    PatchOp(
                        op="upsert",
                        type="CodeArtifact",
                        id="code-002",
                        value={
                            "filename": "causal_engine.py",
                            "language": "python",
                            "content_hash": "f6e5d4c3b2a1",
                            "lines_of_code": 180,
                            "description": "Causal graph with BFS invalidation propagation",
                        },
                    ),
                ]
            )
            result = await patch_service.propose(db, self.mission_id, "forge", patch)
            if result.accepted:
                await patch_service.commit(db, self.mission_id, "forge", result.proposal_id)

            # Link code to plan steps
            await causal_service.add_edge(
                db,
                self.mission_id,
                "forge",
                "ps-001",
                "code-001",
                "implemented_by",
            )
            await causal_service.add_edge(
                db,
                self.mission_id,
                "forge",
                "ps-002",
                "code-002",
                "implemented_by",
            )

            # Mark plan step as done
            done_patch = Patch(
                ops=[
                    PatchOp(
                        op="upsert",
                        type="PlanStep",
                        id="ps-001",
                        value={
                            "title": "Design shared world model schema",
                            "description": "Define entity types and invariants for the coordination substrate",
                            "status": "done",
                            "priority": 1,
                        },
                    ),
                ]
            )
            done_result = await patch_service.propose(db, self.mission_id, "forge", done_patch)
            if done_result.accepted:
                await patch_service.commit(db, self.mission_id, "forge", done_result.proposal_id)

            await baton_service.release(db, self.mission_id, "forge")
        await self._pause()

    async def _step_6_invalidation(self) -> None:
        """Atlas updates evidence, triggering causal invalidation cascade."""
        async with get_db() as db:
            await baton_service.claim(db, self.mission_id, "atlas")
            await self._pause()

            # Update ev-001 with new data — triggers downstream invalidation
            patch = Patch(
                ops=[
                    PatchOp(
                        op="upsert",
                        type="Evidence",
                        id="ev-001",
                        value={
                            "claim": "Shared state coordination with causal tracking outperforms pure message-passing by 3x",
                            "source": "updated-coordination-benchmark-2025",
                            "confidence": 0.93,
                        },
                    ),
                ]
            )
            result = await patch_service.propose(db, self.mission_id, "atlas", patch)
            if result.accepted:
                await patch_service.commit(db, self.mission_id, "atlas", result.proposal_id)
                # Trigger invalidation from ev-001 downstream
                await causal_service.invalidate_downstream(
                    db,
                    self.mission_id,
                    "ev-001",
                    "atlas",
                )

            await baton_service.release(db, self.mission_id, "atlas")
        await self._pause()

    async def _step_7_energy_depletion(self) -> None:
        """Forge spends remaining energy on a big commit."""
        async with get_db() as db:
            await baton_service.claim(db, self.mission_id, "forge")
            await self._pause()

            # Large code artifact
            patch = Patch(
                ops=[
                    PatchOp(
                        op="upsert",
                        type="CodeArtifact",
                        id="code-003",
                        value={
                            "filename": "energy_pool.py",
                            "language": "python",
                            "content_hash": "deadbeef1234",
                            "lines_of_code": 320,
                            "description": "Energy accounting with fair allocation and spend tracking",
                        },
                    ),
                ]
            )
            result = await patch_service.propose(db, self.mission_id, "forge", patch)
            if result.accepted:
                await patch_service.commit(db, self.mission_id, "forge", result.proposal_id)

            # Spend a big chunk of energy
            try:
                await energy_service.spend(
                    db,
                    self.mission_id,
                    "forge",
                    150,
                    "large_implementation_effort",
                )
            except ValueError:
                pass

            await baton_service.release(db, self.mission_id, "forge")

            # Add a decision about the architecture
            await baton_service.claim(db, self.mission_id, "meridian")
            decision_patch = Patch(
                ops=[
                    PatchOp(
                        op="upsert",
                        type="Decision",
                        id="dec-001",
                        value={
                            "question": "Should we use shared state or message-passing for coordination?",
                            "resolution": "Shared state with causal tracking",
                            "rationale": "Evidence shows 3x improvement and better transparency",
                            "decided_by": "meridian",
                        },
                    ),
                ]
            )
            dec_result = await patch_service.propose(
                db,
                self.mission_id,
                "meridian",
                decision_patch,
            )
            if dec_result.accepted:
                await patch_service.commit(
                    db,
                    self.mission_id,
                    "meridian",
                    dec_result.proposal_id,
                )

            # Link decision to evidence
            await causal_service.add_edge(
                db,
                self.mission_id,
                "meridian",
                "ev-001",
                "dec-001",
                "supports",
            )
            await causal_service.add_edge(
                db,
                self.mission_id,
                "meridian",
                "ev-003",
                "dec-001",
                "supports",
            )

            await baton_service.release(db, self.mission_id, "meridian")


async def run_demo(delay: float = 0.3) -> str:
    sim = DemoSimulator(delay=delay)
    return await sim.run()

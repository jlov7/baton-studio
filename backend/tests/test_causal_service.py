"""Tests for causal graph operations and invalidation."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.db.schema import MissionRow
from baton_substrate.services import causal_service


async def _seed_mission(db: AsyncSession, mid: str = "mis_test") -> str:
    db.add(
        MissionRow(
            mission_id=mid,
            created_at=datetime.now(timezone.utc).isoformat(),
            title="Test",
            goal="",
            energy_budget=1000,
            status="idle",
        )
    )
    await db.flush()
    return mid


async def test_ensure_node_creates(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    await causal_service.ensure_node(db, mid, "node-1", "evidence", "Evidence 1")
    graph = await causal_service.get_graph(db, mid)
    assert len(graph.nodes) == 1
    assert graph.nodes[0].node_id == "node-1"
    assert graph.nodes[0].status == "valid"


async def test_ensure_node_idempotent(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    await causal_service.ensure_node(db, mid, "node-1", "evidence", "A")
    await causal_service.ensure_node(db, mid, "node-1", "evidence", "B")
    graph = await causal_service.get_graph(db, mid)
    assert len(graph.nodes) == 1


async def test_add_edge_auto_creates_nodes(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    result = await causal_service.add_edge(db, mid, "agent-a", "n1", "n2", "supports")
    assert result.edge_id.startswith("edg_")
    graph = await causal_service.get_graph(db, mid)
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1


async def test_get_graph_empty(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    graph = await causal_service.get_graph(db, mid)
    assert graph.mission_id == mid
    assert graph.nodes == []
    assert graph.edges == []


async def test_invalidate_downstream_linear(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    # A -> B -> C
    await causal_service.add_edge(db, mid, "a", "A", "B", "depends_on")
    await causal_service.add_edge(db, mid, "a", "B", "C", "depends_on")
    invalidated = await causal_service.invalidate_downstream(db, mid, "A", "a")
    assert set(invalidated) == {"B", "C"}
    graph = await causal_service.get_graph(db, mid)
    statuses = {n.node_id: n.status for n in graph.nodes}
    assert statuses["A"] == "valid"
    assert statuses["B"] == "stale"
    assert statuses["C"] == "stale"


async def test_invalidate_downstream_branching(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    # A -> B, A -> C, B -> D
    await causal_service.add_edge(db, mid, "a", "A", "B", "depends_on")
    await causal_service.add_edge(db, mid, "a", "A", "C", "depends_on")
    await causal_service.add_edge(db, mid, "a", "B", "D", "depends_on")
    invalidated = await causal_service.invalidate_downstream(db, mid, "A", "a")
    assert set(invalidated) == {"B", "C", "D"}


async def test_invalidate_no_downstream(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    await causal_service.ensure_node(db, mid, "lone", "evidence")
    invalidated = await causal_service.invalidate_downstream(db, mid, "lone", "a")
    assert invalidated == []


async def test_invalidate_handles_cycles(db: AsyncSession) -> None:
    mid = await _seed_mission(db)
    # A -> B -> C -> A (cycle)
    await causal_service.add_edge(db, mid, "a", "A", "B", "depends_on")
    await causal_service.add_edge(db, mid, "a", "B", "C", "depends_on")
    await causal_service.add_edge(db, mid, "a", "C", "A", "depends_on")
    invalidated = await causal_service.invalidate_downstream(db, mid, "A", "a")
    assert set(invalidated) == {"B", "C"}

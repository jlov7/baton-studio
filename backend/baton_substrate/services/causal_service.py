from __future__ import annotations

import json
import uuid
from collections import defaultdict, deque
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.db.schema import CausalEdgeRow, CausalNodeRow
from baton_substrate.models.causal import (
    AddEdgeResponse,
    CausalEdgeDetail,
    CausalGraphSnapshot,
    CausalNodeDetail,
)
from baton_substrate.models.common import Actor
from baton_substrate.services import event_service


async def ensure_node(
    db: AsyncSession,
    mission_id: str,
    node_id: str,
    node_type: str = "entity",
    label: str = "",
    metadata: dict[str, Any] | None = None,
) -> None:
    result = await db.execute(
        select(CausalNodeRow).where(
            CausalNodeRow.mission_id == mission_id,
            CausalNodeRow.node_id == node_id,
        )
    )
    if result.scalar_one_or_none():
        return
    row = CausalNodeRow(
        mission_id=mission_id,
        node_id=node_id,
        node_type=node_type,
        label=label or node_id,
        metadata_json=json.dumps(metadata or {}),
        status="valid",
    )
    db.add(row)
    await db.flush()


async def add_edge(
    db: AsyncSession,
    mission_id: str,
    actor_id: str,
    from_id: str,
    to_id: str,
    edge_type: str,
    metadata: dict[str, Any] | None = None,
) -> AddEdgeResponse:
    await ensure_node(db, mission_id, from_id)
    await ensure_node(db, mission_id, to_id)

    edge_id = f"edg_{uuid.uuid4().hex[:12]}"
    row = CausalEdgeRow(
        mission_id=mission_id,
        edge_id=edge_id,
        from_id=from_id,
        to_id=to_id,
        edge_type=edge_type,
        metadata_json=json.dumps(metadata or {}),
    )
    db.add(row)
    await db.flush()

    actor = Actor(actor_id=actor_id, actor_type="agent", display_name=actor_id)
    await event_service.emit(
        db,
        mission_id,
        "causal.edge_added",
        actor,
        {"edge_id": edge_id, "from": from_id, "to": to_id, "type": edge_type},
    )

    return AddEdgeResponse(edge_id=edge_id)


async def get_graph(db: AsyncSession, mission_id: str) -> CausalGraphSnapshot:
    node_result = await db.execute(
        select(CausalNodeRow).where(CausalNodeRow.mission_id == mission_id)
    )
    edge_result = await db.execute(
        select(CausalEdgeRow).where(CausalEdgeRow.mission_id == mission_id)
    )
    nodes = [
        CausalNodeDetail(
            node_id=n.node_id,
            node_type=n.node_type,
            label=n.label,
            metadata=json.loads(n.metadata_json),
            status=n.status,
        )
        for n in node_result.scalars().all()
    ]
    edges = [
        CausalEdgeDetail(
            edge_id=e.edge_id,
            from_id=e.from_id,
            to_id=e.to_id,
            edge_type=e.edge_type,
            metadata=json.loads(e.metadata_json),
        )
        for e in edge_result.scalars().all()
    ]
    return CausalGraphSnapshot(mission_id=mission_id, nodes=nodes, edges=edges)


async def invalidate_downstream(
    db: AsyncSession,
    mission_id: str,
    start_node_id: str,
    actor_id: str,
) -> list[str]:
    edge_result = await db.execute(
        select(CausalEdgeRow).where(CausalEdgeRow.mission_id == mission_id)
    )
    edges = edge_result.scalars().all()

    adjacency: dict[str, list[str]] = defaultdict(list)
    for e in edges:
        adjacency[e.from_id].append(e.to_id)

    visited: set[str] = set()
    queue: deque[str] = deque([start_node_id])
    invalidated: list[str] = []

    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        if current != start_node_id:
            invalidated.append(current)
        for neighbor in adjacency.get(current, []):
            if neighbor not in visited:
                queue.append(neighbor)

    if invalidated:
        for node_id in invalidated:
            node_result = await db.execute(
                select(CausalNodeRow).where(
                    CausalNodeRow.mission_id == mission_id,
                    CausalNodeRow.node_id == node_id,
                )
            )
            node = node_result.scalar_one_or_none()
            if node:
                node.status = "stale"
        await db.flush()

        actor = Actor(actor_id=actor_id, actor_type="agent", display_name=actor_id)
        await event_service.emit(
            db,
            mission_id,
            "causal.invalidated",
            actor,
            {"source": start_node_id, "invalidated": invalidated},
        )

    return invalidated

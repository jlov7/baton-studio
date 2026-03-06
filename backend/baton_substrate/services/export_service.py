from __future__ import annotations

import io
import json
import zipfile
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.db.schema import (
    CausalEdgeRow,
    CausalNodeRow,
    EnergyAccountRow,
    EntityRow,
    EntityTypeRow,
    EntityVersionRow,
    EventRow,
    MissionRow,
    PatchRow,
)


async def export_mission_pack(db: AsyncSession, mission_id: str) -> bytes:
    result = await db.execute(select(MissionRow).where(MissionRow.mission_id == mission_id))
    mission = result.scalar_one_or_none()
    if not mission:
        raise ValueError(f"Mission {mission_id} not found")

    pack: dict[str, Any] = {
        "mission": {
            "mission_id": mission.mission_id,
            "title": mission.title,
            "goal": mission.goal,
            "energy_budget": mission.energy_budget,
            "status": mission.status,
            "created_at": mission.created_at,
        }
    }

    types_result = await db.execute(
        select(EntityTypeRow).where(EntityTypeRow.mission_id == mission_id)
    )
    pack["entity_types"] = [
        {"type_name": t.type_name, "json_schema": json.loads(t.json_schema), "invariants": json.loads(t.invariants_json)}
        for t in types_result.scalars().all()
    ]

    entities_result = await db.execute(
        select(EntityRow).where(EntityRow.mission_id == mission_id)
    )
    pack["entities"] = [
        {"entity_id": e.entity_id, "type_name": e.type_name}
        for e in entities_result.scalars().all()
    ]

    versions_result = await db.execute(
        select(EntityVersionRow).where(EntityVersionRow.mission_id == mission_id)
        .order_by(EntityVersionRow.entity_id, EntityVersionRow.version)
    )
    pack["entity_versions"] = [
        {
            "entity_id": v.entity_id, "version": v.version,
            "created_at": v.created_at, "actor_id": v.actor_id,
            "value": json.loads(v.value_json),
        }
        for v in versions_result.scalars().all()
    ]

    patches_result = await db.execute(
        select(PatchRow).where(PatchRow.mission_id == mission_id)
    )
    pack["patches"] = [
        {
            "proposal_id": p.proposal_id, "actor_id": p.actor_id,
            "created_at": p.created_at, "status": p.status,
            "patch": json.loads(p.patch_json),
            "violations": json.loads(p.violations_json),
        }
        for p in patches_result.scalars().all()
    ]

    nodes_result = await db.execute(
        select(CausalNodeRow).where(CausalNodeRow.mission_id == mission_id)
    )
    pack["causal_nodes"] = [
        {
            "node_id": n.node_id, "node_type": n.node_type,
            "label": n.label, "status": n.status,
            "metadata": json.loads(n.metadata_json),
        }
        for n in nodes_result.scalars().all()
    ]

    edges_result = await db.execute(
        select(CausalEdgeRow).where(CausalEdgeRow.mission_id == mission_id)
    )
    pack["causal_edges"] = [
        {
            "edge_id": e.edge_id, "from_id": e.from_id,
            "to_id": e.to_id, "edge_type": e.edge_type,
            "metadata": json.loads(e.metadata_json),
        }
        for e in edges_result.scalars().all()
    ]

    energy_result = await db.execute(
        select(EnergyAccountRow).where(EnergyAccountRow.mission_id == mission_id)
    )
    pack["energy_accounts"] = [
        {"actor_id": a.actor_id, "balance": a.balance}
        for a in energy_result.scalars().all()
    ]

    events_result = await db.execute(
        select(EventRow).where(EventRow.mission_id == mission_id).order_by(EventRow.ts)
    )
    pack["events"] = [
        {
            "event_id": ev.event_id, "ts": ev.ts, "type": ev.type,
            "actor": json.loads(ev.actor_json),
            "payload": json.loads(ev.payload_json) if ev.payload_json else {},
        }
        for ev in events_result.scalars().all()
    ]

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mission_pack.json", json.dumps(pack, indent=2))
    return buf.getvalue()


async def import_mission_pack(db: AsyncSession, data: bytes) -> str:
    buf = io.BytesIO(data)
    with zipfile.ZipFile(buf, "r") as zf:
        pack = json.loads(zf.read("mission_pack.json"))

    m = pack["mission"]
    mission = MissionRow(
        mission_id=m["mission_id"],
        created_at=m["created_at"],
        title=m["title"],
        goal=m["goal"],
        energy_budget=m["energy_budget"],
        status=m.get("status", "exported"),
    )
    db.add(mission)

    for t in pack.get("entity_types", []):
        db.add(EntityTypeRow(
            mission_id=m["mission_id"],
            type_name=t["type_name"],
            json_schema=json.dumps(t["json_schema"]),
            invariants_json=json.dumps(t["invariants"]),
        ))

    for e in pack.get("entities", []):
        db.add(EntityRow(
            mission_id=m["mission_id"],
            entity_id=e["entity_id"],
            type_name=e["type_name"],
        ))

    for v in pack.get("entity_versions", []):
        db.add(EntityVersionRow(
            mission_id=m["mission_id"],
            entity_id=v["entity_id"],
            version=v["version"],
            created_at=v["created_at"],
            actor_id=v["actor_id"],
            value_json=json.dumps(v["value"]),
        ))

    for p in pack.get("patches", []):
        db.add(PatchRow(
            proposal_id=p["proposal_id"],
            mission_id=m["mission_id"],
            created_at=p["created_at"],
            actor_id=p["actor_id"],
            patch_json=json.dumps(p["patch"]),
            violations_json=json.dumps(p["violations"]),
            status=p["status"],
        ))

    for n in pack.get("causal_nodes", []):
        db.add(CausalNodeRow(
            mission_id=m["mission_id"],
            node_id=n["node_id"],
            node_type=n["node_type"],
            label=n["label"],
            metadata_json=json.dumps(n["metadata"]),
            status=n.get("status", "valid"),
        ))

    for e in pack.get("causal_edges", []):
        db.add(CausalEdgeRow(
            mission_id=m["mission_id"],
            edge_id=e["edge_id"],
            from_id=e["from_id"],
            to_id=e["to_id"],
            edge_type=e["edge_type"],
            metadata_json=json.dumps(e["metadata"]),
        ))

    for a in pack.get("energy_accounts", []):
        db.add(EnergyAccountRow(
            mission_id=m["mission_id"],
            actor_id=a["actor_id"],
            balance=a["balance"],
        ))

    from baton_substrate.db.schema import BatonStateRow
    db.add(BatonStateRow(mission_id=m["mission_id"]))

    await db.flush()
    return m["mission_id"]

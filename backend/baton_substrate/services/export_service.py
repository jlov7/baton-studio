from __future__ import annotations

import io
import json
import uuid
import zipfile
from collections.abc import Mapping
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.config import settings
from baton_substrate.db.schema import (
    AgentRow,
    BatonStateRow,
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
from baton_substrate.services.event_service import parse_payload

MISSION_PACK_SCHEMA_VERSION = 1


class MissionPackError(ValueError):
    pass


class DuplicateMissionError(MissionPackError):
    pass


def _load_json(value: str) -> Any:
    return json.loads(value) if value else {}


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise MissionPackError(f"Mission pack {label} must be an object")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise MissionPackError(f"Mission pack {label} must be an array")
    return value


def _pack_list(pack: Mapping[str, Any], key: str) -> list[Any]:
    return _list(pack.get(key, []), key)


def _required_str(value: Mapping[str, Any], key: str, label: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise MissionPackError(f"Mission pack {label}.{key} must be a non-empty string")
    return item


def _optional_str(value: Mapping[str, Any], key: str, label: str) -> str | None:
    item = value.get(key)
    if item is None:
        return None
    if not isinstance(item, str):
        raise MissionPackError(f"Mission pack {label}.{key} must be a string")
    return item


def _str_with_default(
    value: Mapping[str, Any],
    key: str,
    label: str,
    default: str,
    *,
    allow_empty: bool = False,
) -> str:
    item = value.get(key, default)
    if not isinstance(item, str) or (not allow_empty and not item):
        raise MissionPackError(f"Mission pack {label}.{key} must be a non-empty string")
    return item


def _required_int(value: Mapping[str, Any], key: str, label: str) -> int:
    item = value.get(key)
    if not isinstance(item, int):
        raise MissionPackError(f"Mission pack {label}.{key} must be an integer")
    return item


def _object_field(value: Mapping[str, Any], key: str, label: str) -> Mapping[str, Any]:
    return _mapping(value.get(key, {}), f"{label}.{key}")


def _array_field(value: Mapping[str, Any], key: str, label: str) -> list[Any]:
    return _list(value.get(key, []), f"{label}.{key}")


def _read_pack(data: bytes) -> dict[str, Any]:
    try:
        with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
            names = set(zf.namelist())
            if names != {"mission_pack.json"}:
                raise MissionPackError("Mission pack must contain only mission_pack.json")
            info = zf.getinfo("mission_pack.json")
            if info.flag_bits & 0x1:
                raise MissionPackError("Encrypted mission packs are not supported")
            if info.file_size > settings.max_mission_pack_bytes:
                raise MissionPackError("Mission pack JSON exceeds upload size limit")
            raw = zf.read("mission_pack.json")
    except zipfile.BadZipFile as exc:
        raise MissionPackError("Mission pack is not a valid zip file") from exc
    except KeyError as exc:
        raise MissionPackError("Mission pack missing mission_pack.json") from exc

    try:
        pack = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise MissionPackError("Mission pack JSON is malformed") from exc

    if not isinstance(pack, dict):
        raise MissionPackError("Mission pack root must be an object")
    if "mission" not in pack or not isinstance(pack["mission"], dict):
        raise MissionPackError("Mission pack missing mission object")
    schema_version = pack.get("schema_version", 0)
    if not isinstance(schema_version, int):
        raise MissionPackError("Mission pack schema_version must be an integer")
    if schema_version not in (0, MISSION_PACK_SCHEMA_VERSION):
        raise MissionPackError(f"Unsupported mission pack schema_version {schema_version}")
    return pack


async def export_mission_pack(db: AsyncSession, mission_id: str) -> bytes:
    result = await db.execute(select(MissionRow).where(MissionRow.mission_id == mission_id))
    mission = result.scalar_one_or_none()
    if not mission:
        raise ValueError(f"Mission {mission_id} not found")

    pack: dict[str, Any] = {
        "schema_version": MISSION_PACK_SCHEMA_VERSION,
        "mission": {
            "mission_id": mission.mission_id,
            "title": mission.title,
            "goal": mission.goal,
            "energy_budget": mission.energy_budget,
            "status": mission.status,
            "created_at": mission.created_at,
        },
    }

    types_result = await db.execute(
        select(EntityTypeRow).where(EntityTypeRow.mission_id == mission_id)
    )
    pack["entity_types"] = [
        {
            "type_name": t.type_name,
            "json_schema": _load_json(t.json_schema),
            "invariants": _load_json(t.invariants_json),
        }
        for t in types_result.scalars().all()
    ]

    entities_result = await db.execute(select(EntityRow).where(EntityRow.mission_id == mission_id))
    pack["entities"] = [
        {
            "entity_id": e.entity_id,
            "type_name": e.type_name,
            "deleted_at": e.deleted_at,
            "deleted_by": e.deleted_by,
        }
        for e in entities_result.scalars().all()
    ]

    baton_result = await db.execute(
        select(BatonStateRow).where(BatonStateRow.mission_id == mission_id)
    )
    baton = baton_result.scalar_one_or_none()
    pack["baton_state"] = {
        "holder_actor_id": baton.holder_actor_id if baton else None,
        "queue": _load_json(baton.queue_json) if baton else [],
        "lease_expires_at": baton.lease_expires_at if baton else None,
    }

    agents_result = await db.execute(select(AgentRow).where(AgentRow.mission_id == mission_id))
    pack["agents"] = [
        {
            "actor_id": a.actor_id,
            "display_name": a.display_name,
            "role": a.role,
            "joined_at": a.joined_at,
            "last_seen_at": a.last_seen_at,
            "status": a.status,
        }
        for a in agents_result.scalars().all()
    ]

    versions_result = await db.execute(
        select(EntityVersionRow)
        .where(EntityVersionRow.mission_id == mission_id)
        .order_by(EntityVersionRow.entity_id, EntityVersionRow.version)
    )
    pack["entity_versions"] = [
        {
            "entity_id": v.entity_id,
            "version": v.version,
            "created_at": v.created_at,
            "actor_id": v.actor_id,
            "value": _load_json(v.value_json),
        }
        for v in versions_result.scalars().all()
    ]

    patches_result = await db.execute(select(PatchRow).where(PatchRow.mission_id == mission_id))
    pack["patches"] = [
        {
            "proposal_id": p.proposal_id,
            "actor_id": p.actor_id,
            "created_at": p.created_at,
            "status": p.status,
            "patch": _load_json(p.patch_json),
            "violations": _load_json(p.violations_json),
        }
        for p in patches_result.scalars().all()
    ]

    nodes_result = await db.execute(
        select(CausalNodeRow).where(CausalNodeRow.mission_id == mission_id)
    )
    pack["causal_nodes"] = [
        {
            "node_id": n.node_id,
            "node_type": n.node_type,
            "label": n.label,
            "status": n.status,
            "metadata": _load_json(n.metadata_json),
        }
        for n in nodes_result.scalars().all()
    ]

    edges_result = await db.execute(
        select(CausalEdgeRow).where(CausalEdgeRow.mission_id == mission_id)
    )
    pack["causal_edges"] = [
        {
            "edge_id": e.edge_id,
            "from_id": e.from_id,
            "to_id": e.to_id,
            "edge_type": e.edge_type,
            "metadata": _load_json(e.metadata_json),
        }
        for e in edges_result.scalars().all()
    ]

    energy_result = await db.execute(
        select(EnergyAccountRow).where(EnergyAccountRow.mission_id == mission_id)
    )
    pack["energy_accounts"] = [
        {"actor_id": a.actor_id, "balance": a.balance} for a in energy_result.scalars().all()
    ]

    events_result = await db.execute(
        select(EventRow).where(EventRow.mission_id == mission_id).order_by(EventRow.ts)
    )
    pack["events"] = [
        {
            "event_id": ev.event_id,
            "ts": ev.ts,
            "type": ev.type,
            "actor": _load_json(ev.actor_json),
            "payload": parse_payload(ev.payload_json),
        }
        for ev in events_result.scalars().all()
    ]

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mission_pack.json", json.dumps(pack, indent=2))
    return buf.getvalue()


async def import_mission_pack(db: AsyncSession, data: bytes) -> str:
    pack = _read_pack(data)
    m = _mapping(pack["mission"], "mission")
    mission_id = _required_str(m, "mission_id", "mission")
    energy_budget = _required_int(m, "energy_budget", "mission")
    if energy_budget <= 0:
        raise MissionPackError("Mission pack mission.energy_budget must be positive")

    existing = await db.execute(select(MissionRow).where(MissionRow.mission_id == mission_id))
    if existing.scalar_one_or_none():
        raise DuplicateMissionError(f"Mission {mission_id} already exists")

    mission = MissionRow(
        mission_id=mission_id,
        created_at=_required_str(m, "created_at", "mission"),
        title=_required_str(m, "title", "mission"),
        goal=_str_with_default(m, "goal", "mission", "", allow_empty=True),
        energy_budget=energy_budget,
        status=_str_with_default(m, "status", "mission", "exported"),
    )
    db.add(mission)

    for index, raw_type in enumerate(_pack_list(pack, "entity_types")):
        t = _mapping(raw_type, f"entity_types[{index}]")
        db.add(
            EntityTypeRow(
                mission_id=mission_id,
                type_name=_required_str(t, "type_name", f"entity_types[{index}]"),
                json_schema=json.dumps(_object_field(t, "json_schema", f"entity_types[{index}]")),
                invariants_json=json.dumps(_array_field(t, "invariants", f"entity_types[{index}]")),
            )
        )

    for index, raw_entity in enumerate(_pack_list(pack, "entities")):
        e = _mapping(raw_entity, f"entities[{index}]")
        db.add(
            EntityRow(
                mission_id=mission_id,
                entity_id=_required_str(e, "entity_id", f"entities[{index}]"),
                type_name=_required_str(e, "type_name", f"entities[{index}]"),
                deleted_at=_optional_str(e, "deleted_at", f"entities[{index}]"),
                deleted_by=_optional_str(e, "deleted_by", f"entities[{index}]"),
            )
        )

    for index, raw_agent in enumerate(_pack_list(pack, "agents")):
        a = _mapping(raw_agent, f"agents[{index}]")
        actor_id = _required_str(a, "actor_id", f"agents[{index}]")
        db.add(
            AgentRow(
                mission_id=mission_id,
                actor_id=actor_id,
                display_name=_str_with_default(a, "display_name", f"agents[{index}]", actor_id),
                role=_str_with_default(a, "role", f"agents[{index}]", "agent"),
                joined_at=_required_str(a, "joined_at", f"agents[{index}]"),
                last_seen_at=_required_str(a, "last_seen_at", f"agents[{index}]"),
                status=_str_with_default(a, "status", f"agents[{index}]", "active"),
            )
        )

    for index, raw_version in enumerate(_pack_list(pack, "entity_versions")):
        v = _mapping(raw_version, f"entity_versions[{index}]")
        db.add(
            EntityVersionRow(
                mission_id=mission_id,
                entity_id=_required_str(v, "entity_id", f"entity_versions[{index}]"),
                version=_required_int(v, "version", f"entity_versions[{index}]"),
                created_at=_required_str(v, "created_at", f"entity_versions[{index}]"),
                actor_id=_required_str(v, "actor_id", f"entity_versions[{index}]"),
                value_json=json.dumps(_object_field(v, "value", f"entity_versions[{index}]")),
            )
        )

    for index, raw_patch in enumerate(_pack_list(pack, "patches")):
        p = _mapping(raw_patch, f"patches[{index}]")
        db.add(
            PatchRow(
                proposal_id=_required_str(p, "proposal_id", f"patches[{index}]"),
                mission_id=mission_id,
                created_at=_required_str(p, "created_at", f"patches[{index}]"),
                actor_id=_required_str(p, "actor_id", f"patches[{index}]"),
                patch_json=json.dumps(_object_field(p, "patch", f"patches[{index}]")),
                violations_json=json.dumps(_array_field(p, "violations", f"patches[{index}]")),
                status=_required_str(p, "status", f"patches[{index}]"),
            )
        )

    for index, raw_node in enumerate(_pack_list(pack, "causal_nodes")):
        n = _mapping(raw_node, f"causal_nodes[{index}]")
        db.add(
            CausalNodeRow(
                mission_id=mission_id,
                node_id=_required_str(n, "node_id", f"causal_nodes[{index}]"),
                node_type=_required_str(n, "node_type", f"causal_nodes[{index}]"),
                label=_required_str(n, "label", f"causal_nodes[{index}]"),
                metadata_json=json.dumps(_object_field(n, "metadata", f"causal_nodes[{index}]")),
                status=_str_with_default(n, "status", f"causal_nodes[{index}]", "valid"),
            )
        )

    for index, raw_edge in enumerate(_pack_list(pack, "causal_edges")):
        e = _mapping(raw_edge, f"causal_edges[{index}]")
        db.add(
            CausalEdgeRow(
                mission_id=mission_id,
                edge_id=_required_str(e, "edge_id", f"causal_edges[{index}]"),
                from_id=_required_str(e, "from_id", f"causal_edges[{index}]"),
                to_id=_required_str(e, "to_id", f"causal_edges[{index}]"),
                edge_type=_required_str(e, "edge_type", f"causal_edges[{index}]"),
                metadata_json=json.dumps(_object_field(e, "metadata", f"causal_edges[{index}]")),
            )
        )

    for index, raw_account in enumerate(_pack_list(pack, "energy_accounts")):
        a = _mapping(raw_account, f"energy_accounts[{index}]")
        balance = _required_int(a, "balance", f"energy_accounts[{index}]")
        if balance < 0:
            raise MissionPackError(f"Mission pack energy_accounts[{index}].balance must be >= 0")
        db.add(
            EnergyAccountRow(
                mission_id=mission_id,
                actor_id=_required_str(a, "actor_id", f"energy_accounts[{index}]"),
                balance=balance,
            )
        )

    baton = _mapping(pack.get("baton_state", {}), "baton_state")
    queue = _array_field(baton, "queue", "baton_state")
    if any(not isinstance(actor_id, str) or not actor_id for actor_id in queue):
        raise MissionPackError("Mission pack baton_state.queue must contain actor IDs")
    db.add(
        BatonStateRow(
            mission_id=mission_id,
            holder_actor_id=_optional_str(baton, "holder_actor_id", "baton_state"),
            queue_json=json.dumps(queue),
            lease_expires_at=_optional_str(baton, "lease_expires_at", "baton_state"),
        )
    )

    for index, raw_event in enumerate(_pack_list(pack, "events")):
        ev = _mapping(raw_event, f"events[{index}]")
        event_id = (
            _optional_str(ev, "event_id", f"events[{index}]") or f"evt_{uuid.uuid4().hex[:12]}"
        )
        db.add(
            EventRow(
                event_id=event_id,
                mission_id=mission_id,
                ts=_required_str(ev, "ts", f"events[{index}]"),
                type=_required_str(ev, "type", f"events[{index}]"),
                actor_json=json.dumps(_object_field(ev, "actor", f"events[{index}]")),
                payload_json=json.dumps(_object_field(ev, "payload", f"events[{index}]")),
            )
        )

    await db.flush()
    return mission_id

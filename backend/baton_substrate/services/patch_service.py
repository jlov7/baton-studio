from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.db.schema import PatchRow
from baton_substrate.invariants.builtin import check_required_id, check_type_registered
from baton_substrate.invariants.engine import check_patch_op
from baton_substrate.models.common import Actor, Patch, Violation
from baton_substrate.models.patch import CommitPatchResponse, ProposePatchResponse
from baton_substrate.services import event_service, world_service


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def propose(
    db: AsyncSession,
    mission_id: str,
    actor_id: str,
    patch: Patch,
) -> ProposePatchResponse:
    proposal_id = f"prop_{uuid.uuid4().hex[:12]}"
    all_violations: list[Violation] = []

    types = await world_service.list_entity_types(db, mission_id)
    type_map = {t.type_name: t for t in types}
    registered = set(type_map.keys())

    for op in patch.ops:
        all_violations.extend(check_required_id(op.value, op.id))
        all_violations.extend(check_type_registered(op.type, registered))

        if op.op == "upsert" and op.type in type_map:
            et = type_map[op.type]
            all_violations.extend(check_patch_op(op.value, et.json_schema, et.invariants))

    has_hard = any(v.severity == "hard" for v in all_violations)
    status = "rejected" if has_hard else "pending"
    accepted = not has_hard

    row = PatchRow(
        proposal_id=proposal_id,
        mission_id=mission_id,
        created_at=_now(),
        actor_id=actor_id,
        patch_json=patch.model_dump_json(),
        violations_json=json.dumps([v.model_dump() for v in all_violations]),
        status=status,
    )
    db.add(row)
    await db.flush()

    actor = Actor(actor_id=actor_id, actor_type="agent", display_name=actor_id)
    event_type = "patch.proposed" if accepted else "patch.rejected"
    await event_service.emit(
        db,
        mission_id,
        event_type,
        actor,
        {
            "proposal_id": proposal_id,
            "accepted": accepted,
            "violations": [v.model_dump() for v in all_violations],
            "ops_count": len(patch.ops),
        },
    )

    return ProposePatchResponse(
        proposal_id=proposal_id,
        accepted=accepted,
        violations=all_violations,
    )


async def commit(
    db: AsyncSession,
    mission_id: str,
    actor_id: str,
    proposal_id: str,
) -> CommitPatchResponse:
    result = await db.execute(
        select(PatchRow).where(
            PatchRow.proposal_id == proposal_id,
            PatchRow.mission_id == mission_id,
        )
    )
    row = result.scalar_one_or_none()
    if not row:
        return CommitPatchResponse(committed=False, message="Proposal not found")
    if row.status != "pending":
        return CommitPatchResponse(
            committed=False, message=f"Proposal status is '{row.status}', expected 'pending'"
        )

    patch_data = json.loads(row.patch_json)
    patch = Patch(**patch_data)

    new_versions: list[dict[str, Any]] = []
    for op in patch.ops:
        if op.op == "upsert":
            version = await world_service.upsert_entity(
                db,
                mission_id,
                op.id,
                op.type,
                op.value,
                actor_id,
            )
            new_versions.append({"entity_id": op.id, "type": op.type, "version": version})
        elif op.op == "delete":
            deleted = await world_service.delete_entity(db, mission_id, op.id, actor_id)
            if deleted:
                new_versions.append({"entity_id": op.id, "type": op.type, "deleted": True})

    row.status = "committed"
    await db.flush()

    actor = Actor(actor_id=actor_id, actor_type="agent", display_name=actor_id)
    await event_service.emit(
        db,
        mission_id,
        "patch.committed",
        actor,
        {"proposal_id": proposal_id, "new_versions": new_versions},
    )

    return CommitPatchResponse(
        committed=True,
        new_versions=new_versions,
        message="Patch committed successfully",
    )


async def estimate_commit_energy_cost(
    db: AsyncSession,
    mission_id: str,
    proposal_id: str,
) -> int:
    result = await db.execute(
        select(PatchRow).where(
            PatchRow.proposal_id == proposal_id,
            PatchRow.mission_id == mission_id,
        )
    )
    row = result.scalar_one_or_none()
    if not row or row.status != "pending":
        return 0
    patch = Patch(**json.loads(row.patch_json))
    return len(patch.ops) * 10

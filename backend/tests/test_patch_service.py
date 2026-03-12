"""Tests for patch propose and commit flow with invariant checks."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.db.schema import BatonStateRow, MissionRow
from baton_substrate.models.common import Patch, PatchOp
from baton_substrate.services import patch_service, world_service


async def _seed(db: AsyncSession, mid: str = "mis_test") -> str:
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
    db.add(BatonStateRow(mission_id=mid, holder_actor_id=None, queue_json="[]"))
    await db.flush()
    await world_service.register_entity_type(
        db,
        mid,
        "Evidence",
        json_schema={
            "type": "object",
            "properties": {"claim": {"type": "string"}},
            "required": ["claim"],
        },
        invariants=[{"rule": "required_fields", "fields": ["claim"], "severity": "hard"}],
    )
    return mid


async def test_propose_valid_patch(db: AsyncSession) -> None:
    mid = await _seed(db)
    patch = Patch(
        ops=[PatchOp(op="upsert", type="Evidence", id="ev-1", value={"claim": "Earth is round"})]
    )
    result = await patch_service.propose(db, mid, "agent-a", patch)
    assert result.accepted is True
    assert result.violations == []
    assert result.proposal_id.startswith("prop_")


async def test_propose_hard_violation_rejected(db: AsyncSession) -> None:
    mid = await _seed(db)
    patch = Patch(ops=[PatchOp(op="upsert", type="Evidence", id="ev-1", value={})])
    result = await patch_service.propose(db, mid, "agent-a", patch)
    assert result.accepted is False
    hard = [v for v in result.violations if v.severity == "hard"]
    assert len(hard) >= 1


async def test_propose_unknown_type_rejected(db: AsyncSession) -> None:
    mid = await _seed(db)
    patch = Patch(ops=[PatchOp(op="upsert", type="Unknown", id="x-1", value={"name": "test"})])
    result = await patch_service.propose(db, mid, "agent-a", patch)
    assert result.accepted is False
    assert any(v.code == "unknown_type" for v in result.violations)


async def test_propose_empty_id_rejected(db: AsyncSession) -> None:
    mid = await _seed(db)
    patch = Patch(ops=[PatchOp(op="upsert", type="Evidence", id="", value={"claim": "test"})])
    result = await patch_service.propose(db, mid, "agent-a", patch)
    assert result.accepted is False
    assert any(v.code == "empty_id" for v in result.violations)


async def test_commit_valid_proposal(db: AsyncSession) -> None:
    mid = await _seed(db)
    patch = Patch(ops=[PatchOp(op="upsert", type="Evidence", id="ev-1", value={"claim": "test"})])
    propose_result = await patch_service.propose(db, mid, "agent-a", patch)
    commit_result = await patch_service.commit(db, mid, "agent-a", propose_result.proposal_id)
    assert commit_result.committed is True
    assert len(commit_result.new_versions) == 1
    assert commit_result.new_versions[0]["entity_id"] == "ev-1"
    assert commit_result.new_versions[0]["version"] == 1


async def test_commit_creates_entity_version(db: AsyncSession) -> None:
    mid = await _seed(db)
    patch = Patch(ops=[PatchOp(op="upsert", type="Evidence", id="ev-1", value={"claim": "v1"})])
    r1 = await patch_service.propose(db, mid, "agent-a", patch)
    await patch_service.commit(db, mid, "agent-a", r1.proposal_id)

    # Second version
    patch2 = Patch(ops=[PatchOp(op="upsert", type="Evidence", id="ev-1", value={"claim": "v2"})])
    r2 = await patch_service.propose(db, mid, "agent-a", patch2)
    c2 = await patch_service.commit(db, mid, "agent-a", r2.proposal_id)
    assert c2.new_versions[0]["version"] == 2


async def test_commit_not_found(db: AsyncSession) -> None:
    mid = await _seed(db)
    result = await patch_service.commit(db, mid, "agent-a", "prop_nonexistent")
    assert result.committed is False
    assert "not found" in result.message.lower()


async def test_commit_already_committed(db: AsyncSession) -> None:
    mid = await _seed(db)
    patch = Patch(ops=[PatchOp(op="upsert", type="Evidence", id="ev-1", value={"claim": "test"})])
    r = await patch_service.propose(db, mid, "agent-a", patch)
    await patch_service.commit(db, mid, "agent-a", r.proposal_id)
    result = await patch_service.commit(db, mid, "agent-a", r.proposal_id)
    assert result.committed is False
    assert "committed" in result.message.lower()


async def test_commit_rejected_proposal(db: AsyncSession) -> None:
    mid = await _seed(db)
    patch = Patch(ops=[PatchOp(op="upsert", type="Evidence", id="ev-1", value={})])
    r = await patch_service.propose(db, mid, "agent-a", patch)
    assert r.accepted is False
    result = await patch_service.commit(db, mid, "agent-a", r.proposal_id)
    assert result.committed is False


async def test_delete_op(db: AsyncSession) -> None:
    mid = await _seed(db)
    # Create entity
    patch = Patch(ops=[PatchOp(op="upsert", type="Evidence", id="ev-1", value={"claim": "test"})])
    r = await patch_service.propose(db, mid, "agent-a", patch)
    await patch_service.commit(db, mid, "agent-a", r.proposal_id)

    # Delete entity
    del_patch = Patch(ops=[PatchOp(op="delete", type="Evidence", id="ev-1")])
    r2 = await patch_service.propose(db, mid, "agent-a", del_patch)
    c2 = await patch_service.commit(db, mid, "agent-a", r2.proposal_id)
    assert c2.committed is True

    snapshot = await world_service.get_world_snapshot(db, mid)
    entity_ids = [e.entity_id for e in snapshot.entities]
    assert "ev-1" not in entity_ids

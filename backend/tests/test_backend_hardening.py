from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.config import settings
from baton_substrate.db.schema import EventRow, MissionRow, PatchRow
from baton_substrate.models.common import Actor
from baton_substrate.services import event_service, export_service, world_service


async def _create_mission(client: AsyncClient, title: str = "Hardening") -> str:
    response = await client.post("/missions", json={"title": title, "energy_budget": 5})
    assert response.status_code == 200
    return str(response.json()["mission_id"])


async def _register_evidence_type(mission_id: str) -> None:
    import baton_substrate.db.engine as db_engine

    async with db_engine.get_db() as db:
        await world_service.register_entity_type(
            db,
            mission_id,
            "Evidence",
            json_schema={
                "type": "object",
                "properties": {"claim": {"type": "string"}},
                "required": ["claim"],
            },
            invariants=[{"rule": "required_fields", "fields": ["claim"], "severity": "hard"}],
        )


def _mission_pack_zip(pack: dict[str, object]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("mission_pack.json", json.dumps(pack))
    return buffer.getvalue()


def _minimal_pack(mission_id: str = "mis_import") -> dict[str, object]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "schema_version": 1,
        "mission": {
            "mission_id": mission_id,
            "created_at": now,
            "title": "Import",
            "goal": "",
            "energy_budget": 10,
            "status": "exported",
        },
    }


async def test_child_routes_return_404_for_unknown_mission(api_client: AsyncClient) -> None:
    world_response = await api_client.get("/missions/missing/world")
    baton_response = await api_client.post(
        "/missions/missing/baton/claim",
        json={"actor_id": "atlas"},
    )

    assert world_response.status_code == 404
    assert baton_response.status_code == 404


async def test_production_mode_requires_bearer_token(
    api_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(settings, "api_key", "secret-token")

    health_response = await api_client.get("/health")
    unauthorized = await api_client.post("/missions", json={"title": "Blocked"})
    authorized = await api_client.post(
        "/missions",
        json={"title": "Allowed"},
        headers={"Authorization": "Bearer secret-token"},
    )

    assert health_response.status_code == 200
    assert health_response.json()["auth_required"] is True
    assert unauthorized.status_code == 401
    assert authorized.status_code == 200


async def test_production_mode_supports_scoped_api_keys(
    api_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(settings, "api_key", "")
    monkeypatch.setattr(
        settings, "api_keys", "read-token:reader,op-token:operator,admin-token:admin"
    )

    reader_metrics = await api_client.get(
        "/metrics",
        headers={"Authorization": "Bearer read-token"},
    )
    reader_write = await api_client.post(
        "/missions",
        json={"title": "Blocked"},
        headers={"Authorization": "Bearer read-token"},
    )
    operator_write = await api_client.post(
        "/missions",
        json={"title": "Allowed"},
        headers={"Authorization": "Bearer op-token"},
    )

    assert reader_metrics.status_code == 200
    assert "baton_http_requests_total" in reader_metrics.text
    assert reader_write.status_code == 403
    assert operator_write.status_code == 200


async def test_readiness_reports_auth_configuration(
    api_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(settings, "api_key", "")
    monkeypatch.setattr(settings, "api_keys", "")

    not_ready = await api_client.get("/ready")
    monkeypatch.setattr(settings, "api_keys", "admin-token:admin")
    ready = await api_client.get("/ready")

    assert not_ready.status_code == 503
    assert not_ready.json()["auth"] is False
    assert ready.status_code == 200
    assert ready.json()["ok"] is True


async def test_api_responses_include_security_headers(api_client: AsyncClient) -> None:
    response = await api_client.get("/health")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["x-frame-options"] == "DENY"


async def test_invalid_numeric_values_are_rejected(api_client: AsyncClient) -> None:
    bad_mission = await api_client.post("/missions", json={"title": "Bad", "energy_budget": -1})
    assert bad_mission.status_code == 422

    mission_id = await _create_mission(api_client)
    bad_lease = await api_client.post(
        f"/missions/{mission_id}/baton/claim",
        json={"actor_id": "atlas", "lease_ms": 0},
    )
    bad_spend = await api_client.post(
        f"/missions/{mission_id}/energy/spend",
        json={"actor_id": "atlas", "amount": -1},
    )

    assert bad_lease.status_code == 422
    assert bad_spend.status_code == 422


async def test_list_agents_includes_allocated_energy(api_client: AsyncClient) -> None:
    mission_id = await _create_mission(api_client)
    await api_client.post(
        f"/missions/{mission_id}/agents",
        json={"actor_id": "atlas", "display_name": "Atlas", "role": "researcher"},
    )

    response = await api_client.get(f"/missions/{mission_id}/agents")

    assert response.status_code == 200
    assert response.json()[0]["energy_balance"] == 5


async def test_commit_without_baton_is_forbidden(api_client: AsyncClient) -> None:
    mission_id = await _create_mission(api_client)

    response = await api_client.post(
        f"/missions/{mission_id}/patches/commit",
        json={"actor_id": "atlas", "proposal_id": "prop_missing"},
    )

    assert response.status_code == 403


async def test_energy_overspend_blocks_commit_and_keeps_patch_pending(
    api_client: AsyncClient,
) -> None:
    mission_id = await _create_mission(api_client)
    await _register_evidence_type(mission_id)
    await api_client.post(
        f"/missions/{mission_id}/agents",
        json={"actor_id": "atlas", "display_name": "Atlas", "role": "researcher"},
    )
    await api_client.post(f"/missions/{mission_id}/baton/claim", json={"actor_id": "atlas"})
    proposal = await api_client.post(
        f"/missions/{mission_id}/patches/propose",
        json={
            "actor_id": "atlas",
            "patch": {
                "ops": [
                    {
                        "op": "upsert",
                        "type": "Evidence",
                        "id": "ev-overspend",
                        "value": {"claim": "Energy must gate commits"},
                    }
                ]
            },
        },
    )
    proposal_id = proposal.json()["proposal_id"]

    response = await api_client.post(
        f"/missions/{mission_id}/patches/commit",
        json={"actor_id": "atlas", "proposal_id": proposal_id},
    )

    assert response.status_code == 409
    import baton_substrate.db.engine as db_engine

    async with db_engine.get_db() as db:
        result = await db.execute(select(PatchRow).where(PatchRow.proposal_id == proposal_id))
        assert result.scalar_one().status == "pending"


async def test_export_payload_shape_and_import_validation(api_client: AsyncClient) -> None:
    mission_id = await _create_mission(api_client)
    response = await api_client.post(f"/missions/{mission_id}/export")
    assert response.status_code == 200

    with zipfile.ZipFile(io.BytesIO(response.content), "r") as archive:
        pack = json.loads(archive.read("mission_pack.json"))

    assert pack["schema_version"] == 1
    assert "payload" not in pack["events"][0]["payload"]

    duplicate = await api_client.post(
        "/missions/import",
        files={"file": ("pack.zip", response.content, "application/zip")},
    )
    malformed = await api_client.post(
        "/missions/import",
        files={"file": ("pack.zip", b"not-a-zip", "application/zip")},
    )

    assert duplicate.status_code == 409
    assert malformed.status_code == 400


async def test_import_rejects_malformed_nested_pack(api_client: AsyncClient) -> None:
    pack = _minimal_pack("mis_nested_bad")
    pack["entity_types"] = [{"json_schema": {}, "invariants": []}]
    payload = _mission_pack_zip(pack)

    response = await api_client.post(
        "/missions/import",
        files={"file": ("pack.zip", payload, "application/zip")},
    )

    assert response.status_code == 400
    assert "entity_types[0].type_name" in response.json()["detail"]


async def test_import_rejects_large_uncompressed_member(
    db: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "max_mission_pack_bytes", 256)
    pack = _minimal_pack("mis_zip_bomb")
    mission = pack["mission"]
    assert isinstance(mission, dict)
    pack["mission"] = {**mission, "goal": "x" * 10_000}
    payload = _mission_pack_zip(pack)

    with pytest.raises(export_service.MissionPackError, match="exceeds upload size"):
        await export_service.import_mission_pack(db, payload)


async def test_event_cursor_handles_same_timestamp_ordering(db: AsyncSession) -> None:
    mission_id = "mis_cursor"
    now = datetime.now(timezone.utc).isoformat()
    db.add(
        MissionRow(
            mission_id=mission_id,
            created_at=now,
            title="Cursor",
            goal="",
            energy_budget=100,
            status="idle",
        )
    )
    actor = Actor(actor_id="system", actor_type="system", display_name="System")
    for event_id in ("evt_a", "evt_b", "evt_c"):
        db.add(
            EventRow(
                event_id=event_id,
                mission_id=mission_id,
                ts=now,
                type="mission.test",
                actor_json=actor.model_dump_json(),
                payload_json=json.dumps({"event_id": event_id}),
            )
        )
    await db.flush()

    first_page, cursor = await event_service.query(db, mission_id, limit=2)
    assert [event.event_id for event in first_page] == ["evt_a", "evt_b"]
    assert cursor is not None

    second_page, next_cursor = await event_service.query(db, mission_id, after=cursor, limit=2)
    assert [event.event_id for event in second_page] == ["evt_c"]
    assert next_cursor is None

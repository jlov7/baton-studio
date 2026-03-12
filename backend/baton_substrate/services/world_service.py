from __future__ import annotations

import json
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from baton_substrate.db.schema import (
    EntityRow,
    EntityTypeRow,
    EntityVersionRow,
    PatchRow,
)
from baton_substrate.models.world import (
    EntityDetail,
    EntityTypeSchema,
    EntityVersionDetail,
    WorldSnapshot,
)


async def register_entity_type(
    db: AsyncSession,
    mission_id: str,
    type_name: str,
    json_schema: dict[str, Any] | None = None,
    invariants: list[dict[str, Any]] | None = None,
) -> None:
    row = EntityTypeRow(
        mission_id=mission_id,
        type_name=type_name,
        json_schema=json.dumps(json_schema or {}),
        invariants_json=json.dumps(invariants or []),
    )
    db.add(row)
    await db.flush()


async def list_entity_types(
    db: AsyncSession,
    mission_id: str,
) -> list[EntityTypeSchema]:
    result = await db.execute(select(EntityTypeRow).where(EntityTypeRow.mission_id == mission_id))
    rows = result.scalars().all()
    return [
        EntityTypeSchema(
            type_name=r.type_name,
            json_schema=json.loads(r.json_schema),
            invariants=json.loads(r.invariants_json),
        )
        for r in rows
    ]


async def get_entity_type(
    db: AsyncSession,
    mission_id: str,
    type_name: str,
) -> EntityTypeRow | None:
    result = await db.execute(
        select(EntityTypeRow).where(
            EntityTypeRow.mission_id == mission_id,
            EntityTypeRow.type_name == type_name,
        )
    )
    return result.scalar_one_or_none()


async def upsert_entity(
    db: AsyncSession,
    mission_id: str,
    entity_id: str,
    type_name: str,
    value: dict[str, Any],
    actor_id: str,
) -> int:
    result = await db.execute(
        select(EntityRow).where(
            EntityRow.mission_id == mission_id,
            EntityRow.entity_id == entity_id,
        )
    )
    entity = result.scalar_one_or_none()
    if not entity:
        entity = EntityRow(
            mission_id=mission_id,
            entity_id=entity_id,
            type_name=type_name,
        )
        db.add(entity)
        await db.flush()

    max_v = await db.execute(
        select(func.coalesce(func.max(EntityVersionRow.version), 0)).where(
            EntityVersionRow.mission_id == mission_id,
            EntityVersionRow.entity_id == entity_id,
        )
    )
    next_version = max_v.scalar_one() + 1

    from datetime import datetime, timezone

    ver = EntityVersionRow(
        mission_id=mission_id,
        entity_id=entity_id,
        version=next_version,
        created_at=datetime.now(timezone.utc).isoformat(),
        actor_id=actor_id,
        value_json=json.dumps(value),
    )
    db.add(ver)
    await db.flush()
    return next_version


async def delete_entity(
    db: AsyncSession,
    mission_id: str,
    entity_id: str,
) -> bool:
    result = await db.execute(
        select(EntityRow).where(
            EntityRow.mission_id == mission_id,
            EntityRow.entity_id == entity_id,
        )
    )
    row = result.scalar_one_or_none()
    if not row:
        return False
    await db.delete(row)
    await db.flush()
    return True


async def get_world_snapshot(
    db: AsyncSession,
    mission_id: str,
) -> WorldSnapshot:
    types = await list_entity_types(db, mission_id)

    entity_result = await db.execute(select(EntityRow).where(EntityRow.mission_id == mission_id))
    entity_rows = entity_result.scalars().all()

    entities: list[EntityDetail] = []
    for er in entity_rows:
        ver_result = await db.execute(
            select(EntityVersionRow)
            .where(
                EntityVersionRow.mission_id == mission_id,
                EntityVersionRow.entity_id == er.entity_id,
            )
            .order_by(EntityVersionRow.version)
        )
        versions_rows = ver_result.scalars().all()
        if not versions_rows:
            continue
        latest = versions_rows[-1]
        versions = [
            EntityVersionDetail(
                version=v.version,
                created_at=v.created_at,
                actor_id=v.actor_id,
                value=json.loads(v.value_json),
            )
            for v in versions_rows
        ]
        entities.append(
            EntityDetail(
                entity_id=er.entity_id,
                type_name=er.type_name,
                latest_version=latest.version,
                value=json.loads(latest.value_json),
                versions=versions,
            )
        )

    pending_result = await db.execute(
        select(func.count())
        .select_from(PatchRow)
        .where(PatchRow.mission_id == mission_id, PatchRow.status == "pending")
    )
    pending = pending_result.scalar_one()

    return WorldSnapshot(
        mission_id=mission_id,
        entity_types=types,
        entities=entities,
        pending_proposals=pending,
    )

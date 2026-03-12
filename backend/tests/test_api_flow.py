"""Integration tests: full lifecycle through the HTTP API."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from baton_substrate.api.main import create_app
from baton_substrate.db.schema import Base


@pytest.fixture
async def client() -> AsyncClient:  # type: ignore[misc]
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    from contextlib import asynccontextmanager
    from collections.abc import AsyncGenerator

    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    @asynccontextmanager
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    # Monkey-patch the db module
    import baton_substrate.db.engine as db_engine

    original_get_db = db_engine.get_db
    db_engine.get_db = override_get_db

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    db_engine.get_db = original_get_db
    await engine.dispose()


async def test_health(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["service"] == "baton-substrate"


async def test_create_and_get_mission(client: AsyncClient) -> None:
    resp = await client.post(
        "/missions", json={"title": "Test Mission", "goal": "test", "energy_budget": 500}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Test Mission"
    assert data["mission_id"].startswith("mis_")
    mid = data["mission_id"]

    resp2 = await client.get(f"/missions/{mid}")
    assert resp2.status_code == 200
    assert resp2.json()["mission_id"] == mid


async def test_full_lifecycle(client: AsyncClient) -> None:
    # Create mission
    resp = await client.post("/missions", json={"title": "Lifecycle", "energy_budget": 1000})
    mid = resp.json()["mission_id"]

    # Register agent
    resp = await client.post(
        f"/missions/{mid}/agents",
        json={"actor_id": "atlas", "display_name": "Atlas", "role": "researcher"},
    )
    assert resp.status_code == 200

    # Check energy
    resp = await client.get(f"/missions/{mid}/energy/atlas")
    assert resp.status_code == 200
    balance = resp.json()["balance"]
    assert balance > 0

    # Register entity type
    # (entity types are registered via world_service, but we test the world endpoint)
    resp = await client.get(f"/missions/{mid}/world")
    assert resp.status_code == 200

    # Claim baton
    resp = await client.post(f"/missions/{mid}/baton/claim", json={"actor_id": "atlas"})
    assert resp.status_code == 200
    assert resp.json()["holder"] == "atlas"

    # Get baton state
    resp = await client.get(f"/missions/{mid}/baton")
    assert resp.status_code == 200
    assert resp.json()["holder"] == "atlas"

    # Release baton
    resp = await client.post(f"/missions/{mid}/baton/release", json={"actor_id": "atlas"})
    assert resp.status_code == 200
    assert resp.json()["holder"] is None

    # Get events
    resp = await client.get(f"/missions/{mid}/events")
    assert resp.status_code == 200
    events = resp.json()["events"]
    assert len(events) >= 3  # mission.created, agent.joined, energy.allocated, baton.claimed, etc.

    # SC metric
    resp = await client.get(f"/missions/{mid}/metrics/sc")
    assert resp.status_code == 200


async def test_baton_contention_via_api(client: AsyncClient) -> None:
    resp = await client.post("/missions", json={"title": "Contention"})
    mid = resp.json()["mission_id"]

    await client.post(f"/missions/{mid}/baton/claim", json={"actor_id": "agent-a"})
    resp2 = await client.post(f"/missions/{mid}/baton/claim", json={"actor_id": "agent-b"})
    assert resp2.json()["holder"] == "agent-a"
    assert resp2.json()["queue"] == ["agent-b"]


async def test_causal_graph_via_api(client: AsyncClient) -> None:
    resp = await client.post("/missions", json={"title": "Graph"})
    mid = resp.json()["mission_id"]

    resp = await client.post(
        f"/missions/{mid}/causal/edge",
        json={"actor_id": "a", "from_id": "n1", "to_id": "n2", "type": "supports"},
    )
    assert resp.status_code == 200
    assert resp.json()["edge_id"].startswith("edg_")

    resp2 = await client.get(f"/missions/{mid}/causal/graph")
    assert resp2.status_code == 200
    graph = resp2.json()
    assert len(graph["nodes"]) == 2
    assert len(graph["edges"]) == 1


async def test_mission_status_update(client: AsyncClient) -> None:
    resp = await client.post("/missions", json={"title": "Status"})
    mid = resp.json()["mission_id"]
    assert resp.json()["status"] == "idle"

    resp2 = await client.post(f"/missions/{mid}/status", json={"status": "running"})
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "running"

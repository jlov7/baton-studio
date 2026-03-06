"""Tests for the demo simulator end-to-end flow."""
from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from baton_substrate.db.schema import Base
from baton_substrate.demo.simulator import run_demo


async def test_demo_runs_to_completion() -> None:
    # StaticPool ensures all connections share the same in-memory DB
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
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

    async def noop_init_db() -> None:
        pass

    # Patch references in all modules that import get_db / init_db
    import baton_substrate.db.engine as db_engine
    import baton_substrate.db as db_pkg
    import baton_substrate.demo.simulator as sim_mod

    orig_engine_get_db = db_engine.get_db
    orig_engine_init_db = db_engine.init_db
    orig_pkg_get_db = db_pkg.get_db
    orig_pkg_init_db = db_pkg.init_db
    orig_sim_get_db = sim_mod.get_db
    orig_sim_init_db = sim_mod.init_db

    db_engine.get_db = override_get_db
    db_engine.init_db = noop_init_db
    db_pkg.get_db = override_get_db
    db_pkg.init_db = noop_init_db
    sim_mod.get_db = override_get_db
    sim_mod.init_db = noop_init_db

    try:
        mission_id = await run_demo(delay=0.0)
        assert mission_id.startswith("mis_")

        # Verify state after demo
        async with override_get_db() as db:
            from baton_substrate.services import event_service, world_service, causal_service

            events, _ = await event_service.query(db, mission_id, limit=500)
            assert len(events) >= 20

            world = await world_service.get_world_snapshot(db, mission_id)
            assert len(world.entity_types) >= 4
            assert len(world.entities) >= 5

            graph = await causal_service.get_graph(db, mission_id)
            assert len(graph.nodes) >= 5
            assert len(graph.edges) >= 4

            # Verify some stale nodes exist (from invalidation step)
            stale_nodes = [n for n in graph.nodes if n.status == "stale"]
            assert len(stale_nodes) >= 1
    finally:
        db_engine.get_db = orig_engine_get_db
        db_engine.init_db = orig_engine_init_db
        db_pkg.get_db = orig_pkg_get_db
        db_pkg.init_db = orig_pkg_init_db
        sim_mod.get_db = orig_sim_get_db
        sim_mod.init_db = orig_sim_init_db
        await engine.dispose()

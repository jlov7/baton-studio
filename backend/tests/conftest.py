from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from baton_substrate.api.main import create_app
from baton_substrate.db.schema import Base


@pytest.fixture
async def db() -> AsyncSession:  # type: ignore[misc]
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.commit()

    await engine.dispose()


@pytest.fixture
async def api_client() -> AsyncGenerator[AsyncClient, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)

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

    import baton_substrate.db.engine as db_engine

    original_get_db = db_engine.get_db
    original_init_db = db_engine.init_db
    db_engine.get_db = override_get_db
    db_engine.init_db = noop_init_db

    app = create_app()
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
    finally:
        db_engine.get_db = original_get_db
        db_engine.init_db = original_init_db
        await engine.dispose()

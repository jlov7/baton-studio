from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import logging

from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from baton_substrate.config import settings
from baton_substrate.db.schema import Base

logger = logging.getLogger("baton_substrate.db")

engine = create_async_engine(settings.database_url, echo=False)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


def _apply_sqlite_compat_migrations(conn: Connection) -> None:
    if conn.dialect.name != "sqlite":
        return
    tables = {
        row[0]
        for row in conn.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table'").all()
    }
    if "entities" not in tables:
        return
    entity_columns = {
        row["name"] for row in conn.exec_driver_sql("PRAGMA table_info(entities)").mappings()
    }
    if "deleted_at" not in entity_columns:
        conn.exec_driver_sql("ALTER TABLE entities ADD COLUMN deleted_at TEXT")
    if "deleted_by" not in entity_columns:
        conn.exec_driver_sql("ALTER TABLE entities ADD COLUMN deleted_by TEXT")


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_apply_sqlite_compat_migrations)


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            logger.debug("db_session_rollback", extra={"error": str(exc)})
            await session.rollback()
            raise

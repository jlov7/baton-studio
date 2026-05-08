from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from baton_substrate.api.routes import router
from baton_substrate.api.security import (
    ApiKeyAuthMiddleware,
    RequestIdMiddleware,
    SecurityHeadersMiddleware,
)
from baton_substrate.config import settings
import baton_substrate.db.engine as db_engine


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    await db_engine.init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Baton Studio Substrate Server",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(ApiKeyAuthMiddleware)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)

    app.include_router(router)
    return app


app = create_app()

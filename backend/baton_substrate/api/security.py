from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import WebSocket, WebSocketException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from baton_substrate.api.observability import runtime_metrics
from baton_substrate.config import settings

logger = logging.getLogger("baton_substrate.api")

PUBLIC_PATHS = {
    "/health",
    "/ready",
    "/docs",
    "/openapi.json",
    "/redoc",
}

ROLE_RANK = {"reader": 0, "operator": 1, "admin": 2}


def _is_production() -> bool:
    return settings.environment == "production"


def _configured_key_roles() -> dict[str, str]:
    key_roles: dict[str, str] = {}
    if settings.api_key:
        key_roles[settings.api_key] = "admin"
    for item in settings.api_keys.split(","):
        item = item.strip()
        if not item:
            continue
        token, separator, role = item.partition(":")
        normalized_role = role.strip().lower() if separator else "admin"
        if normalized_role not in ROLE_RANK:
            logger.warning("invalid_api_key_role", extra={"role": normalized_role})
            continue
        if token.strip():
            key_roles[token.strip()] = normalized_role
    return key_roles


def _auth_role(authorization: str | None) -> str | None:
    if not _is_production():
        return "admin"
    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer":
        return None
    return _configured_key_roles().get(token)


def _has_role(role: str | None, required_role: str) -> bool:
    if role is None:
        return False
    return ROLE_RANK[role] >= ROLE_RANK[required_role]


def _required_role(method: str, path: str) -> str:
    if method in {"GET", "HEAD", "OPTIONS"}:
        return "reader"
    if path == "/missions/import":
        return "admin"
    return "operator"


def auth_ready() -> bool:
    return not _is_production() or bool(_configured_key_roles())


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("x-request-id") or f"req_{uuid.uuid4().hex[:12]}"
        request.state.request_id = request_id
        started = time.perf_counter()
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        runtime_metrics.record_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response


class ApiKeyAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if (
            request.method == "OPTIONS"
            or request.url.path in PUBLIC_PATHS
            or request.url.path.startswith("/docs/")
        ):
            return await call_next(request)

        if not _is_production():
            return await call_next(request)

        if not _configured_key_roles():
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "BATON_API_KEY or BATON_API_KEYS is required in production mode"
                },
            )

        role = _auth_role(request.headers.get("authorization"))
        if role is None:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
        required_role = _required_role(request.method, request.url.path)
        if not _has_role(role, required_role):
            return JSONResponse(
                status_code=403,
                content={"detail": f"Requires {required_role} role"},
            )

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        response.headers.setdefault("x-content-type-options", "nosniff")
        response.headers.setdefault("referrer-policy", "no-referrer")
        response.headers.setdefault("x-frame-options", "DENY")
        if settings.environment == "production":
            response.headers.setdefault(
                "strict-transport-security",
                "max-age=31536000; includeSubDomains",
            )
        return response


async def authorize_websocket(websocket: WebSocket) -> None:
    if not _is_production():
        return
    authorization = websocket.headers.get("authorization")
    token = websocket.query_params.get("token")
    if token and _has_role(_configured_key_roles().get(token), "reader"):
        return
    if _has_role(_auth_role(authorization), "reader"):
        return
    raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Unauthorized")

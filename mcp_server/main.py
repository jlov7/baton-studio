"""Baton Studio MCP server — stdio transport, proxies to backend HTTP API."""
from __future__ import annotations

import json
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

BASE_URL = os.environ.get("BATON_BACKEND_URL", "http://localhost:8787")

server = Server("baton-studio")
client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)


def _text(data: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


def _error(msg: str, details: Any = None) -> list[TextContent]:
    payload: dict[str, Any] = {"error": msg}
    if details:
        payload["details"] = details
    return [TextContent(type="text", text=json.dumps(payload, indent=2))]


def _auth_headers() -> dict[str, str]:
    token = os.environ.get("BATON_API_KEY")
    return {"Authorization": f"Bearer {token}"} if token else {}


async def _request_json(
    method: str,
    path: str,
    *,
    error_message: str,
    **kwargs: Any,
) -> tuple[Any | None, list[TextContent] | None]:
    try:
        response = await client.request(method, path, headers=_auth_headers(), **kwargs)
    except httpx.ConnectError:
        return None, _error(
            "Cannot connect to Baton backend",
            {"base_url": BASE_URL, "hint": "Start the backend server or set BATON_BACKEND_URL."},
        )

    try:
        data: Any = response.json()
    except json.JSONDecodeError:
        data = {"raw": response.text}

    if response.status_code >= 400:
        return None, _error(
            error_message,
            {"status_code": response.status_code, "response": data},
        )
    return data, None


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="baton.health",
            description="Check backend health and connection status",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="baton.read_world",
            description="Read the current world model snapshot for a mission",
            inputSchema={
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string", "description": "Mission ID"},
                },
                "required": ["mission_id"],
            },
        ),
        Tool(
            name="baton.list_types",
            description="List registered entity types for a mission",
            inputSchema={
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string", "description": "Mission ID"},
                },
                "required": ["mission_id"],
            },
        ),
        Tool(
            name="baton.propose_patch",
            description="Propose a patch to the world model (validates against invariants)",
            inputSchema={
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string"},
                    "actor_id": {"type": "string"},
                    "patch": {
                        "type": "object",
                        "properties": {
                            "ops": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "op": {"type": "string", "enum": ["upsert", "delete"]},
                                        "type": {"type": "string"},
                                        "id": {"type": "string"},
                                        "value": {"type": "object"},
                                    },
                                    "required": ["op", "type", "id"],
                                },
                            }
                        },
                        "required": ["ops"],
                    },
                },
                "required": ["mission_id", "actor_id", "patch"],
            },
        ),
        Tool(
            name="baton.claim_baton",
            description="Claim the baton (write-rights mutex) for a mission",
            inputSchema={
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string"},
                    "actor_id": {"type": "string"},
                    "lease_ms": {"type": "integer", "default": 20000},
                },
                "required": ["mission_id", "actor_id"],
            },
        ),
        Tool(
            name="baton.release_baton",
            description="Release the baton for a mission",
            inputSchema={
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string"},
                    "actor_id": {"type": "string"},
                },
                "required": ["mission_id", "actor_id"],
            },
        ),
        Tool(
            name="baton.commit_patch",
            description="Commit a previously proposed patch (requires baton)",
            inputSchema={
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string"},
                    "actor_id": {"type": "string"},
                    "proposal_id": {"type": "string"},
                },
                "required": ["mission_id", "actor_id", "proposal_id"],
            },
        ),
        Tool(
            name="baton.add_causal_edge",
            description="Add a causal edge between two nodes in the graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string"},
                    "actor_id": {"type": "string"},
                    "from_id": {"type": "string"},
                    "to_id": {"type": "string"},
                    "type": {"type": "string"},
                    "metadata": {"type": "object", "default": {}},
                },
                "required": ["mission_id", "actor_id", "from_id", "to_id", "type"],
            },
        ),
        Tool(
            name="baton.energy_balance",
            description="Check energy balance for an actor in a mission",
            inputSchema={
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string"},
                    "actor_id": {"type": "string"},
                },
                "required": ["mission_id", "actor_id"],
            },
        ),
        Tool(
            name="baton.energy_spend",
            description="Spend energy from an actor's balance",
            inputSchema={
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string"},
                    "actor_id": {"type": "string"},
                    "amount": {"type": "integer"},
                    "reason": {"type": "string", "default": ""},
                },
                "required": ["mission_id", "actor_id", "amount"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    try:
        if name == "baton.health":
            data, error = await _request_json("GET", "/health", error_message="Health check failed")
            return error or _text(data)

        elif name == "baton.read_world":
            mid = arguments["mission_id"]
            data, error = await _request_json(
                "GET",
                f"/missions/{mid}/world",
                error_message="World read failed",
            )
            return error or _text(data)

        elif name == "baton.list_types":
            mid = arguments["mission_id"]
            data, error = await _request_json(
                "GET",
                f"/missions/{mid}/types",
                error_message="Entity type list failed",
            )
            return error or _text(data)

        elif name == "baton.propose_patch":
            mid = arguments["mission_id"]
            data, error = await _request_json(
                "POST",
                f"/missions/{mid}/patches/propose",
                error_message="Patch proposal failed",
                json={"actor_id": arguments["actor_id"], "patch": arguments["patch"]},
            )
            return error or _text(data)

        elif name == "baton.claim_baton":
            mid = arguments["mission_id"]
            data, error = await _request_json(
                "POST",
                f"/missions/{mid}/baton/claim",
                error_message="Baton claim failed",
                json={
                    "actor_id": arguments["actor_id"],
                    "lease_ms": arguments.get("lease_ms", 20000),
                },
            )
            return error or _text(data)

        elif name == "baton.release_baton":
            mid = arguments["mission_id"]
            data, error = await _request_json(
                "POST",
                f"/missions/{mid}/baton/release",
                error_message="Baton release failed",
                json={"actor_id": arguments["actor_id"]},
            )
            return error or _text(data)

        elif name == "baton.commit_patch":
            mid = arguments["mission_id"]
            data, error = await _request_json(
                "POST",
                f"/missions/{mid}/patches/commit",
                error_message="Patch commit failed",
                json={
                    "actor_id": arguments["actor_id"],
                    "proposal_id": arguments["proposal_id"],
                },
            )
            if error:
                payload = json.loads(error[0].text)
                details = payload.get("details", {})
                if details.get("status_code") == 403:
                    return _error("Baton not held", details)
                return error
            return _text(data)

        elif name == "baton.add_causal_edge":
            mid = arguments["mission_id"]
            data, error = await _request_json(
                "POST",
                f"/missions/{mid}/causal/edge",
                error_message="Causal edge creation failed",
                json={
                    "actor_id": arguments["actor_id"],
                    "from_id": arguments["from_id"],
                    "to_id": arguments["to_id"],
                    "type": arguments["type"],
                    "metadata": arguments.get("metadata", {}),
                },
            )
            return error or _text(data)

        elif name == "baton.energy_balance":
            mid = arguments["mission_id"]
            aid = arguments["actor_id"]
            data, error = await _request_json(
                "GET",
                f"/missions/{mid}/energy/{aid}",
                error_message="Energy balance read failed",
            )
            return error or _text(data)

        elif name == "baton.energy_spend":
            mid = arguments["mission_id"]
            data, error = await _request_json(
                "POST",
                f"/missions/{mid}/energy/spend",
                error_message="Energy spend failed",
                json={
                    "actor_id": arguments["actor_id"],
                    "amount": arguments["amount"],
                    "reason": arguments.get("reason", ""),
                },
            )
            return error or _text(data)

        else:
            return _error(f"Unknown tool: {name}")

    except Exception as e:
        return _error(f"Tool error: {type(e).__name__}: {e}")


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def cli() -> None:
    import asyncio

    asyncio.run(main())


if __name__ == "__main__":
    cli()

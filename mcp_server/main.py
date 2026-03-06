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
            r = await client.get("/health")
            return _text(r.json())

        elif name == "baton.read_world":
            mid = arguments["mission_id"]
            r = await client.get(f"/missions/{mid}/world")
            return _text(r.json())

        elif name == "baton.list_types":
            mid = arguments["mission_id"]
            r = await client.get(f"/missions/{mid}/types")
            return _text(r.json())

        elif name == "baton.propose_patch":
            mid = arguments["mission_id"]
            r = await client.post(
                f"/missions/{mid}/patches/propose",
                json={"actor_id": arguments["actor_id"], "patch": arguments["patch"]},
            )
            data = r.json()
            if r.status_code != 200:
                return _error("Patch proposal failed", data)
            return _text(data)

        elif name == "baton.claim_baton":
            mid = arguments["mission_id"]
            r = await client.post(
                f"/missions/{mid}/baton/claim",
                json={
                    "actor_id": arguments["actor_id"],
                    "lease_ms": arguments.get("lease_ms", 20000),
                },
            )
            return _text(r.json())

        elif name == "baton.release_baton":
            mid = arguments["mission_id"]
            r = await client.post(
                f"/missions/{mid}/baton/release",
                json={"actor_id": arguments["actor_id"]},
            )
            return _text(r.json())

        elif name == "baton.commit_patch":
            mid = arguments["mission_id"]
            r = await client.post(
                f"/missions/{mid}/patches/commit",
                json={
                    "actor_id": arguments["actor_id"],
                    "proposal_id": arguments["proposal_id"],
                },
            )
            data = r.json()
            if r.status_code == 403:
                return _error("Baton not held", data)
            return _text(data)

        elif name == "baton.add_causal_edge":
            mid = arguments["mission_id"]
            r = await client.post(
                f"/missions/{mid}/causal/edge",
                json={
                    "actor_id": arguments["actor_id"],
                    "from_id": arguments["from_id"],
                    "to_id": arguments["to_id"],
                    "type": arguments["type"],
                    "metadata": arguments.get("metadata", {}),
                },
            )
            return _text(r.json())

        elif name == "baton.energy_balance":
            mid = arguments["mission_id"]
            aid = arguments["actor_id"]
            r = await client.get(f"/missions/{mid}/energy/{aid}")
            return _text(r.json())

        elif name == "baton.energy_spend":
            mid = arguments["mission_id"]
            r = await client.post(
                f"/missions/{mid}/energy/spend",
                json={
                    "actor_id": arguments["actor_id"],
                    "amount": arguments["amount"],
                    "reason": arguments.get("reason", ""),
                },
            )
            data = r.json()
            if r.status_code == 400:
                return _error("Energy spend failed", data)
            return _text(data)

        else:
            return _error(f"Unknown tool: {name}")

    except httpx.ConnectError:
        return _error("Cannot connect to backend. Is the server running on port 8787?")
    except Exception as e:
        return _error(f"Tool error: {type(e).__name__}: {e}")


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

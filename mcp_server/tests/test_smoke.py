from __future__ import annotations

import json

import httpx
import pytest

import main as mcp_main


@pytest.mark.asyncio
async def test_list_tools_exposes_core_surface() -> None:
    tools = await mcp_main.list_tools()
    tool_names = {tool.name for tool in tools}

    assert "baton.health" in tool_names
    assert "baton.read_world" in tool_names
    assert "baton.commit_patch" in tool_names
    commit_tool = next(tool for tool in tools if tool.name == "baton.commit_patch")
    assert commit_tool.inputSchema["required"] == ["mission_id", "actor_id", "proposal_id"]


async def _with_stubbed_client(
    monkeypatch: pytest.MonkeyPatch,
    handler,
) -> httpx.AsyncClient:
    stub_client = httpx.AsyncClient(
        base_url="http://example.test",
        transport=httpx.MockTransport(handler),
    )
    monkeypatch.setattr(mcp_main, "client", stub_client)
    return stub_client


@pytest.mark.asyncio
async def test_health_tool_proxies_backend_response(monkeypatch: pytest.MonkeyPatch) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/health"
        return httpx.Response(200, json={"ok": True})

    original_client = mcp_main.client
    stub_client = await _with_stubbed_client(monkeypatch, handler)

    try:
        payload = await mcp_main.call_tool("baton.health", {})
    finally:
        await stub_client.aclose()
        monkeypatch.setattr(mcp_main, "client", original_client)

    assert json.loads(payload[0].text) == {"ok": True}


@pytest.mark.asyncio
async def test_auth_header_is_forwarded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BATON_API_KEY", "secret-token")

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer secret-token"
        return httpx.Response(200, json={"ok": True})

    stub_client = await _with_stubbed_client(monkeypatch, handler)
    try:
        payload = await mcp_main.call_tool("baton.health", {})
    finally:
        await stub_client.aclose()

    assert json.loads(payload[0].text) == {"ok": True}


@pytest.mark.asyncio
async def test_backend_non_200_returns_structured_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "Mission missing"})

    stub_client = await _with_stubbed_client(monkeypatch, handler)
    try:
        payload = await mcp_main.call_tool("baton.read_world", {"mission_id": "missing"})
    finally:
        await stub_client.aclose()

    data = json.loads(payload[0].text)
    assert data["error"] == "World read failed"
    assert data["details"]["status_code"] == 404
    assert data["details"]["response"] == {"detail": "Mission missing"}


@pytest.mark.asyncio
async def test_commit_without_baton_returns_specific_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/missions/mis_1/patches/commit"
        return httpx.Response(403, json={"detail": "Actor atlas does not hold the baton"})

    stub_client = await _with_stubbed_client(monkeypatch, handler)
    try:
        payload = await mcp_main.call_tool(
            "baton.commit_patch",
            {"mission_id": "mis_1", "actor_id": "atlas", "proposal_id": "prop_1"},
        )
    finally:
        await stub_client.aclose()

    data = json.loads(payload[0].text)
    assert data["error"] == "Baton not held"
    assert data["details"]["status_code"] == 403


@pytest.mark.asyncio
async def test_connection_failure_has_actionable_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline", request=request)

    stub_client = await _with_stubbed_client(monkeypatch, handler)
    try:
        payload = await mcp_main.call_tool("baton.health", {})
    finally:
        await stub_client.aclose()

    data = json.loads(payload[0].text)
    assert data["error"] == "Cannot connect to Baton backend"
    assert "BATON_BACKEND_URL" in data["details"]["hint"]


@pytest.mark.asyncio
async def test_causal_edge_tool_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/missions/mis_1/causal/edge"
        assert json.loads(request.content) == {
            "actor_id": "atlas",
            "from_id": "ev-1",
            "to_id": "ps-1",
            "type": "supports",
            "metadata": {"confidence": 0.8},
        }
        return httpx.Response(200, json={"edge_id": "edg_1"})

    stub_client = await _with_stubbed_client(monkeypatch, handler)
    try:
        payload = await mcp_main.call_tool(
            "baton.add_causal_edge",
            {
                "mission_id": "mis_1",
                "actor_id": "atlas",
                "from_id": "ev-1",
                "to_id": "ps-1",
                "type": "supports",
                "metadata": {"confidence": 0.8},
            },
        )
    finally:
        await stub_client.aclose()

    assert json.loads(payload[0].text) == {"edge_id": "edg_1"}


@pytest.mark.asyncio
async def test_energy_spend_error_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/missions/mis_1/energy/spend"
        assert json.loads(request.content)["amount"] == 50
        return httpx.Response(409, json={"detail": "Insufficient energy"})

    stub_client = await _with_stubbed_client(monkeypatch, handler)
    try:
        payload = await mcp_main.call_tool(
            "baton.energy_spend",
            {"mission_id": "mis_1", "actor_id": "atlas", "amount": 50},
        )
    finally:
        await stub_client.aclose()

    data = json.loads(payload[0].text)
    assert data["error"] == "Energy spend failed"
    assert data["details"]["status_code"] == 409

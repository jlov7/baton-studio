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


@pytest.mark.asyncio
async def test_health_tool_proxies_backend_response(monkeypatch) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/health"
        return httpx.Response(200, json={"ok": True})

    stub_client = httpx.AsyncClient(
        base_url="http://example.test",
        transport=httpx.MockTransport(handler),
    )
    original_client = mcp_main.client
    monkeypatch.setattr(mcp_main, "client", stub_client)

    try:
        payload = await mcp_main.call_tool("baton.health", {})
    finally:
        await stub_client.aclose()
        monkeypatch.setattr(mcp_main, "client", original_client)

    assert json.loads(payload[0].text) == {"ok": True}

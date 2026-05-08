# Baton Studio MCP Server

This directory contains the stdio MCP bridge for Baton Studio. It proxies `baton.*` tool calls to the backend HTTP API.

## Run It

```bash
uv run --project mcp_server baton-mcp-server
```

By default it talks to `http://localhost:8787`. Override that with `BATON_BACKEND_URL`.

For production-mode backends, provide an `operator` or `admin` token:

```bash
BATON_BACKEND_URL=http://localhost:8787 \
BATON_API_KEY="$BATON_API_KEY" \
uv run --project mcp_server baton-mcp-server
```

## Local Checks

```bash
cd mcp_server
uv sync --extra dev
uv run pytest -q
```

## Tool Surface

The current server exposes:

- `baton.health`
- `baton.read_world`
- `baton.list_types`
- `baton.propose_patch`
- `baton.claim_baton`
- `baton.release_baton`
- `baton.commit_patch`
- `baton.add_causal_edge`
- `baton.energy_balance`
- `baton.energy_spend`

See [../docs/MCP_SPEC.md](../docs/MCP_SPEC.md) for the public contract and [main.py](main.py) for the current implementation.

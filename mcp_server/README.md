# MCP server (Baton Studio)

This folder contains the **Model Context Protocol** server that exposes Baton Studio substrate operations as tools.

Target clients:
- Claude Code (via `claude mcp add ...`)
- any MCP-compatible client

Tools to implement (minimum):
- baton.health
- baton.read_world
- baton.list_types
- baton.propose_patch
- baton.claim_baton
- baton.release_baton
- baton.add_causal_edge
- baton.energy_balance
- baton.energy_spend

See `docs/MCP_SPEC.md` and `docs/CLAUDE_CODE_INTEGRATION.md`.

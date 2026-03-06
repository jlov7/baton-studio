"""Baton Studio MCP server (stub).

Implementation expectation:
- Provide a stdio MCP server that proxies to the backend HTTP API (localhost:8787 by default).
- Support dynamic tool updates (optional).
- Validate payloads against the schemas in docs/MCP_SPEC.md.

This starter pack intentionally does not include a full MCP implementation;
the build agent should implement it using an MCP SDK.
"""

from __future__ import annotations

def main() -> None:
    raise SystemExit(
        "MCP server not implemented yet. See docs/MCP_SPEC.md and implement stdio MCP server."
    )

if __name__ == "__main__":
    main()

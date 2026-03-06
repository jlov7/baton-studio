# Troubleshooting

## Backend won’t start
- Ensure Python 3.11+
- `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -e .[dev]`
- `uvicorn baton_substrate.api.main:app --reload --port 8787`

## Frontend won’t start
- Ensure Node 20+
- `cd frontend && npm install && npm run dev`

## UI shows “Disconnected”
- Backend must be running on port 8787
- Confirm `GET http://localhost:8787/health` returns 200
- Confirm the UI points to correct base URL (`NEXT_PUBLIC_BATON_API_BASE`)

## WebSocket not updating
- Ensure UI connects to `ws://localhost:8787/ws?mission_id=...`
- Check browser console for WS errors

## MCP server “Connection closed”
- Confirm MCP server runs under stdio transport
- Ensure `claude mcp list` shows baton server healthy
- If on Windows native, wrap npx/commands with `cmd /c` (Claude Code requirement)

## Agent teams not appearing
- Ensure `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Try in-process mode first (no tmux)

## Graph rendering slow
- Limit node count by:
  - collapsing evidence nodes
  - filtering to “recent”
  - virtualizing timeline

## Demo is nondeterministic
- Demo mode must set a fixed seed.
- Persist demo events to `dist/` for replay tests.

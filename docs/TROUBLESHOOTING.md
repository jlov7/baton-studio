# Troubleshooting

## Backend won't start
- Ensure Python 3.11+ and [uv](https://docs.astral.sh/uv/) are installed
- `cd backend && uv sync --dev && uv run uvicorn baton_substrate.api.main:app --reload --port 8787`

## Frontend won't start
- Ensure Node 20+ and [pnpm](https://pnpm.io/) are installed
- `cd frontend && pnpm install && pnpm dev`

## UI shows "Backend Offline"
- Backend must be running on port 8787
- Confirm `GET http://localhost:8787/health` returns `{"ok": true}`
- The UI defaults to `NEXT_PUBLIC_API_URL=http://localhost:8787`

## WebSocket not updating
- Ensure UI connects to `ws://localhost:8787/ws?mission_id=...`
- Check browser console for WS errors
- The UI defaults to `NEXT_PUBLIC_WS_URL=ws://localhost:8787`

## MCP server "Connection closed"
- Confirm MCP server runs under stdio transport
- Ensure `claude mcp list` shows baton server healthy
- Backend must be running before the MCP server can proxy calls

## Agent teams not appearing
- Ensure `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Try in-process mode first (no tmux)

## Graph rendering slow
- Limit node count by filtering with the lens dropdown
- The timeline virtualizes large event lists automatically

## Tests failing
- Backend: `cd backend && uv sync --dev && uv run pytest -v`
- Frontend lint: `cd frontend && pnpm lint && pnpm typecheck`
- E2E: Start `make dev` first, then `make e2e`

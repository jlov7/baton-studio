# Troubleshooting

## Backend will not start

- Confirm Python 3.11+ and `uv` are installed.
- Run `cd backend && uv sync --dev`.
- Start the API directly with `uv run uvicorn baton_substrate.api.main:app --reload --port 8787`.

## Frontend will not start

- Confirm Node 20+ and `pnpm` are installed.
- Run `cd frontend && pnpm install --frozen-lockfile`.
- Start the UI directly with `pnpm dev`.

## UI shows "Backend Offline"

- Confirm `http://localhost:8787/health` returns `{"ok": true}`.
- The frontend defaults to `NEXT_PUBLIC_API_URL=http://localhost:8787`.
- If you changed ports, restart the frontend with matching `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_WS_URL`.

## `make check` fails on a fresh clone

- `make check` installs backend dev dependencies, frontend dependencies, and MCP test dependencies automatically.
- If it still fails, rerun the failing subcommand directly to isolate the surface:

```bash
cd backend && uv sync --extra dev && uv run pytest -q
cd frontend && pnpm install --frozen-lockfile && pnpm lint && pnpm typecheck
cd mcp_server && uv sync --extra dev && uv run pytest -q
```

## `make e2e` fails before tests start

- Make sure ports `3000` and `8787` are free, or stop any conflicting local servers.
- Install Playwright browsers if this machine has never run the suite:

```bash
cd frontend && pnpm exec playwright install chromium
```

- `make e2e` starts its own backend and frontend and uses `dist/playwright-e2e.sqlite` for test isolation.

## MCP server exits or cannot connect

- Start the backend first with `make dev`.
- Run the server directly with `uv run --project mcp_server baton-mcp-server`.
- If the backend is elsewhere, set `BATON_BACKEND_URL`.

## Demo mission or exports look empty

- Load the demo mission from Mission Control before opening World, Graph, or Timeline.
- Mission-pack exports are `.zip` files containing `mission_pack.json`.
- Imported mission packs appear in the same UI flow as live demo missions.

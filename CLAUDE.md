# Baton Studio

## Quick Reference
- Backend: `cd backend && uv run uvicorn baton_substrate.api.main:app --reload --port 8787`
- Frontend: `cd frontend && pnpm dev`
- Both: `make dev`
- Check: `make check` (ruff, mypy, pytest, eslint, tsc)
- E2E: `make e2e` (Playwright)
- Demo: `make demo`

## Architecture
- **Backend**: FastAPI + SQLite (async via aiosqlite/SQLAlchemy) on port 8787
- **Frontend**: Next.js 15 + React 18 + Tailwind + React Flow + Framer Motion on port 3000
- **MCP Server**: Python stdio server proxying to backend HTTP API

## Conventions
- Python: uv for env/deps, ruff for lint/format, mypy strict, pytest-asyncio
- Node: pnpm for deps, TypeScript strict, Tailwind CSS, ESLint next/core-web-vitals
- All API payloads are JSON, all IDs are prefixed strings (mis_, evt_, prop_, etc.)
- Append-only event log: every mutation emits an event to the events table + WebSocket

## Key Specs
- `docs/PRD.md` — product requirements
- `docs/API_SPEC.md` — HTTP/WS API contract
- `docs/DATA_MODEL.md` — SQLite schema
- `docs/UX_SPEC.md` — UI specification
- `docs/MCP_SPEC.md` — MCP tool definitions

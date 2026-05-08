# Baton Studio

Local-first agent operations room: a shared substrate for multi-agent work with a typed world model, causal graph, energy budget, baton arbitration, replayable events, import/export, MCP, and a production-ready control-room UI.

[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Node](https://img.shields.io/badge/node-20%2B-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

## Why It Exists

Most agent systems lose the plot because state is scattered across prompts, logs, scratch files, and tool calls. Baton Studio gives agents and humans one shared operational substrate:

- **World model**: typed entities with immutable versions
- **Causal graph**: evidence, decisions, plans, artifacts, and invalidation edges
- **Baton arbitration**: one writer at a time for high-consequence commits
- **Energy budget**: explicit spend/lease pressure instead of hidden agent churn
- **Event replay**: append-only timeline for debugging and audit
- **MCP surface**: agents can read, propose, claim, commit, and spend through tools

The default mode is frictionless and local. Production mode adds scoped bearer tokens, CORS hardening, security headers, readiness checks, and metrics without requiring a cloud dependency.

## Screens

### Mission Control

![Mission Control](assets/ui/mission-control.png)

### World Model

![World Model](assets/ui/world-model.png)

### Causal Graph

![Causal Graph](assets/ui/causal-graph.png)

## Quickstart

Prerequisites:

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Node 20+
- [pnpm](https://pnpm.io/)

```bash
git clone https://github.com/jlov7/baton-studio.git
cd baton-studio
make dev
```

Open [http://localhost:3000](http://localhost:3000), click `Load Demo Mission`, then inspect Mission, World, Graph, Timeline, and Export.

If port `3000` is occupied:

```bash
cd frontend
NEXT_PUBLIC_API_URL=http://127.0.0.1:8787 \
NEXT_PUBLIC_WS_URL=ws://127.0.0.1:8787 \
pnpm exec next dev -p 3100
```

## Commands

```bash
make dev      # backend + frontend in watch mode
make check    # backend ruff/format/full mypy/tests + frontend audit/lint/typecheck + MCP tests
make audit    # backend, frontend, and MCP dependency vulnerability audit
make e2e      # self-started Playwright suite with isolated test DB; refreshes assets/ui/*.png
make demo     # writes dist/demo_pack.zip and builds the frontend
```

Current quality bar:

- backend tests: 83 passing
- MCP tests: 8 passing
- Playwright E2E: 21 passing
- full backend mypy: passing
- frontend typecheck/lint/build: passing
- backend/frontend/MCP dependency audits: passing

## Production Mode

Local mode is unauthenticated. Production mode requires bearer auth.

```bash
export BATON_ENV=production
export BATON_API_KEY="$(openssl rand -hex 32)"
export BATON_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
make dev
```

Scoped team tokens are supported:

```bash
export BATON_ENV=production
export BATON_API_KEYS="read-token:reader,ops-token:operator,admin-token:admin"
```

Roles:

- `reader`: read HTTP routes, WebSocket subscription, metrics
- `operator`: reader plus mutating mission operations
- `admin`: operator plus mission import and admin-compatible access

`BATON_API_KEY` remains a compatibility shortcut and is treated as `admin`.

Frontend production auth is intentionally explicit. Only expose `NEXT_PUBLIC_BATON_API_KEY` in trusted internal deployments:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8787 \
NEXT_PUBLIC_WS_URL=ws://localhost:8787 \
NEXT_PUBLIC_BATON_API_KEY="$BATON_API_KEY" \
pnpm --dir frontend build
```

## Docker

Create a `.env` from [.env.example](.env.example), set a real token, then run:

```bash
docker compose up --build
```

Services:

- frontend: [http://localhost:3000](http://localhost:3000)
- backend: [http://localhost:8787](http://localhost:8787)
- readiness: [http://localhost:8787/ready](http://localhost:8787/ready)

The default compose file uses a named Docker volume for SQLite at `/data/baton.sqlite`. For Postgres, set `BATON_DATABASE_URL` to an async SQLAlchemy URL and run migrations before serving.

## Operations

Backend health surfaces:

- `GET /health`: mode and high-level readiness
- `GET /ready`: database/auth readiness, returns `503` when not ready
- `GET /metrics`: Prometheus-style runtime counters and request duration totals

Production responses include:

- `x-request-id`
- `x-content-type-options: nosniff`
- `referrer-policy: no-referrer`
- `x-frame-options: DENY`
- HSTS in production

Mission packs are zip files containing exactly one `mission_pack.json` with `schema_version: 1`. Import validates zip shape, uncompressed size, nested payload shape, duplicate mission IDs, and schema version before writing.

## Architecture

![Architecture](assets/diagrams/architecture.svg)

### Write Protocol

![Write Protocol](assets/diagrams/write-protocol.svg)

### Baton Arbitration

![Baton Arbitration](assets/diagrams/baton-arbitration.svg)

### Data Model

![Data Model](assets/diagrams/data-model.svg)

Detailed specs:

- [PRODUCT.md](PRODUCT.md)
- [DESIGN.md](DESIGN.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/API_SPEC.md](docs/API_SPEC.md)
- [docs/DATA_MODEL.md](docs/DATA_MODEL.md)
- [docs/MCP_SPEC.md](docs/MCP_SPEC.md)
- [docs/UX_SPEC.md](docs/UX_SPEC.md)
- [docs/ACCEPTANCE_CHECKLIST.md](docs/ACCEPTANCE_CHECKLIST.md)

## MCP Integration

Start the backend first, then register the MCP server from another project:

```bash
claude mcp add baton-studio -- \
  uv run --project /absolute/path/to/baton-studio/mcp_server \
  baton-mcp-server
```

Production/authenticated backend:

```bash
BATON_BACKEND_URL=http://localhost:8787 \
BATON_API_KEY="$BATON_API_KEY" \
claude mcp add baton-studio -- \
  uv run --project /absolute/path/to/baton-studio/mcp_server \
  baton-mcp-server
```

MCP tools are documented in [docs/MCP_SPEC.md](docs/MCP_SPEC.md) and implemented in [mcp_server/main.py](mcp_server/main.py).

## Repo Layout

```text
backend/        FastAPI substrate server, migrations, simulator, services, pytest suite
frontend/       Next.js control-room app, typed API client, Playwright suite
mcp_server/     Stdio MCP bridge that proxies to the backend HTTP API
assets/         Brand assets, diagrams, generated UI screenshots
docs/           Product, architecture, API, UX, MCP, troubleshooting, acceptance docs
scripts/        Repo utilities such as diagram rendering
```

## Regenerating Artifacts

```bash
./scripts/render_diagrams.sh
make e2e
```

## Development Notes

- Backend tests live in [backend/tests](backend/tests).
- Frontend E2E tests live in [frontend/tests](frontend/tests).
- MCP tests live in [mcp_server/tests](mcp_server/tests).
- Active engineering notes live in [.codex](.codex).

For contribution workflow and common issues, see [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

# Contributing to Baton Studio

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Node 20+
- [pnpm](https://pnpm.io/)

## First Run

```bash
git clone <repo-url> baton-studio
cd baton-studio
make dev
```

This starts:

- Backend at `http://localhost:8787`
- Frontend at `http://localhost:3000`

## Repo Shape

```text
backend/        FastAPI app, demo simulator, services, pytest suite
frontend/       Next.js UI, Playwright suite, generated screenshots
mcp_server/     Stdio MCP server entrypoint and smoke tests
docs/           Product, architecture, API, UX, troubleshooting
assets/         Brand assets, diagrams, UI screenshots
scripts/        Utility scripts such as diagram rendering
```

## Quality Gates

Run these before sending a PR:

```bash
make check
make audit
make e2e
```

What they do:

- `make check` installs what it needs and runs backend lint/format/typecheck/tests, frontend lint/typecheck, and MCP smoke tests.
- `make audit` runs backend, frontend, and MCP dependency audits.
- `make e2e` self-starts backend and frontend, runs Playwright against an isolated test DB, and refreshes `assets/ui/*.png`.

For release artifacts:

```bash
make demo
```

That writes `dist/demo_pack.zip` and performs a production frontend build.

## Workflow Expectations

- Keep changes scoped to the task at hand.
- Add or update tests for behavior changes.
- Update docs when commands, artifacts, or public behavior changes.
- For UI changes, run `make e2e` and review the regenerated screenshots in `assets/ui/`.

## MCP Server

The MCP entrypoint is `baton-mcp-server` from [mcp_server/pyproject.toml](mcp_server/pyproject.toml). Run it locally with:

```bash
uv run --project mcp_server baton-mcp-server
```

## Pull Requests

Before opening a PR:

- Ensure `make check` passes.
- Ensure `make audit` passes.
- Ensure `make e2e` passes.
- Run `docker compose config` when deployment files changed.
- Include screenshots for UI changes if the rendered UI changed.
- Mention any docs or artifact updates in the PR summary.

## Useful Docs

- [README.md](README.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/API_SPEC.md](docs/API_SPEC.md)
- [docs/MCP_SPEC.md](docs/MCP_SPEC.md)
- [docs/QUALITY_BURN_DOWN.md](docs/QUALITY_BURN_DOWN.md)
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

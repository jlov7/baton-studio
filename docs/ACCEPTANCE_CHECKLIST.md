# Acceptance Checklist (Definition of Done)

## Product
- [ ] First run: loads a demo mission in one click
- [ ] Start simulation: baton holder changes at least once
- [ ] World Model view: shows typed entities + version history
- [ ] Causal Graph view: shows nodes + edges, clickable inspector
- [ ] Timeline view: shows events + scrub replay
- [ ] Export Mission Pack: produces a zip that can be re-imported

## Engineering
- [ ] `make dev` works
- [ ] `make check` passes (backend + frontend)
- [ ] `make e2e` passes (Playwright smoke tests)
- [ ] `make demo` generates artifacts in `dist/`

## Integration
- [ ] Claude Code can add MCP server (stdio)
- [ ] `baton.health` tool works
- [ ] `baton.read_world` returns world snapshot
- [ ] Agents can propose + commit with baton arbitration

## UX polish
- [ ] Baton transfer animation is visible and tasteful
- [ ] Energy drain animations and per-agent bars render cleanly
- [ ] Empty states always have a clear CTA
- [ ] Keyboard shortcuts work for graph search and timeline navigation

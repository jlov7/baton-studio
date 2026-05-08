# Baton Studio Product Context

## Register

product

## Product Purpose

Baton Studio is a local-first operations room for coordinating AI agent teams through shared typed state, causal provenance, energy budgets, baton-based write arbitration, and replayable event logs. It should make agent coordination legible enough for builders to trust during real work and vivid enough for technical leaders to understand in a live demo.

## Primary Users

- AI builders and operator-engineers coordinating multiple coding, research, or analysis agents.
- Technical leads reviewing what changed, who changed it, why it changed, and which downstream assumptions became stale.
- OSS evaluators deciding whether the substrate is credible from a fresh clone.

## Core Jobs

- Load or create a mission quickly, then see the health of the agent team at a glance.
- Understand who holds the baton, who is queued, and whether writes are safe to commit.
- Inspect the world model as typed, versioned state rather than prose.
- Read the causal graph as a provenance map, including contradictions and stale chains.
- Replay the event log for debugging, postmortems, and demos.
- Export and import mission packs without losing provenance.

## Strategic Principles

- Local-first must feel like a strength, not a limitation.
- The UI is an operational instrument, not a generic dashboard or marketing page.
- State changes should be visible, explainable, and reversible through replay.
- Production mode should add trust boundaries without breaking the one-click demo.
- Every screen should answer: what is happening, why it matters, and what should happen next.

## Tone

Precise, sober, high-agency, technical, and confident. Avoid SaaS fluff, novelty copy, and speculative hype. The system should feel like a serious instrument for people doing expensive work.

## Anti-References

- Generic dark admin dashboards with flat cards and tiny empty canvases.
- AI-purple gradients, decorative glass, or motion that does not explain state.
- Landing-page theatrics inside the working product.
- Hidden demo magic that cannot be inspected or replayed.

## Success Bar

A first-time evaluator can load the demo in under a minute, understand baton arbitration and causal invalidation without reading docs, inspect a real entity/version/event, and leave with confidence that the substrate could coordinate real agent work.

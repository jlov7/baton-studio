# Baton Studio — Substrate-native Coordination (internal whitepaper)

## Thesis
Multi-agent systems that coordinate primarily through **text passing** will hit a ceiling:
- typed structure becomes untyped prose
- contradictions accumulate
- coordination cost becomes token cost

The next stage is **substrate-native coordination**:
agents coordinate through shared, typed, auditable structures.

## The primitives
1) Shared World Model (typed state with invariants + history)  
2) Shared Causal Graph (explicit dependencies + attribution)  
3) Shared Energy Pool (budget-aware arbitration)  
4) Baton Arbitration (explicit right-to-write transfer)

## Why this matters for enterprise
- auditability: every state change is attributable
- debuggability: explicit dependency chains let you find root causes
- cost control: budgets are first-class (not after-the-fact invoices)
- resilience: inconsistent beliefs can be detected structurally (not via “clarifying” messages)

## Positioning
Baton Studio is not “another agent framework.”  
It is an *infrastructure-level coordination substrate* that agent teams can plug into.

## How it fits with Claude Code
Claude Code’s agent teams provide parallelism + messaging + shared tasks. Baton Studio adds:
- shared typed state
- provenance graph
- budget arbitration
- explicit conflict resolution

This is a plausible “next layer” above today’s multi-agent toolchains.

# Baton Studio Design Context

## Scene

An AI engineer is coordinating several autonomous coding and research agents on a 27-inch monitor late in a dim room, watching for contention, stale assumptions, and expensive mistakes while staying in flow.

## Color Strategy

Restrained product palette with a few semantic signal colors. Use OKLCH tokens. The surface is warm charcoal, not pure black. Baton amber, energy cyan, continuity green, and risk red are state colors, not decoration.

## Typography

Use a high-quality system/product sans stack for UI text and a tuned monospace stack for IDs, event payloads, schema fragments, timestamps, and numerical telemetry. Keep labels compact and readable. Do not use decorative display fonts in controls or data surfaces.

## Layout Language

- Product-first control room: persistent navigation, mission HUD, primary canvas, route-scoped inspector.
- Favor clear bands, dividers, and spatial grouping over nested cards.
- Use denser information where it helps operators scan, but give the graph and replay surfaces enough space to breathe.
- Mobile should collapse into a usable single-column console, not a squeezed desktop.

## Motion

Motion explains state. Baton transfer, queue movement, event replay, loading skeletons, graph focus, and inspector transitions may animate. Avoid page-load choreography, bounce/elastic easing, and scroll effects in the core app.

## Component Principles

- Every interactive element needs default, hover, focus, active, disabled, and loading states.
- Empty states must show the next action.
- Graph lenses and timeline filters must visibly change the data, not just selected button styling.
- Code and JSON payloads should be readable, clipped safely, and copyable when useful.

## Visual Signature

Quiet technical intensity: warm black surfaces, fine grid lines, tabular data, high contrast active states, precise borders, subtle noise, and stateful color used sparingly. Avoid generic SaaS gradients and identical card grids.

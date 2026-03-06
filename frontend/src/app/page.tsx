export default function Home() {
  return (
    <main style={{ padding: 24, fontFamily: "ui-sans-serif, system-ui" }}>
      <h1 style={{ fontSize: 32, marginBottom: 8 }}>Baton Studio</h1>
      <p style={{ opacity: 0.8, maxWidth: 720 }}>
        Starter UI scaffold. Implement Mission Control, World Model, Causal Graph, and Baton/Energy HUD per docs/UX_SPEC.md.
      </p>
      <div style={{ marginTop: 24, padding: 16, border: "1px solid rgba(255,255,255,0.12)", borderRadius: 12 }}>
        <strong>Next step:</strong> run <code>make dev</code> after Codex completes the build.
      </div>
    </main>
  );
}

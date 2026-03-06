# Claude Code integration

Baton Studio integrates with Claude Code via MCP.

## 1) Enable agent teams (optional)
Agent teams are experimental. Enable via environment in Claude Code settings:

`settings.json`:
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

## 2) Add Baton MCP server

### Option A (stdio, local)
From your project directory:
```bash
claude mcp add --transport stdio baton -- python -m mcp_server.main
```

If your MCP server needs env:
```bash
claude mcp add --transport stdio --env BATON_BACKEND_URL=http://localhost:8787 baton -- python -m mcp_server.main
```

### Option B (HTTP, remote)
If you deploy MCP server remotely:
```bash
claude mcp add --transport http baton https://your-domain.example/mcp
```

## 3) Verify in Claude Code
Inside Claude Code, run:
- `/mcp` to see server status
- ask Claude to call `baton.health`

## 4) Recommended agent team prompt
Create an agent team:
- Lead: “Mission Controller”
- Teammate 1: “Planner”
- Teammate 2: “Critic”
- Teammate 3: “Researcher”

Instruction:
- All agents must read the world model before acting.
- Use propose/commit with baton arbitration.
- Add causal edges for every decision.

## 5) Privacy defaults
Baton Studio is local-first.
- Demo mode runs with simulated agents.
- Real mode uses your Claude Code session’s own auth.
- Avoid exporting raw prompts in Mission Packs.

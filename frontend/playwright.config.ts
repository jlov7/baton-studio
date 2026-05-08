import path from "node:path";
import { defineConfig } from "@playwright/test";

const repoRoot = path.resolve(__dirname, "..");
const backendDir = path.join(repoRoot, "backend");
const frontendDir = path.join(repoRoot, "frontend");
const distDir = path.join(repoRoot, "dist");
const e2eDbPath = path.join(distDir, "playwright-e2e.sqlite");
const e2eDbUrl = `sqlite+aiosqlite:///${e2eDbPath}`;

function quote(value: string): string {
  return `"${value.replace(/(["\\$`])/g, "\\$1")}"`;
}

export default defineConfig({
  testDir: "./tests",
  timeout: 60_000,
  fullyParallel: false,
  workers: 1,
  use: {
    baseURL: "http://127.0.0.1:3100",
    trace: "retain-on-failure",
  },
  webServer: [
    {
      command: [
        `mkdir -p ${quote(distDir)}`,
        `rm -f ${quote(e2eDbPath)}`,
        `cd ${quote(backendDir)}`,
        "uv sync --extra dev",
        `BATON_DATABASE_URL=${quote(e2eDbUrl)} uv run uvicorn baton_substrate.api.main:app --host 127.0.0.1 --port 8787`,
      ].join(" && "),
      url: "http://127.0.0.1:8787/health",
      reuseExistingServer: !process.env.CI,
      timeout: 180_000,
    },
    {
      command: `cd ${quote(frontendDir)} && pnpm install --frozen-lockfile && NEXT_PUBLIC_API_URL=http://127.0.0.1:8787 NEXT_PUBLIC_WS_URL=ws://127.0.0.1:8787 pnpm exec next dev -p 3100`,
      url: "http://127.0.0.1:3100/mission",
      reuseExistingServer: !process.env.CI,
      timeout: 180_000,
    },
  ],
});

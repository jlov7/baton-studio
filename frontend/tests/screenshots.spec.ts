import fs from "node:fs";
import path from "node:path";
import { test, expect } from "@playwright/test";
import { loadDemoMission } from "./helpers";

const screenshotsDir = path.resolve(process.cwd(), "../assets/ui");

function screenshotPath(name: string): string {
  fs.mkdirSync(screenshotsDir, { recursive: true });
  return path.join(screenshotsDir, name);
}

test.describe("Release screenshots", () => {
  test("captures mission control, world model, and causal graph", async ({ page }) => {
    await loadDemoMission(page);

    await expect(page.getByText("Squad")).toBeVisible();
    await page.screenshot({
      path: screenshotPath("mission-control.png"),
      fullPage: true,
    });

    await page.locator("nav").getByText("World").click();
    await expect(page.getByText("Entity Types")).toBeVisible();
    await page.screenshot({
      path: screenshotPath("world-model.png"),
      fullPage: true,
    });

    await page.locator("nav").getByText("Graph").click();
    await expect(page.getByText(/\d+ nodes/)).toBeVisible();
    await page.screenshot({
      path: screenshotPath("causal-graph.png"),
      fullPage: true,
    });
  });
});

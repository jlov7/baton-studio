import { test, expect } from "@playwright/test";
import { loadDemoAndSimulate } from "./helpers";

test.describe("Causal Graph - Empty State", () => {
  test("shows no mission message", async ({ page }) => {
    await page.goto("/graph");
    await expect(page.getByText("No Mission Loaded")).toBeVisible();
  });
});

test.describe("Causal Graph - After Simulation", () => {
  test("renders graph with nodes and edges", async ({ page }) => {
    await loadDemoAndSimulate(page);

    // Navigate to Graph
    await page.locator("nav").getByText("Graph").click();
    await expect(page).toHaveURL(/\/graph/);

    // Should show node/edge counts in toolbar
    await expect(page.getByText(/\d+ nodes/)).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(/\d+ edges/)).toBeVisible({ timeout: 5_000 });
  });
});

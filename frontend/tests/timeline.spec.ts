import { test, expect } from "@playwright/test";
import { loadDemoAndSimulate } from "./helpers";

test.describe("Timeline - Empty State", () => {
  test("shows no mission message", async ({ page }) => {
    await page.goto("/timeline");
    await expect(page.getByText("No Mission Loaded")).toBeVisible();
  });
});

test.describe("Timeline - After Simulation", () => {
  test("shows events in the stream", async ({ page }) => {
    await loadDemoAndSimulate(page);

    // Navigate to Timeline
    await page.locator("nav").getByText("Timeline").click();
    await expect(page).toHaveURL(/\/timeline/);

    // Should show event count
    await expect(page.getByText(/\d+ events/)).toBeVisible({ timeout: 10_000 });
  });
});

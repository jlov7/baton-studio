import { test, expect } from "@playwright/test";
import { loadDemoMission } from "./helpers";

test.describe("Timeline - Empty State", () => {
  test("shows no mission message", async ({ page }) => {
    await page.goto("/timeline");
    await expect(page.getByText("No Mission Loaded")).toBeVisible();
  });
});

test.describe("Timeline - With Demo Mission", () => {
  test("shows events in the stream", async ({ page }) => {
    await loadDemoMission(page);

    await page.locator("nav").getByText("Timeline").click();
    await expect(page).toHaveURL(/\/timeline/);
    await expect(page.getByText(/\d+ events/)).toBeVisible({ timeout: 10_000 });
  });
});

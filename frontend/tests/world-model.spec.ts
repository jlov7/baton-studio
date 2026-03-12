import { test, expect } from "@playwright/test";
import { loadDemoMission } from "./helpers";

test.describe("World Model - Empty State", () => {
  test("shows no mission message", async ({ page }) => {
    await page.goto("/world");
    await expect(page.getByText("No Mission Loaded")).toBeVisible();
  });
});

test.describe("World Model - With Demo Mission", () => {
  test("shows entity types and entities", async ({ page }) => {
    await loadDemoMission(page);

    await page.locator("nav").getByText("World").click();
    await expect(page).toHaveURL(/\/world/);
    await expect(page.getByText("Entity Types")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText("Evidence")).toBeVisible({ timeout: 5_000 });
  });
});

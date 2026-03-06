import { test, expect } from "@playwright/test";
import { loadDemoAndSimulate } from "./helpers";

test.describe("World Model - Empty State", () => {
  test("shows no mission message", async ({ page }) => {
    await page.goto("/world");
    await expect(page.getByText("No Mission Loaded")).toBeVisible();
  });
});

test.describe("World Model - After Simulation", () => {
  test("shows entity types and entities", async ({ page }) => {
    await loadDemoAndSimulate(page);

    // Navigate to World
    await page.locator("nav").getByText("World").click();
    await expect(page).toHaveURL(/\/world/);

    // Entity types sidebar should show types
    await expect(page.getByText("Entity Types")).toBeVisible({ timeout: 10_000 });

    // Should have Evidence type from demo
    await expect(page.getByText("Evidence")).toBeVisible({ timeout: 5_000 });
  });
});

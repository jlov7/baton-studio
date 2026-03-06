import { test, expect } from "@playwright/test";

test.describe("Mission Control - Empty State", () => {
  test("shows empty state with load demo button", async ({ page }) => {
    await page.goto("/mission");
    await expect(page.getByText("No Mission Loaded")).toBeVisible();
    await expect(page.getByText("Load Demo Mission")).toBeVisible();
  });
});

test.describe("Mission Control - Demo Flow", () => {
  test("load demo creates mission and shows hero panel", async ({ page }) => {
    await page.goto("/mission");

    // Click Load Demo Mission
    await page.getByText("Load Demo Mission").click();

    // Wait for mission to load — hero panel title appears
    await expect(
      page.getByRole("heading", { level: 1 })
    ).toBeVisible({ timeout: 15_000 });

    // Mission title should be visible in HUD
    const hud = page.locator("header");
    await expect(hud).not.toContainText("No Mission");
  });

  test("start simulation populates squad and metrics", async ({ page }) => {
    await page.goto("/mission");
    await page.getByText("Load Demo Mission").click();

    // Wait for hero panel
    await expect(
      page.getByRole("heading", { level: 1 })
    ).toBeVisible({ timeout: 15_000 });

    // Start simulation
    await page.getByText("Start Simulation").click();

    // Wait for agents to appear in squad strip
    await expect(page.getByText("Squad")).toBeVisible({ timeout: 20_000 });

    // Should show at least one agent card
    await expect(page.getByText("Atlas")).toBeVisible({ timeout: 20_000 });

    // HUD should show running status
    await expect(page.getByText("running")).toBeVisible({ timeout: 10_000 });
  });
});

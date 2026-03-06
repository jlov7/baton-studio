import { expect, type Page } from "@playwright/test";

/**
 * Load demo mission and run simulation to completion.
 * Waits for agents to appear before returning.
 */
export async function loadDemoAndSimulate(page: Page): Promise<void> {
  await page.goto("/mission");

  // Load demo mission
  await page.getByText("Load Demo Mission").click();
  await expect(
    page.getByRole("heading", { level: 1 })
  ).toBeVisible({ timeout: 15_000 });

  // Start simulation
  await page.getByText("Start Simulation").click();

  // Wait for simulation to produce agents
  await expect(page.getByText("Atlas")).toBeVisible({ timeout: 30_000 });
}

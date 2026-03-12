import { expect, type Page } from "@playwright/test";

/**
 * Load the demo mission and wait for populated mission state.
 */
export async function loadDemoMission(page: Page): Promise<void> {
  await page.goto("/mission");

  await page.getByText("Load Demo Mission").click();
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible({
    timeout: 15_000,
  });
  await expect(page.getByText("Atlas")).toBeVisible({ timeout: 15_000 });
}

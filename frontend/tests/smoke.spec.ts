import { test, expect } from "@playwright/test";

test("home redirects to mission", async ({ page }) => {
  await page.goto("/");
  await page.waitForURL("**/mission");
  await expect(page).toHaveURL(/\/mission/);
});

test("nav rail shows all 5 links", async ({ page }) => {
  await page.goto("/mission");
  const nav = page.locator("nav");
  await expect(nav.getByText("Mission")).toBeVisible();
  await expect(nav.getByText("World")).toBeVisible();
  await expect(nav.getByText("Graph")).toBeVisible();
  await expect(nav.getByText("Timeline")).toBeVisible();
  await expect(nav.getByText("Export")).toBeVisible();
});

test("nav rail navigates between pages", async ({ page }) => {
  await page.goto("/mission");
  const nav = page.locator("nav");

  await nav.getByText("World").click();
  await expect(page).toHaveURL(/\/world/);

  await nav.getByText("Graph").click();
  await expect(page).toHaveURL(/\/graph/);

  await nav.getByText("Timeline").click();
  await expect(page).toHaveURL(/\/timeline/);

  await nav.getByText("Export").click();
  await expect(page).toHaveURL(/\/export/);

  await nav.getByText("Mission").click();
  await expect(page).toHaveURL(/\/mission/);
});

test("top HUD shows no mission initially", async ({ page }) => {
  await page.goto("/mission");
  await expect(page.getByText("No Mission")).toBeVisible();
});

test("Baton Studio branding visible", async ({ page }) => {
  await page.goto("/mission");
  // NavRail logo "B"
  await expect(page.locator("nav").getByText("B")).toBeVisible();
});

import { expect, test } from "@playwright/test";
import { loadDemoMission } from "./helpers";

test("persists active mission in URL and localStorage", async ({ page }) => {
  await loadDemoMission(page);
  await expect(page).toHaveURL(/mission=mis_/);

  const missionId = await page.evaluate(() => window.localStorage.getItem("baton.currentMissionId"));
  expect(missionId).toMatch(/^mis_/);

  await page.goto(`/world?mission=${missionId}`);
  await expect(page.getByText("Entity Types")).toBeVisible({ timeout: 10_000 });
  await expect(page.locator("header")).toContainText("Substrate-Native");
});

test("graph search and stale lens keep the canvas nonblank", async ({ page }) => {
  await loadDemoMission(page);
  await page.locator("nav").getByText("Graph").click();
  await expect(page.getByText(/\d+ nodes/)).toBeVisible({ timeout: 10_000 });

  await page.getByPlaceholder("Search nodes...").fill("ev-001");
  await expect(page.getByText(/1 nodes/)).toBeVisible();
  await expect(page.locator(".react-flow__viewport")).toBeVisible();

  await page.getByPlaceholder("Search nodes...").fill("");
  await page.getByRole("button", { name: "Stale Chain" }).click();
  await expect(page.locator(".react-flow__viewport")).toBeVisible();
});

test("timeline replay slider can scrub to zero", async ({ page }) => {
  await loadDemoMission(page);
  await page.locator("nav").getByText("Timeline").click();
  const slider = page.getByLabel("Replay position");

  await expect(slider).toBeVisible({ timeout: 10_000 });
  await slider.fill("0");
  await expect(page.getByTestId("timeline-replay-counter")).toHaveText(/^0\/\d+$/);
});

test("export uses the official POST mission pack flow", async ({ page }) => {
  await loadDemoMission(page);
  await page.locator("nav").getByText("Export").click();

  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: /Download \.zip/ }).click();
  const file = await download;

  expect(file.suggestedFilename()).toMatch(/^mis_.*\.zip$/);
});

test("mobile mission view has no horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await loadDemoMission(page);

  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  expect(overflow).toBe(false);
  await expect(page.locator("nav").getByText("Mission")).toBeVisible();
});

test("stale persisted mission is cleared after backend reset", async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem("baton.currentMissionId", "mis_missing_after_reset");
  });

  await page.goto("/mission");

  await expect(page).not.toHaveURL(/mission=mis_missing_after_reset/);
  await expect(page.getByText("Load Demo Mission")).toBeVisible();
  const storedMission = await page.evaluate(() =>
    window.localStorage.getItem("baton.currentMissionId"),
  );
  expect(storedMission).toBeNull();
});

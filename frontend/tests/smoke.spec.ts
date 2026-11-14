import { test, expect } from "@playwright/test";

test("loads the analyst workspace", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByText("NEXUS", { exact: false })).toBeVisible();
  await expect(page.getByRole("button", { name: "CSV FILE" })).toBeVisible();
  await expect(page.getByRole("button", { name: "SQLITE" })).toBeVisible();
  await expect(page.getByRole("button", { name: /LOAD SAMPLE DATA/ })).toBeVisible();
  await expect(page.getByRole("button", { name: "ANALYZE DATA" })).toBeDisabled();
});

test("guided questions update the analysis prompt", async ({ page }) => {
  await page.goto("/");

  const prompt = page.getByRole("textbox");
  await page.getByRole("button", { name: "Which product has the highest revenue?" }).click();
  await expect(prompt).toHaveValue("Which product has the highest revenue?");
});

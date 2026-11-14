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

test("sample data flows through the API into analysis results", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "LOAD SAMPLE DATA" }).click();
  await expect(page.getByText("sample_sales.csv")).toBeVisible();
  await page.getByText("USE LOCAL AI INTERPRETER").click();
  await page.getByRole("button", { name: "ANALYZE DATA" }).click();

  await expect(page.getByRole("heading", { name: "Analysis complete" })).toBeVisible({ timeout: 15000 });
  await expect(page.getByText("3 ROWS")).toBeVisible();
  await expect(page.getByText("VISUAL SUMMARY")).toBeVisible();
});

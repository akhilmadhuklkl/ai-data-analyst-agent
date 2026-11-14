import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  reporter: process.env.CI ? [["list"], ["html", { outputFolder: "playwright-report", open: "never" }]] : "list",
  use: { baseURL: "http://localhost:3000", trace: "on-first-retry" },
  webServer: process.env.CI
    ? [
        { command: "python -m uvicorn backend.main:app --port 8001", url: "http://localhost:8001/health", cwd: ".." },
        { command: "npm run dev -- --port 3000", url: "http://localhost:3000" },
      ]
    : undefined,
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});

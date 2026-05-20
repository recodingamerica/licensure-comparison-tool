import { defineConfig, devices } from "@playwright/test";

// Site-protection password the middleware checks. Tests set the same value
// in the dev-server env and pass it via httpCredentials so every request
// satisfies the Basic-auth gate. Override locally with PLAYWRIGHT_SITE_PASSWORD.
const SITE_PASSWORD = process.env.PLAYWRIGHT_SITE_PASSWORD ?? "test-pw";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? "github" : "list",

  use: {
    baseURL: "http://localhost:3100",
    // The site middleware requires Basic-auth on every page. Set the header
    // explicitly via extraHTTPHeaders so it lands on every request — page
    // navigations AND the page's own `fetch('/data/...')` calls. (Playwright's
    // `httpCredentials` only kicks in after a 401 challenge, which doesn't
    // get forwarded to XHRs by Chromium — they just silently fail.)
    extraHTTPHeaders: {
      Authorization:
        "Basic " + Buffer.from(`any:${SITE_PASSWORD}`).toString("base64"),
    },
    trace: "retain-on-failure",
    actionTimeout: 10_000,
  },

  projects: [
    {
      name: "chromium",
      // Wide viewport so AG Grid's column virtualization keeps every default
      // column in the DOM. At the default 1280px only ~7 columns render and
      // the rest are dropped; that makes header-based filter tests flaky.
      use: { ...devices["Desktop Chrome"], viewport: { width: 2400, height: 1200 } },
    },
  ],

  webServer: {
    // Use port 3100 so a `next dev` someone left running on 3000 doesn't
    // collide with the test server.
    command: `SITE_PASSWORD=${SITE_PASSWORD} npx next dev -p 3100`,
    url: "http://localhost:3100",
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    stdout: "ignore",
    stderr: "pipe",
  },
});

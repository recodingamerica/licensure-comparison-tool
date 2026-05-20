import { expect, test, type Page, type Locator } from "@playwright/test";

// ----------------------------------------------------------------------------
// E2E coverage for the per-column filter UI on the profile page.
// Tests pick `nursing` because it has the residual 4 unverified rows; on the
// other professions every row is at 0 unverified, so the multicheck would only
// show "0" as an option and there'd be nothing to filter for.
// ----------------------------------------------------------------------------

const NURSING_URL = "/profile?p=nursing";

function header(page: Page, colId: string): Locator {
  return page
    .locator(
      `.ag-header-cell[col-id="${colId}"], .ag-header-cell[data-col-id="${colId}"]`,
    )
    .first();
}

/** AG Grid virtualizes off-screen column headers out of the DOM. If the
 * column we need isn't already rendered, scroll the horizontal viewport
 * to its right edge — every column not in the initial viewport is to the
 * right of the ones that are. */
async function scrollColumnIntoView(page: Page, colId: string) {
  const sel = `.ag-header-cell[col-id="${colId}"], .ag-header-cell[data-col-id="${colId}"]`;
  if ((await page.locator(sel).count()) > 0) return;
  await page.evaluate(() => {
    const el = document.querySelector(
      ".ag-body-horizontal-scroll-viewport",
    ) as HTMLElement | null;
    if (el) el.scrollLeft = el.scrollWidth;
  });
  await page.waitForSelector(sel, { timeout: 5_000 });
}

async function openColumnFilter(page: Page, colId: string) {
  await scrollColumnIntoView(page, colId);
  await header(page, colId).locator(".ag-header-cell-filter-button").click();
  await page.waitForSelector(".ag-popup-child", { state: "visible" });
}

async function visibleRowCount(page: Page): Promise<number> {
  return page.locator(".ag-center-cols-container .ag-row").count();
}

async function unverifiedRowCount(page: Page): Promise<number> {
  return page
    .locator(".ag-center-cols-container .ag-row.ag-row-unverified")
    .count();
}

test.beforeEach(async ({ page }) => {
  await page.goto(NURSING_URL);
  // The page renders "Loading…" until /data/nursing.json fetches and the
  // grid mounts. Wait for at least one row, with a generous timeout (cold
  // first-paint can take a few seconds on `next dev`).
  await page.waitForSelector(".ag-center-cols-container .ag-row", {
    timeout: 30_000,
  });
});

test.describe("Unverified column — multicheck filter", () => {
  test("popover shows '0' and '1' as the two options", async ({ page }) => {
    await openColumnFilter(page, "evidence");
    const popup = page.locator(".ag-popup-child").last();
    // MulticheckFilter renders a stringified label per unique value. With
    // nursing's residual flagged rows we expect both "0" and "1" present.
    const labels = await popup.locator("label").allTextContents();
    expect(labels.some((l) => /\b0\b/.test(l))).toBe(true);
    expect(labels.some((l) => /\b1\b/.test(l))).toBe(true);
  });

  test("checking only '1' actually narrows the visible rows", async ({ page }) => {
    const baselineRows = await visibleRowCount(page);
    const flaggedBaseline = await unverifiedRowCount(page);
    expect(flaggedBaseline).toBeGreaterThan(0); // sanity: fixture has flagged rows
    expect(baselineRows).toBeGreaterThan(flaggedBaseline); // sanity: some unflagged

    await openColumnFilter(page, "evidence");
    const popup = page.locator(".ag-popup-child").last();
    // Find the checkbox whose adjacent label is exactly "1".
    const oneCheckbox = popup
      .locator("label", { has: page.locator("span", { hasText: /^1$/ }) })
      .locator("input[type='checkbox']");
    await oneCheckbox.check();

    // AG Grid debounces filter updates. Poll until row count drops.
    await expect
      .poll(() => visibleRowCount(page), { timeout: 5_000 })
      .toBe(flaggedBaseline);
  });
});

test.describe("MulticheckFilter (low-cardinality categorical)", () => {
  test("checking one value narrows the visible rows", async ({ page }) => {
    const baseline = await visibleRowCount(page);
    await openColumnFilter(page, "regulatory_model");
    const popup = page.locator(".ag-popup-child").last();
    const firstCheckbox = popup.locator("input[type='checkbox']").first();
    await firstCheckbox.check();
    await expect
      .poll(() => visibleRowCount(page), { timeout: 5_000 })
      .toBeLessThan(baseline);
  });
});

test.describe("Columns dropdown", () => {
  test("search narrows the list and updates 'N of M match'", async ({ page }) => {
    await page.getByRole("button", { name: /^Columns \(/ }).click();
    const menu = page.getByRole("menu");
    await expect(menu).toBeVisible();

    const totalText = await menu
      .locator("text=/\\d+ columns/")
      .first()
      .innerText();
    const totalCount = Number(totalText.match(/\d+/)?.[0] ?? "0");
    expect(totalCount).toBeGreaterThan(20);

    await menu.getByPlaceholder("Search columns…").fill("ce");
    await expect(menu.locator("text=/of \\d+ match/")).toBeVisible({
      timeout: 2_000,
    });

    const labels = await menu.locator("label span").allTextContents();
    expect(labels.length).toBeGreaterThan(0);
    for (const l of labels) {
      expect(l.toLowerCase()).toContain("ce");
    }
  });

  test("hide all acts only on the currently-filtered set", async ({ page }) => {
    const visibleBefore = Number(
      (await page
        .getByRole("button", { name: /^Columns \(/ })
        .innerText()).match(/\((\d+)\//)?.[1] ?? "0",
    );

    await page.getByRole("button", { name: /^Columns \(/ }).click();
    const menu = page.getByRole("menu");
    await menu.getByPlaceholder("Search columns…").fill("ce");
    const ceMatched = (await menu.locator("label span").allTextContents()).length;
    expect(ceMatched).toBeGreaterThan(0);

    await menu.getByRole("button", { name: "hide all" }).click();

    const visibleAfter = Number(
      (await page
        .getByRole("button", { name: /^Columns \(/ })
        .innerText()).match(/\((\d+)\//)?.[1] ?? "0",
    );
    expect(visibleBefore - visibleAfter).toBeLessThanOrEqual(ceMatched);
    expect(visibleBefore - visibleAfter).toBeGreaterThanOrEqual(1);
  });
});

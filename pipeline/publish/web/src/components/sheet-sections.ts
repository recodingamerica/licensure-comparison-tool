/**
 * The state-detail Sheet's section names.
 *
 * These are the join between two files: profile-view declares which section a column
 * points at (colDef `context.section`), and state-detail-dialog renders the heading.
 * Held as bare strings in both, renaming a heading would silently break that column's
 * filter — the same drift the colId->label override table used to cause, just across a
 * file boundary instead of within one.
 *
 * Its own module rather than living in state-detail-dialog, so the grid can name a
 * section without importing the whole Sheet.
 */
export const SHEET_SECTION = {
  baseLicensure: "Base licensure",
  exams: "Exams",
  disciplinaryGrounds: "Disciplinary grounds",
  scopeOfPractice: "Scope of practice",
} as const;

export type SheetSectionName = (typeof SHEET_SECTION)[keyof typeof SHEET_SECTION];

/**
 * Typed constructors for a column's click target.
 *
 * AG Grid types `colDef.context` as `any`, so writing `context: { section: "Exmas" }`
 * compiles happily and the filter silently never matches. Going through these makes the
 * typo a compile error — the point of naming the sections at all.
 */
export const sectionTarget = (section: SheetSectionName) => ({ section });
export const fieldTarget = (fieldPath: string) => ({ fieldPath });

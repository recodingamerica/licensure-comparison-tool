export function humanize(s: string | null | undefined): string {
  if (!s) return "";
  return String(s).replace(/_/g, " ").trim();
}

// Prettify a dotted field path into a title-cased leaf label. When the leaf is
// a generic word (required/available/…), prefix it with its parent so e.g.
// "licensure.exam.required" reads "Exam required" instead of just "Required".
// Shared by the analysis views (novel-policies, compare).
const GENERIC_LEAVES = new Set([
  "required", "available", "exists", "offered", "permitted",
  "authorized", "prohibited", "allowed", "excluded", "type",
]);
export function fieldLabel(f: string): string {
  const parts = f.split(".");
  let leaf = parts[parts.length - 1];
  if (GENERIC_LEAVES.has(leaf) && parts.length >= 2) {
    leaf = `${parts[parts.length - 2]}_${leaf}`;
  }
  const s = leaf.replace(/_/g, " ");
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// Format a raw stringified field value for display: booleans → yes/no, whole
// numbers ("7.0") → "7", everything else de-underscored.
export function formatFieldValue(v: string): string {
  if (v === "true") return "yes";
  if (v === "false") return "no";
  const n = Number(v);
  if (v.trim() !== "" && Number.isInteger(n)) return String(n);
  return v.replace(/_/g, " ");
}

// Max chars of quoted text to put in the URL fragment. Short prefixes are
// more reliable — long quotes are more likely to hit a rendering difference
// somewhere along their length that breaks the verbatim match.
const FRAGMENT_PREFIX_MAX = 80;
const FRAGMENT_PREFIX_MIN = 30;

/**
 * Build a Justia link that scrolls to (and yellow-highlights) the quoted
 * clause on arrival, using a URL Text Fragment (`#:~:text=...`). Supported
 * in Chrome, Edge, and Safari; Firefox ignores the fragment and lands on
 * the section page, which is fine — that's the same behavior as the bare
 * link today.
 *
 * The snippet comes from `source.text` (our scrape, which is closest to
 * what Justia renders), sliced by the first verified `quote_span`. We cap
 * at ~80 chars and trim to a word boundary because the matcher is
 * verbatim — any single rendering difference along the snippet breaks
 * the scroll, so shorter is safer.
 *
 * Returns the bare URL whenever we don't have enough to build a fragment.
 */
export function citationUrlWithFragment(
  url: string | undefined,
  sourceText: string | undefined,
  spans: Array<[number, number]> | undefined,
): string {
  if (!url) return "";
  if (!sourceText || !spans || spans.length === 0) return url;
  const [start, end] = spans[0];
  let snippet = sourceText.slice(start, Math.min(end, start + FRAGMENT_PREFIX_MAX));
  // Text fragments match against rendered text, where any whitespace run
  // collapses to a single space. Mirror that so our snippet matches what
  // the browser sees on Justia.
  snippet = snippet.replace(/\s+/g, " ").trim();
  // Trim back to the last word boundary so we don't end mid-word — a
  // dangling partial word is more likely to differ from Justia's render
  // (hyphenation, abbreviation breaks) than a clean word.
  const lastSpace = snippet.lastIndexOf(" ");
  if (lastSpace >= FRAGMENT_PREFIX_MIN) snippet = snippet.slice(0, lastSpace);
  if (snippet.length < FRAGMENT_PREFIX_MIN) return url;
  return `${url}#:~:text=${encodeURIComponent(snippet)}`;
}

// ----------------------------------------------------------------------------
// Highlight rendering.
//
// The quote-finding logic now lives in Python — pipeline/extract/locate_quote.py
// computes (start, end) offsets against the EXACT section text that
// pipeline/publish/build_frontend.py emits, and ships them on each Evidence
// node as `quote_spans`. This module just slices the rendered string at those
// offsets so the yellow <mark> covers the same characters Python's verifier
// accepted. One matcher, no parity test.
// ----------------------------------------------------------------------------

export type HighlightPart = { kind: "text" | "mark"; value: string };

/**
 * Render `text` as a sequence of plain/marked parts using pre-computed
 * char-offset spans. When `spans` is missing or empty, returns the text
 * as a single plain part (no highlight). Span pairs are assumed to be
 * non-overlapping and in ascending order — that's the contract
 * locate_quote_in_section guarantees.
 */
export function highlightSpans(
  text: string,
  spans: Array<[number, number]> | undefined,
): HighlightPart[] {
  if (!spans || spans.length === 0) return [{ kind: "text", value: text }];
  const parts: HighlightPart[] = [];
  let pos = 0;
  for (const [start, end] of spans) {
    if (start > pos) parts.push({ kind: "text", value: text.slice(pos, start) });
    parts.push({ kind: "mark", value: text.slice(start, end) });
    pos = end;
  }
  if (pos < text.length) parts.push({ kind: "text", value: text.slice(pos) });
  return parts;
}

/**
 * Find every position of `query` in `text`, case-insensitive, returning
 * `[start, end]` spans into the ORIGINAL text. Non-overlapping, in ascending
 * order — the contract `highlightSpans` expects.
 *
 * Intentionally plain substring matching, not the smart-quote / list-marker
 * normalization used by `locate_quote_in_section`. Users typing into the
 * Statute-text filter expect literal matches: typing "podiatrist" finds
 * "podiatrist", not "podiatry" or "podiatrists". Substring match also
 * matches what AG Grid's built-in `agTextColumnFilter` does for the row-
 * filter pass, so the table inclusion and the Sheet highlights agree.
 */
export function findAllSpans(
  query: string,
  text: string,
): Array<[number, number]> {
  const q = query.trim().toLowerCase();
  if (!q || !text) return [];
  const hay = text.toLowerCase();
  const spans: Array<[number, number]> = [];
  let from = 0;
  // Bound the result set so a query like "a" against a 500 KB section
  // doesn't allocate a million spans. The first 500 highlights are plenty
  // of signal — anything more is just visual noise.
  const MAX = 500;
  while (spans.length < MAX) {
    const idx = hay.indexOf(q, from);
    if (idx < 0) break;
    spans.push([idx, idx + q.length]);
    from = idx + q.length;
  }
  return spans;
}

export type SearchSnippet = {
  before: string;  // up to `contextChars` of text before the match
  match: string;   // the matched text, verbatim from the source
  after: string;   // up to `contextChars` of text after the match
};

/**
 * For every occurrence of `query` in `text`, return a snippet of context
 * around it. Used by the Sheet's "Statute text matches" panel so users can
 * see WHERE their search hits live without scrolling through the full
 * section text. Caps at `maxSnippets` because rendering all 500 spans of
 * "a" is useless.
 */
export function searchSnippets(
  query: string,
  text: string,
  contextChars = 70,
  maxSnippets = 50,
): SearchSnippet[] {
  const spans = findAllSpans(query, text).slice(0, maxSnippets);
  return spans.map(([start, end]) => ({
    before: text.slice(Math.max(0, start - contextChars), start),
    match: text.slice(start, end),
    after: text.slice(end, Math.min(text.length, end + contextChars)),
  }));
}

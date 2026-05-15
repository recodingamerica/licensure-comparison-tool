export function humanize(s: string | null | undefined): string {
  if (!s) return "";
  return String(s).replace(/_/g, " ").trim();
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

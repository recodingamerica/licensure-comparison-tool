export function humanize(s: string | null | undefined): string {
  if (!s) return "";
  return String(s).replace(/_/g, " ").trim();
}

// ----------------------------------------------------------------------------
// Quote / source normalization — MUST stay in lock-step with
// pipeline/extract/extract_state.py:_normalize_for_match (Python).
//
// Both sides do:
//   1. lowercase
//   2. map smart quotes / em-dashes / NBSPs to ASCII
//   3. strip parenthesized list markers (1) (a) (iv) — surgically, before
//      the non-alnum strip, so they don't become bare "1"/"a"/"i" tokens
//   4. drop everything non-alphanumeric to spaces
//   5. collapse whitespace
//
// The Python verifier uses the result to decide if a quote was faithfully
// drawn from the source; the UI highlighter uses it to find WHERE in the
// original source to paint the yellow mark. Diverging behavior between the
// two means a quote that "verifies" wouldn't highlight, which is the bug
// this comment is trying to prevent.
// ----------------------------------------------------------------------------

const SMART_MAP: Record<string, string> = {
  // curly single quotes
  "‘": "'",
  "’": "'",
  "‚": "'",
  "‛": "'",
  // curly double quotes
  "“": '"',
  "”": '"',
  "„": '"',
  "‟": '"',
  // dashes
  "–": "-",
  "—": "-",
  "−": "-",
  // odd spaces -> regular space
  " ": " ",
  " ": " ",
  " ": " ",
  " ": " ",
  // ellipsis -> three dots
  "…": "...",
};

// Matches the Python regex: \(\s*(?:\d{1,3}|[a-z]|[ivxIVX]+)\s*\)
const LIST_MARKER_RE = /\(\s*(?:\d{1,3}|[a-z]|[ivxIVX]+)\s*\)/gi;

/**
 * Normalize text the same way Python does, AND keep a mapping from each
 * output character back to its source-text index so callers can find where
 * in the original a normalized match landed.
 *
 * Returns:
 *   normalized — the lowercased / stripped / collapsed text
 *   srcIndex   — srcIndex[i] is the index in the original text that
 *                normalized[i] came from. Length equals normalized.length.
 */
function normalizeWithMapping(text: string): { normalized: string; srcIndex: number[] } {
  // Step 1: strip parenthesized list markers, but track which positions in the
  // intermediate string came from which positions in the original. We process
  // chars one at a time, skipping over the marker entirely when we see one.
  type Slot = { ch: string; src: number };
  const stage1: Slot[] = [];
  let i = 0;
  while (i < text.length) {
    // Look for a list marker starting at i
    LIST_MARKER_RE.lastIndex = 0;
    const probe = text.slice(i, i + 12); // markers are short
    const m = probe.match(/^\(\s*(?:\d{1,3}|[a-z]|[ivxIVX]+)\s*\)/i);
    if (m) {
      i += m[0].length;
      continue;
    }
    let ch = text[i];
    // smart-char map (length 1, except ellipsis -> 3)
    if (SMART_MAP[ch] !== undefined) {
      const mapped = SMART_MAP[ch];
      for (let k = 0; k < mapped.length; k++) {
        stage1.push({ ch: mapped[k], src: i });
      }
    } else {
      stage1.push({ ch, src: i });
    }
    i++;
  }

  // Step 2: lowercase, replace non-[a-z0-9 ] with space, collapse whitespace
  const out: string[] = [];
  const idx: number[] = [];
  let lastWasSpace = true; // suppress leading space
  for (const slot of stage1) {
    let c = slot.ch.toLowerCase();
    if (!/[a-z0-9 ]/.test(c)) c = " ";
    if (c === " ") {
      if (lastWasSpace) continue;
      lastWasSpace = true;
      out.push(" ");
      idx.push(slot.src);
    } else {
      lastWasSpace = false;
      out.push(c);
      idx.push(slot.src);
    }
  }
  // Trim trailing space
  while (out.length && out[out.length - 1] === " ") {
    out.pop();
    idx.pop();
  }
  return { normalized: out.join(""), srcIndex: idx };
}

export function normalizeForMatch(text: string): string {
  return normalizeWithMapping(text).normalized;
}

/**
 * Find the verbatim quote (after the same normalization the Python verifier
 * uses) inside the original source text, and return text-or-mark parts so
 * the highlighted region in the rendered UI matches the region the Python
 * verifier accepted.
 */
export function highlightInText(
  text: string,
  quote: string
): Array<{ kind: "text" | "mark"; value: string }> {
  if (!quote) return [{ kind: "text", value: text }];
  const { normalized: normSource, srcIndex } = normalizeWithMapping(text);
  const { normalized: normQuote } = normalizeWithMapping(quote);
  if (!normQuote) return [{ kind: "text", value: text }];
  const idx = normSource.indexOf(normQuote);
  if (idx < 0) return [{ kind: "text", value: text }];
  // Map normalized [idx, idx+len) back to source positions.
  const startSrc = srcIndex[idx];
  const lastNormPos = idx + normQuote.length - 1;
  const endSrc = srcIndex[lastNormPos] + 1; // exclusive in source
  return [
    { kind: "text", value: text.slice(0, startSrc) },
    { kind: "mark", value: text.slice(startSrc, endSrc) },
    { kind: "text", value: text.slice(endSrc) },
  ];
}

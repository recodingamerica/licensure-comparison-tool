// Multi-layer span renderer used by both /browse views.
//
// Given a block of text plus two kinds of spans — Evidence quote spans
// (amber, hover = field name + value) and search-query spans (yellow) —
// produces a sequence of RenderPart elements the React side can map over
// without re-running the matcher.
//
// Search wins ties: when an evidence span and a search match cover the
// same character range, the user's active query is the more salient
// signal so we render it yellow.
//
// Pure data → data; no JSX. Lives outside the per-view client components
// so both consume the same logic.

import type { BrowseEvidence } from "@/lib/types";

export type RenderPart =
  | { kind: "text"; value: string }
  | { kind: "evidence"; value: string; evs: BrowseEvidence[] }
  | { kind: "search"; value: string };

/**
 * @param text         The original section text to split.
 * @param evidenceSpans Flat list of {start, end, ev} — one entry per
 *                     evidence-span. Multiple evidence rows may overlap
 *                     the same range (when different fields share a
 *                     source quote); renderLayered keeps both.
 * @param searchSpans  Flat list of [start, end] pairs from findAllSpans.
 */
export function renderLayered(
  text: string,
  evidenceSpans: Array<{ start: number; end: number; ev: BrowseEvidence }>,
  searchSpans: Array<[number, number]>,
): RenderPart[] {
  type Char = { evs: BrowseEvidence[]; search: boolean };
  const chars: Char[] = Array.from({ length: text.length }, () => ({
    evs: [],
    search: false,
  }));
  for (const { start, end, ev } of evidenceSpans) {
    for (let i = start; i < end && i < text.length; i++) {
      if (!chars[i].evs.includes(ev)) chars[i].evs.push(ev);
    }
  }
  for (const [start, end] of searchSpans) {
    for (let i = start; i < end && i < text.length; i++) {
      chars[i].search = true;
    }
  }

  // Run-key — combines field_path + profession (the latter is only set
  // on state-browse evidence; absent on per-prof). Identical key means a
  // run continues; a change means a new <mark> tag with distinct tooltip.
  const key = (evs: BrowseEvidence[]): string =>
    evs
      .map((e) => `${e.field_path}@${e.profession ?? ""}`)
      .sort()
      .join("\x1f");

  const parts: RenderPart[] = [];
  let i = 0;
  while (i < text.length) {
    const c = chars[i];
    const kind: "text" | "evidence" | "search" = c.search
      ? "search"
      : c.evs.length > 0
        ? "evidence"
        : "text";
    const startKey = kind === "evidence" ? key(c.evs) : "";
    let j = i + 1;
    while (j < text.length) {
      const c2 = chars[j];
      const k2 = c2.search ? "search" : c2.evs.length > 0 ? "evidence" : "text";
      if (k2 !== kind) break;
      if (kind === "evidence" && key(c2.evs) !== startKey) break;
      j++;
    }
    parts.push({
      kind,
      value: text.slice(i, j),
      ...(kind === "evidence" ? { evs: c.evs.slice() } : {}),
    } as RenderPart);
    i = j;
  }
  return parts;
}

/**
 * Flatten section.evidence into the {start, end, ev} shape renderLayered
 * wants. One section's worth of evidence can yield many spans (multi-
 * range matches via locate_quote_in_section's ellipsis-split logic).
 */
export function flattenEvidenceSpans(
  evidence: BrowseEvidence[],
): Array<{ start: number; end: number; ev: BrowseEvidence }> {
  const out: Array<{ start: number; end: number; ev: BrowseEvidence }> = [];
  for (const ev of evidence) {
    for (const [s, e] of ev.spans) {
      out.push({ start: s, end: e, ev });
    }
  }
  out.sort((a, b) => a.start - b.start || a.end - b.end);
  return out;
}

/** Tiny display helpers used by the tooltip + tree-node leaf labels. */
export function shortFieldPath(p: string): string {
  if (p.startsWith("licensure.")) return p.slice("licensure.".length);
  if (p.startsWith("profession_specific.")) return p.slice("profession_specific.".length);
  if (p.startsWith("scope.")) return p.slice("scope.".length);
  return p;
}

export function formatEvidenceValue(v: unknown): string {
  if (v === null || v === undefined) return "—";
  if (Array.isArray(v)) return v.map(String).join(", ");
  return String(v);
}

"use client";

import { createContext, useContext, useEffect, useRef, useState } from "react";
import type { Evidence, SectionRef } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { SEMANTIC_CLASSES as SC } from "@/lib/web-colors";
import {
  humanize,
  highlightSpans,
  citationUrlWithFragment,
  findAllSpans,
} from "@/lib/format";
import { ExternalLink, ChevronDown, ChevronRight } from "lucide-react";

// Shared context for the active "Statute text" search query. Set at the
// Sheet level so we don't have to thread the prop through ~27 EvidenceRow
// call sites. When non-empty, the "in context" panel below each evidence
// row highlights occurrences of this string instead of the LLM quote span.
export const SearchQueryContext = createContext<string>("");

// The row the user clicked through to (#34): the Sheet sets this to the
// EvidenceRow `label` matching the grid column that was clicked. The matching
// row scrolls itself into view, highlights, and auto-expands its statute text.
// Context (like SearchQueryContext) so we don't thread a prop through every
// call site. Null when the Sheet was opened without a specific field focus.
export const FocusFieldContext = createContext<string | null>(null);

// Per-state bucket labels keyed by EvidenceRow `label` (#34): the same
// normalized tag the grid shows above bucketed cells (e.g. issuing_authority's
// "Dedicated Dietetics Board"). Empty for rows with no bucket.
export const BucketContext = createContext<Record<string, string>>({});

type Props = {
  label: string;
  ev: Evidence | null | undefined;
  sections: Record<string, SectionRef>;
};

function formatValue(v: unknown): React.ReactNode {
  if (Array.isArray(v))
    return v.length ? (
      v.map(String).map(humanize).join(", ")
    ) : (
      <span className="text-muted-foreground">—</span>
    );
  if (typeof v === "boolean") return v ? "yes" : "no";
  if (v === null || v === undefined || v === "")
    return <span className="text-muted-foreground">—</span>;
  return humanize(String(v));
}

export function EvidenceRow({ label, ev, sections }: Props) {
  const focusField = useContext(FocusFieldContext);
  const focused = focusField !== null && focusField === label;
  // When this row is the click-through target, expand its statute context by
  // default so the user lands on the value AND its source text in one step.
  const [open, setOpen] = useState(focused);
  const searchQuery = useContext(SearchQueryContext);
  const bucket = useContext(BucketContext)[label];
  const rowRef = useRef<HTMLDivElement>(null);

  // Scroll the focused row into the middle of the Sheet after it paints. The
  // Sheet slides in via a transform, so defer past that with rAF to land on
  // the right final position.
  useEffect(() => {
    if (!focused) return;
    const id = requestAnimationFrame(() => {
      rowRef.current?.scrollIntoView({ block: "center", behavior: "smooth" });
    });
    return () => cancelAnimationFrame(id);
  }, [focused]);

  if (!ev) return null;

  const cite = ev.citation || "";
  const source =
    sections[cite] || sections[cite.replace(/^\[|\]$/g, "")] || null;
  const unverified = !!ev.unverified;
  // Strict verifier failed but fuzzy fallback found a long contiguous
  // substring. Different visual treatment than bare-unverified so the
  // user can see "we think this is the source, but the wording shifts."
  const approximate = ev.approximate;

  // If the user has an active "Statute text" search, prefer THEIR highlight
  // — overlay every occurrence of the query on the source text. Otherwise
  // fall back to the LLM-extracted quote span (the existing behavior).
  const hasSearch = searchQuery.trim().length > 0;
  const searchSpans = hasSearch && source?.text
    ? findAllSpans(searchQuery, source.text)
    : [];
  const usingSearch = hasSearch && searchSpans.length > 0;
  const parts = source?.text
    ? highlightSpans(
        source.text,
        usingSearch ? searchSpans : ev.quote_spans,
      )
    : null;
  const deepLinkUrl = citationUrlWithFragment(source?.url, source?.text, ev.quote_spans);

  return (
    <div
      ref={rowRef}
      data-field={label}
      className={
        "grid grid-cols-[160px_1fr] md:grid-cols-[180px_1fr] gap-x-3 py-2 border-b border-border/60 last:border-0 scroll-mt-4 " +
        (focused
          ? "rounded-md ring-2 ring-sky-400 bg-sky-50/60 -mx-2 px-2"
          : "")
      }
    >
      <code className="text-xs text-muted-foreground font-mono pt-1 break-all">{label}</code>
      <div className="space-y-1.5">
        {bucket && (
          <Badge
            variant="outline"
            className={`self-start font-mono text-[10px] px-1.5 py-0 ${SC.attention.bg} ${SC.attention.text} ${SC.attention.border}`}
          >
            {bucket}
          </Badge>
        )}
        <div className="font-medium text-sm flex items-center gap-2">
          {formatValue(ev.value)}
          {unverified && approximate && (
            <Badge
              variant="secondary"
              className={`${SC.attention.bg} ${SC.attention.text} ${SC.attention.hoverBg} text-[10px] font-mono uppercase tracking-wide`}
              title={`${Math.round(approximate.ratio * 100)}% of this quote appears word-for-word in the statute; the rest differs (usually a phrase the model shortened). Flags the quote wording — not whether the value is correct.`}
            >
              ~{Math.round(approximate.ratio * 100)}% verbatim
            </Badge>
          )}
          {unverified && !approximate && (
            <Badge
              variant="secondary"
              className={`${SC.attention.bg} ${SC.attention.text} ${SC.attention.hoverBg} text-[10px] font-mono uppercase tracking-wide`}
              title="This quote isn't a word-for-word span of the statute — the model paraphrased or compressed the wording. Flags the quote text, not whether the value is correct."
            >
              quote not verbatim
            </Badge>
          )}
        </div>
        {unverified && (
          <p className="text-[11px] not-italic text-muted-foreground leading-snug">
            {approximate
              ? `Most of this quote (${Math.round(approximate.ratio * 100)}%) appears word-for-word in the statute; the rest differs — usually a phrase the model shortened.`
              : "This quote isn't a word-for-word span of the statute — the model paraphrased or compressed the wording."}{" "}
            It flags the <em>quote wording</em>, not whether the value is correct
            {source?.text ? (
              <>
                {" — use "}
                <span className="font-medium">in context</span>
                {" below to compare against the statute."}
              </>
            ) : (
              "."
            )}
          </p>
        )}
        <div
          className={
            "text-xs px-3 py-2 rounded border-l-2 italic " +
            (unverified
              ? `${SC.attention.border} ${SC.attention.bg}`
              : "border-sky-400 bg-muted/40")
          }
        >
          “{ev.quote}”{" "}
          {source?.url ? (
            <a
              href={deepLinkUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="not-italic font-mono text-sky-700 hover:text-sky-900 hover:underline text-[10px] ml-1"
              title={`Open ${cite} on Justia`}
            >
              [{cite}]
            </a>
          ) : (
            <span className="not-italic font-mono text-muted-foreground text-[10px] ml-1">
              [{cite}]
            </span>
          )}
        </div>
        {approximate && (
          <div className={`text-[11px] not-italic px-3 py-1.5 rounded ${SC.attention.bg} border ${SC.attention.border} ${SC.attention.text}`}>
            <span className="font-mono uppercase tracking-wide text-[9px] mr-2">
              longest verbatim run found in statute
            </span>
            “…{approximate.matched_normalized}…”
          </div>
        )}
        {source && (
          <div className="flex items-center gap-3 text-xs">
            {source.url && (
              <a
                href={deepLinkUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-foreground inline-flex items-center gap-1"
              >
                source <ExternalLink className="size-3" />
              </a>
            )}
            {source.text && (
              <button
                onClick={() => setOpen(!open)}
                className="text-muted-foreground hover:text-foreground inline-flex items-center gap-1"
              >
                {open ? <ChevronDown className="size-3" /> : <ChevronRight className="size-3" />}
                {open ? "hide context" : "in context"}
              </button>
            )}
          </div>
        )}
        {open && parts && (
          <div className="mt-1 text-[12px] leading-relaxed bg-muted/30 border rounded p-3 max-h-72 overflow-y-auto whitespace-pre-wrap">
            {parts.map((p, i) =>
              p.kind === "mark" ? (
                <mark
                  key={i}
                  className={
                    usingSearch
                      ? // User's search match — yellow so it's visually
                        // distinct from the existing LLM-quote highlight.
                        "bg-yellow-300 px-0.5 rounded-sm"
                      : "bg-amber-200/60 px-0.5 rounded-sm"
                  }
                >
                  {p.value}
                </mark>
              ) : (
                <span key={i}>{p.value}</span>
              )
            )}
          </div>
        )}
      </div>
    </div>
  );
}

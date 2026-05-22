"use client";

import { createContext, useContext, useState } from "react";
import type { Evidence, SectionRef } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
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
  const [open, setOpen] = useState(false);
  const searchQuery = useContext(SearchQueryContext);
  if (!ev) return null;

  const cite = ev.citation || "";
  const source =
    sections[cite] || sections[cite.replace(/^\[|\]$/g, "")] || null;
  const unverified = !!ev.unverified;

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
    <div className="grid grid-cols-[160px_1fr] md:grid-cols-[180px_1fr] gap-x-3 py-2 border-b border-border/60 last:border-0">
      <code className="text-xs text-muted-foreground font-mono pt-1 break-all">{label}</code>
      <div className="space-y-1.5">
        <div className="font-medium text-sm flex items-center gap-2">
          {formatValue(ev.value)}
          {unverified && (
            <Badge
              variant="secondary"
              className="bg-amber-100 text-amber-900 hover:bg-amber-100 text-[10px] font-mono uppercase tracking-wide"
              title="Quote did not match source via regex"
            >
              unverified
            </Badge>
          )}
        </div>
        <div
          className={
            "text-xs px-3 py-2 rounded border-l-2 italic " +
            (unverified
              ? "border-amber-400 bg-amber-50/50"
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

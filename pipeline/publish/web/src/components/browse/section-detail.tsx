"use client";

// Shared section-detail pane used by both /browse views. Renders the
// citation + Justia link header, caller-provided badges, and the full
// section text with overlapping amber-evidence + yellow-search
// highlights wired through the shadcn Tooltip.
//
// The two views differ in WHICH badges they render (per-prof shows
// scope_layer / applies_to / claim count; per-state shows audience /
// profession / claim count), so badges come in as a JSX prop and the
// shared component stays presentation-pure.

import { useMemo } from "react";
import type { BrowseEvidence } from "@/lib/types";
import { findAllSpans } from "@/lib/format";
import {
  renderLayered,
  flattenEvidenceSpans,
  shortFieldPath,
  formatEvidenceValue,
} from "@/lib/render-layered";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

/** Minimal shape both browse views' sections satisfy. */
export type DetailSection = {
  url: string;
  citation: string;
  label: string;
  text: string;
  evidence: BrowseEvidence[];
};

export function SectionDetail({
  section,
  searchQuery,
  badges,
}: {
  section: DetailSection;
  searchQuery: string;
  /** Audience/scope badges to render below the citation header. The two
   *  browse views build their own (scope_layer vs audience), so this
   *  shared component just slots them in. */
  badges?: React.ReactNode;
}) {
  const evidenceSpans = useMemo(
    () => flattenEvidenceSpans(section.evidence),
    [section.evidence],
  );
  const searchHits = useMemo(
    () => findAllSpans(searchQuery, section.text),
    [searchQuery, section.text],
  );
  const parts = useMemo(
    () => renderLayered(section.text, evidenceSpans, searchHits),
    [section.text, evidenceSpans, searchHits],
  );

  return (
    <article className="px-8 py-6 max-w-4xl mx-auto">
      <header className="mb-4">
        <h2 className="text-lg font-medium flex items-baseline gap-3 flex-wrap">
          <span className="font-mono">{section.citation}</span>
          <a
            href={section.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-mono text-muted-foreground hover:text-foreground underline"
          >
            Justia ↗
          </a>
        </h2>
        <p className="text-xs text-muted-foreground mt-0.5">{section.label}</p>
        {badges && (
          <div className="flex items-center gap-2 mt-2 flex-wrap">{badges}</div>
        )}
      </header>

      <TooltipProvider delay={150}>
        <div className="text-sm leading-relaxed whitespace-pre-wrap">
          {parts.map((p, i) => {
            if (p.kind === "text") return <span key={i}>{p.value}</span>;
            if (p.kind === "search") {
              return (
                <mark key={i} className="bg-yellow-300 rounded-sm">
                  {p.value}
                </mark>
              );
            }
            const evs = p.evs;
            return (
              <Tooltip key={i}>
                <TooltipTrigger
                  render={
                    <mark className="bg-amber-200/60 rounded-sm">
                      {p.value}
                    </mark>
                  }
                />
                <TooltipContent
                  className="bg-popover text-popover-foreground border shadow-lg max-w-lg p-3 text-[13px] leading-snug"
                  side="top"
                >
                  <div className="space-y-3">
                    {evs.map((e, j) => (
                      <div key={j} className={j > 0 ? "pt-3 border-t" : ""}>
                        <div className="flex items-baseline justify-between gap-2">
                          <div className="font-mono text-[11px] uppercase tracking-wide text-muted-foreground">
                            {shortFieldPath(e.field_path)}
                          </div>
                          {e.profession && (
                            <div className="font-mono text-[10px] text-muted-foreground">
                              {e.profession.replace(/_/g, " ")}
                            </div>
                          )}
                        </div>
                        <div className="font-semibold mt-0.5">
                          {formatEvidenceValue(e.value)}
                          {e.unverified && (
                            <span className="ml-1.5 font-normal text-amber-700 text-[11px]">
                              unverified
                            </span>
                          )}
                        </div>
                        {e.quote && (
                          <div className="italic text-muted-foreground mt-1 text-[12px]">
                            &ldquo;{e.quote}&rdquo;
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </TooltipContent>
              </Tooltip>
            );
          })}
        </div>
      </TooltipProvider>
    </article>
  );
}

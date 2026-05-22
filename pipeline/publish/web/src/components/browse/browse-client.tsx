"use client";

// Two-pane document browser:
//   left  — hierarchy tree, sections grouped by scope_layer
//   right — selected section's full text, with two highlight layers:
//             amber  — every quote_span where the LLM drew an extracted
//                      claim from this section (hover for field name)
//             yellow — every search hit (when the search input has a query)
//
// Selected section is carried in the URL as ?cite=<section-citation> so
// links are shareable. Filter bar across the top has the layer chips +
// the search input; both narrow the tree (sections without matches fall
// out) and drive highlights in the right pane.

import { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { Group, Panel, Separator } from "react-resizable-panels";
import type { BrowseSection, BrowseEvidence } from "@/lib/types";
import { findAllSpans } from "@/lib/format";
import { Input } from "@/components/ui/input";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Search } from "lucide-react";

// Short-form for an evidence field path. The full dotted path
// ("licensure.continuing_education.hours_per_period") is too long for
// list rendering, but the last segment alone loses context. Compromise:
// drop the leading "licensure." (the most common prefix), keep the rest.
function shortFieldPath(p: string): string {
  if (p.startsWith("licensure.")) return p.slice("licensure.".length);
  if (p.startsWith("profession_specific.")) return p.slice("profession_specific.".length);
  if (p.startsWith("scope.")) return p.slice("scope.".length);
  return p;
}

type LayerKey = "practice" | "umbrella_enumeration" | "umbrella_universal";

const LAYER_LABEL: Record<LayerKey, string> = {
  practice: "Practice act",
  umbrella_enumeration: "Umbrella (this profession)",
  umbrella_universal: "Umbrella (universal)",
};

const LAYER_DOT: Record<LayerKey, string> = {
  practice: "bg-sky-500",
  umbrella_enumeration: "bg-emerald-500",
  umbrella_universal: "bg-purple-500",
};

const LAYER_TINT: Record<LayerKey, string> = {
  practice: "border-sky-200",
  umbrella_enumeration: "border-emerald-200",
  umbrella_universal: "border-purple-200",
};

export function BrowseClient({
  state,
  profession,
  sections,
}: {
  state: string;
  profession: string;
  sections: BrowseSection[];
}) {
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();

  const [query, setQuery] = useState<string>(params.get("q") ?? "");
  const [activeLayers, setActiveLayers] = useState<Set<LayerKey>>(
    () => new Set(["practice", "umbrella_enumeration", "umbrella_universal"]),
  );

  // Selected section's citation (the unique-ish key from BrowseSection).
  // Reflected in the URL so links survive reload.
  const selectedCite = params.get("cite") ?? "";

  // Filter sections: layer chips AND search query (substring in text or citation).
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return sections.filter((s) => {
      if (!activeLayers.has(s.scope_layer)) return false;
      if (!q) return true;
      return (
        (s.text || "").toLowerCase().includes(q) ||
        (s.citation || "").toLowerCase().includes(q) ||
        (s.label || "").toLowerCase().includes(q)
      );
    });
  }, [sections, activeLayers, query]);

  // Group filtered sections by layer for tree rendering.
  const grouped = useMemo(() => {
    const g: Record<LayerKey, BrowseSection[]> = {
      practice: [],
      umbrella_enumeration: [],
      umbrella_universal: [],
    };
    for (const s of filtered) g[s.scope_layer as LayerKey].push(s);
    return g;
  }, [filtered]);

  // Default-select the first filtered section so the right pane is never
  // empty after a search narrows the tree.
  const selected: BrowseSection | null = useMemo(() => {
    if (selectedCite) {
      const hit = filtered.find((s) => s.citation === selectedCite);
      if (hit) return hit;
    }
    return filtered[0] ?? null;
  }, [filtered, selectedCite]);

  const setUrl = (patch: Record<string, string | null>) => {
    const next = new URLSearchParams(params.toString());
    for (const [k, v] of Object.entries(patch)) {
      if (v === null || v === "") next.delete(k);
      else next.set(k, v);
    }
    router.replace(`${pathname}?${next.toString()}`, { scroll: false });
  };

  const handleSearch = (v: string) => {
    setQuery(v);
    setUrl({ q: v || null });
  };

  const handleSelect = (s: BrowseSection) => setUrl({ cite: s.citation });

  const toggleLayer = (k: LayerKey) => {
    setActiveLayers((prev) => {
      const next = new Set(prev);
      if (next.has(k)) next.delete(k);
      else next.add(k);
      return next;
    });
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Header / breadcrumbs */}
      <header className="border-b px-6 py-3 flex items-center gap-3 flex-wrap bg-background">
        <Link href="/" className="text-xs font-mono text-muted-foreground hover:text-foreground">
          home
        </Link>
        <span className="text-xs text-muted-foreground">›</span>
        <Link
          href={`/profile?p=${encodeURIComponent(profession)}`}
          className="text-xs font-mono text-muted-foreground hover:text-foreground"
        >
          {profession.replace(/_/g, " ")}
        </Link>
        <span className="text-xs text-muted-foreground">›</span>
        <span className="text-xs font-mono font-medium">{state}</span>
        <span className="text-xs text-muted-foreground ml-2">
          browsing {sections.length} sections
        </span>
      </header>

      {/* Filter bar */}
      <div className="border-b px-6 py-2.5 flex items-center gap-3 flex-wrap bg-muted/30">
        {(() => {
          const layersPresent = (Object.keys(LAYER_LABEL) as LayerKey[]).filter(
            (k) => sections.some((s) => s.scope_layer === k),
          );
          // With only one layer there's nothing to filter between — clicking
          // the chip would just hide everything. Show a quiet text label
          // instead. Multi-layer states get the real chip filter.
          if (layersPresent.length <= 1) {
            const k = layersPresent[0];
            if (!k) return null;
            const count = sections.filter((s) => s.scope_layer === k).length;
            return (
              <span className="text-xs flex items-center gap-1.5 text-muted-foreground">
                <span className={`w-2 h-2 rounded-full ${LAYER_DOT[k]}`} />
                {LAYER_LABEL[k]}{" "}
                <span className="font-mono">{count}</span>
              </span>
            );
          }
          return (
            <ToggleGroup variant="outline" size="sm" spacing={1}>
              {layersPresent.map((k) => {
                const count = sections.filter((s) => s.scope_layer === k).length;
                const on = activeLayers.has(k);
                return (
                  <ToggleGroupItem
                    key={k}
                    pressed={on}
                    onPressedChange={() => toggleLayer(k)}
                    className="text-xs gap-1.5 px-2.5"
                  >
                    <span className={`w-2 h-2 rounded-full ${LAYER_DOT[k]}`} />
                    {LAYER_LABEL[k]}
                    <span className="font-mono text-muted-foreground">{count}</span>
                  </ToggleGroupItem>
                );
              })}
            </ToggleGroup>
          );
        })()}
        <div className="ml-auto relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 size-3.5 text-muted-foreground pointer-events-none" />
          <Input
            type="search"
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="search this state's statute…"
            className="pl-8 w-72 h-8 text-xs"
          />
        </div>
      </div>

      {/* Two-pane body — resizable via react-resizable-panels. The
          Separator drags. */}
      <Group
        orientation="horizontal"
        className="flex-1 overflow-hidden flex"
      >
        <Panel defaultSize="28%" minSize="18%" maxSize="50%" className="overflow-y-auto py-2 border-r">
          {(Object.keys(LAYER_LABEL) as LayerKey[]).map((k) => {
            const items = grouped[k];
            if (items.length === 0) return null;
            return (
              <div key={k} className="mb-3">
                <div className="px-4 py-1 text-[10px] font-mono uppercase tracking-widest text-muted-foreground flex items-center gap-1.5">
                  <span className={`w-1.5 h-1.5 rounded-full ${LAYER_DOT[k]}`} />
                  {LAYER_LABEL[k]}
                </div>
                <ul>
                  {items.map((s) => {
                    const active = selected?.citation === s.citation;
                    return (
                      <li key={`${s.scope_layer}-${s.citation}-${s.url}`}>
                        <button
                          type="button"
                          onClick={() => handleSelect(s)}
                          className={
                            "w-full text-left px-4 py-1.5 text-xs hover:bg-muted/50 border-l-2 " +
                            (active
                              ? "bg-muted/70 border-foreground"
                              : `border-transparent ${LAYER_TINT[k]}`)
                          }
                        >
                          <span className="font-mono text-foreground truncate block">
                            {s.citation || s.label || "(no citation)"}
                          </span>
                          {s.evidence.length > 0 && (
                            <span
                              className="text-[10px] text-muted-foreground truncate block"
                              title={s.evidence.map((e) => e.field_path).join(", ")}
                            >
                              {Array.from(
                                new Set(s.evidence.map((e) => shortFieldPath(e.field_path))),
                              ).join(", ")}
                            </span>
                          )}
                        </button>
                      </li>
                    );
                  })}
                </ul>
              </div>
            );
          })}
          {filtered.length === 0 && (
            <p className="px-4 py-6 text-xs text-muted-foreground italic">
              No sections match the current filters.
            </p>
          )}
        </Panel>
        <Separator className="w-1 bg-border hover:bg-foreground/20 transition-colors" />
        <Panel defaultSize="72%" minSize="50%" className="overflow-y-auto">
          {selected ? (
            <SectionDetail section={selected} searchQuery={query} />
          ) : (
            <p className="p-8 text-sm text-muted-foreground italic">
              Select a section from the tree.
            </p>
          )}
        </Panel>
      </Group>
    </div>
  );
}

// Right-pane: full section text with two highlight layers. Built by walking
// the text once, applying both quote-evidence spans (amber, hover = field
// name) and search-query spans (yellow). Overlapping ranges resolve in
// favor of the search highlight — the user's active query is the more
// salient signal.
function SectionDetail({
  section,
  searchQuery,
}: {
  section: BrowseSection;
  searchQuery: string;
}) {
  const evidenceSpans: Array<{ start: number; end: number; ev: BrowseEvidence }> = [];
  for (const ev of section.evidence) {
    for (const [s, e] of ev.spans) {
      evidenceSpans.push({ start: s, end: e, ev });
    }
  }
  evidenceSpans.sort((a, b) => a.start - b.start || a.end - b.end);

  const searchHits = useMemo(
    () => findAllSpans(searchQuery, section.text),
    [searchQuery, section.text],
  );

  // Merge into a single layered render. Approach: build a sorted list of
  // events (start/end with class), walk through text linearly. Search
  // wins ties by getting placed later in the sort order.
  const parts = useMemo(
    () => renderLayered(section.text, evidenceSpans, searchHits),
    // section.text + evidenceSpans + searchHits change in lockstep
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [section.text, searchQuery],
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
        <div className="flex items-center gap-2 mt-2 flex-wrap">
          <Badge variant="outline" className="font-mono text-[10px] gap-1.5">
            <span className={`w-1.5 h-1.5 rounded-full ${LAYER_DOT[section.scope_layer as LayerKey]}`} />
            {LAYER_LABEL[section.scope_layer as LayerKey]}
          </Badge>
          {section.applies_to && section.applies_to.length > 0 && (
            <Badge variant="secondary" className="font-mono text-[10px]">
              applies to {section.applies_to.map((p) => p.replace(/_/g, " ")).join(", ")}
            </Badge>
          )}
          {section.evidence.length > 0 && (
            <Badge
              variant="outline"
              className="font-mono text-[10px] bg-amber-100/60 text-amber-900 border-amber-300"
              title="Each claim is an LLM-extracted field whose quote was found in this section. Multiple claims can share the same quote text — hover an amber span to see all of them."
            >
              {section.evidence.length} claim{section.evidence.length === 1 ? "" : "s"} drawn from this section
            </Badge>
          )}
        </div>
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
            // p.kind === "evidence" — multiple claims may share this span;
            // tooltip lists each one with field, value (the label we gave
            // it), and the verbatim quoted text.
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
                        <div className="font-mono text-[11px] uppercase tracking-wide text-muted-foreground">
                          {shortFieldPath(e.field_path)}
                        </div>
                        <div className="font-semibold mt-0.5">
                          {formatVal(e.value)}
                          {e.unverified && (
                            <span className="ml-1.5 font-normal text-amber-700 text-[11px]">unverified</span>
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

function formatVal(v: unknown): string {
  if (v === null || v === undefined) return "—";
  if (Array.isArray(v)) return v.map(String).join(", ");
  return String(v);
}

type RenderPart =
  | { kind: "text"; value: string }
  | { kind: "evidence"; value: string; evs: BrowseEvidence[] }
  | { kind: "search"; value: string };

// Layered span renderer. Search highlights take priority where they overlap
// with evidence highlights; non-overlapping ranges render independently.
// Multiple evidence rows can cover the same characters (different fields
// drawing from the same quote) — we track ALL of them per char so the
// tooltip can list every claim, not just the first one to land.
function renderLayered(
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
      // Dedup: if the same Evidence already lands here, don't add twice.
      if (!chars[i].evs.includes(ev)) chars[i].evs.push(ev);
    }
  }
  for (const [start, end] of searchSpans) {
    for (let i = start; i < end && i < text.length; i++) {
      chars[i].search = true;
    }
  }

  // Build a stable key for an evs[] so we can detect "same set of claims
  // covering this run" without comparing arrays char-by-char each step.
  const key = (evs: BrowseEvidence[]): string =>
    evs.map((e) => e.field_path).sort().join("\x1f");

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
      // Same kind — for evidence, require the same set of claims so a
      // boundary where one Evidence ends but another keeps going produces
      // separate <mark> spans (different tooltip content).
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

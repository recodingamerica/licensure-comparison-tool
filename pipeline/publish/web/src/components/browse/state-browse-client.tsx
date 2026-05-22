"use client";

// State-level browse: every regulation that touches a licensed profession
// in this state, grouped by audience. Sibling of the per-profession
// BrowseClient — same two-pane shape, same detail-panel rendering, but
// the tree groups by audience (universal / multi-prof / single-prof)
// and the filter is profession-multi-select instead of layer-toggle.

import { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { Group, Panel, Separator } from "react-resizable-panels";
import type { StateBrowsePayload, StateBrowseSection } from "@/lib/state-browse-types";
import type { BrowseEvidence } from "@/lib/types";
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

function shortFieldPath(p: string): string {
  if (p.startsWith("licensure.")) return p.slice("licensure.".length);
  if (p.startsWith("profession_specific.")) return p.slice("profession_specific.".length);
  if (p.startsWith("scope.")) return p.slice("scope.".length);
  return p;
}

const AUDIENCE_LABEL: Record<StateBrowseSection["audience"], string> = {
  universal: "Applies to everyone",
  multi: "Shared with multiple professions",
  single: "Profession-specific",
};

const AUDIENCE_DOT: Record<StateBrowseSection["audience"], string> = {
  universal: "bg-purple-500",
  multi: "bg-emerald-500",
  single: "bg-sky-500",
};

export function StateBrowseClient({ payload }: { payload: StateBrowsePayload }) {
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();

  const allProfessions = payload.professions_available;
  const [query, setQuery] = useState<string>(params.get("q") ?? "");

  // Profession multi-select: defaults to all enabled (show everything).
  // URL param `profs=podiatry,nursing` carries the active subset.
  const urlProfs = (params.get("profs") || "").split(",").filter(Boolean);
  const [activeProfs, setActiveProfs] = useState<Set<string>>(
    () => new Set(urlProfs.length > 0 ? urlProfs : allProfessions),
  );

  const selectedCite = params.get("cite") ?? "";

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

  const handleSelect = (s: StateBrowseSection) => setUrl({ cite: s.citation });

  const toggleProf = (p: string) => {
    // Compute the next set BEFORE updating state — calling setUrl (which
    // does router.replace) inside a setState updater is a render-phase
    // state update on another component (Router), which React warns about.
    const next = new Set(activeProfs);
    if (next.has(p)) next.delete(p);
    else next.add(p);
    setActiveProfs(next);
    const arr = Array.from(next).sort();
    setUrl({
      profs:
        arr.length === allProfessions.length ? null : arr.join(","),
    });
  };

  // Filter the section list: profession filter + search.
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return payload.sections.filter((s) => {
      // Profession filter:
      //   - universal: always show
      //   - multi: show if ANY selected profession is in applies_to
      //   - single: show if its profession is selected
      if (s.audience === "single") {
        if (s.profession && !activeProfs.has(s.profession)) return false;
      } else if (s.audience === "multi") {
        if (!s.applies_to?.some((p) => activeProfs.has(p))) return false;
      }
      // Search:
      if (!q) return true;
      return (
        (s.text || "").toLowerCase().includes(q) ||
        (s.citation || "").toLowerCase().includes(q) ||
        (s.label || "").toLowerCase().includes(q)
      );
    });
  }, [payload.sections, activeProfs, query]);

  // Group: universal first, then multi-prof by unique applies_to set,
  // then single-prof by profession.
  const groups = useMemo(() => {
    const universal: StateBrowseSection[] = [];
    const multiByKey: Record<string, { profs: string[]; sections: StateBrowseSection[] }> = {};
    const singleByProf: Record<string, StateBrowseSection[]> = {};

    for (const s of filtered) {
      if (s.audience === "universal") {
        universal.push(s);
      } else if (s.audience === "multi") {
        const profs = (s.applies_to ?? []).slice().sort();
        const key = profs.join(",");
        if (!multiByKey[key]) multiByKey[key] = { profs, sections: [] };
        multiByKey[key].sections.push(s);
      } else if (s.audience === "single" && s.profession) {
        (singleByProf[s.profession] ||= []).push(s);
      }
    }
    return {
      universal,
      multi: Object.values(multiByKey).sort(
        (a, b) => b.sections.length - a.sections.length,
      ),
      single: Object.entries(singleByProf).sort(([a], [b]) => a.localeCompare(b)),
    };
  }, [filtered]);

  const selected: StateBrowseSection | null = useMemo(() => {
    if (selectedCite) {
      const hit = filtered.find((s) => s.citation === selectedCite);
      if (hit) return hit;
    }
    return filtered[0] ?? null;
  }, [filtered, selectedCite]);

  return (
    <div className="flex flex-col h-screen">
      <header className="border-b px-6 py-3 flex items-center gap-3 flex-wrap bg-background">
        <Link href="/" className="text-xs font-mono text-muted-foreground hover:text-foreground">
          home
        </Link>
        <span className="text-xs text-muted-foreground">›</span>
        <span className="text-xs font-mono font-medium">{payload.state}</span>
        <span className="text-xs text-muted-foreground ml-2">
          showing {filtered.length} of {payload.sections.length} sections
        </span>
      </header>

      {/* Filter bar — profession multi-select */}
      <div className="border-b px-6 py-2.5 flex items-center gap-3 flex-wrap bg-muted/30">
        <span className="text-xs text-muted-foreground">show sections for:</span>
        <ToggleGroup variant="outline" size="sm" spacing={1}>
          {allProfessions.map((p) => (
            <ToggleGroupItem
              key={p}
              pressed={activeProfs.has(p)}
              onPressedChange={() => toggleProf(p)}
              className="text-xs px-2.5"
            >
              {p.replace(/_/g, " ")}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
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

      <Group orientation="horizontal" className="flex-1 overflow-hidden flex">
        <Panel
          defaultSize="32%"
          minSize="20%"
          maxSize="50%"
          className="overflow-y-auto py-2 border-r"
        >
          {/* Universal */}
          {groups.universal.length > 0 && (
            <TreeGroup
              header={
                <>
                  <span className={`w-1.5 h-1.5 rounded-full ${AUDIENCE_DOT.universal}`} />
                  {AUDIENCE_LABEL.universal}{" "}
                  <span className="font-mono text-muted-foreground/70 ml-1">
                    {groups.universal.length}
                  </span>
                </>
              }
              sections={groups.universal}
              selected={selected}
              onSelect={handleSelect}
            />
          )}

          {/* Multi-prof */}
          {groups.multi.map((g) => (
            <TreeGroup
              key={g.profs.join(",")}
              header={
                <>
                  <span className={`w-1.5 h-1.5 rounded-full ${AUDIENCE_DOT.multi}`} />
                  Applies to: {g.profs.map((p) => p.replace(/_/g, " ")).join(", ")}{" "}
                  <span className="font-mono text-muted-foreground/70 ml-1">
                    {g.sections.length}
                  </span>
                </>
              }
              sections={g.sections}
              selected={selected}
              onSelect={handleSelect}
            />
          ))}

          {/* Single-prof */}
          {groups.single.map(([prof, secs]) => (
            <TreeGroup
              key={prof}
              header={
                <>
                  <span className={`w-1.5 h-1.5 rounded-full ${AUDIENCE_DOT.single}`} />
                  {prof.replace(/_/g, " ")} (practice act){" "}
                  <span className="font-mono text-muted-foreground/70 ml-1">
                    {secs.length}
                  </span>
                </>
              }
              sections={secs}
              selected={selected}
              onSelect={handleSelect}
            />
          ))}

          {filtered.length === 0 && (
            <p className="px-4 py-6 text-xs text-muted-foreground italic">
              No sections match the current filters.
            </p>
          )}
        </Panel>
        <Separator className="w-1 bg-border hover:bg-foreground/20 transition-colors" />
        <Panel defaultSize="68%" minSize="50%" className="overflow-y-auto">
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

function TreeGroup({
  header,
  sections,
  selected,
  onSelect,
}: {
  header: React.ReactNode;
  sections: StateBrowseSection[];
  selected: StateBrowseSection | null;
  onSelect: (s: StateBrowseSection) => void;
}) {
  return (
    <div className="mb-3">
      <div className="px-4 py-1 text-[10px] font-mono uppercase tracking-widest text-muted-foreground flex items-center gap-1.5">
        {header}
      </div>
      <ul>
        {sections.map((s) => {
          const active = selected?.citation === s.citation && selected?.url === s.url;
          const fieldNames = Array.from(
            new Set(s.evidence.map((e) => shortFieldPath(e.field_path))),
          );
          return (
            <li key={`${s.audience}-${s.citation}-${s.url}`}>
              <button
                type="button"
                onClick={() => onSelect(s)}
                className={
                  "w-full text-left px-4 py-1.5 text-xs hover:bg-muted/50 border-l-2 " +
                  (active ? "bg-muted/70 border-foreground" : "border-transparent")
                }
              >
                <span className="font-mono text-foreground truncate block">
                  {s.citation || s.label || "(no citation)"}
                </span>
                {fieldNames.length > 0 && (
                  <span
                    className="text-[10px] text-muted-foreground truncate block"
                    title={s.evidence.map((e) => e.field_path).join(", ")}
                  >
                    {fieldNames.join(", ")}
                  </span>
                )}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function SectionDetail({
  section,
  searchQuery,
}: {
  section: StateBrowseSection;
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

  const parts = useMemo(
    () => renderLayered(section.text, evidenceSpans, searchHits),
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
            <span className={`w-1.5 h-1.5 rounded-full ${AUDIENCE_DOT[section.audience]}`} />
            {AUDIENCE_LABEL[section.audience]}
          </Badge>
          {section.audience === "multi" && section.applies_to && (
            <Badge variant="secondary" className="font-mono text-[10px]">
              applies to {section.applies_to.map((p) => p.replace(/_/g, " ")).join(", ")}
            </Badge>
          )}
          {section.audience === "single" && section.profession && (
            <Badge variant="secondary" className="font-mono text-[10px]">
              {section.profession.replace(/_/g, " ")}
            </Badge>
          )}
          {section.evidence.length > 0 && (
            <Badge
              variant="outline"
              className="font-mono text-[10px] bg-amber-100/60 text-amber-900 border-amber-300"
              title="Each claim is an LLM-extracted field whose quote was found in this section. Hover an amber span to see all of them."
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
      if (!chars[i].evs.includes(ev)) chars[i].evs.push(ev);
    }
  }
  for (const [start, end] of searchSpans) {
    for (let i = start; i < end && i < text.length; i++) {
      chars[i].search = true;
    }
  }

  const key = (evs: BrowseEvidence[]): string =>
    evs.map((e) => e.field_path + "@" + (e.profession ?? "")).sort().join("\x1f");

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

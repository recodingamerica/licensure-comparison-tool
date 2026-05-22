"use client";

// State-level browse: every regulation that touches a licensed profession
// in this state, with the actual statute hierarchy (title → chapter/
// article → part → section) preserved. Groups are by audience: universal
// at top, then multi-prof buckets, then single-prof buckets. Each group
// contains a forest of collapsible tree nodes.

import { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { Group, Panel, Separator } from "react-resizable-panels";
import type {
  StateBrowsePayload,
  StateBrowseSection,
  StateBrowseGroup,
} from "@/lib/state-browse-types";
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
import {
  TreeNodeView,
  sectionKey,
  allBranchSlugs,
  type TreeNode,
} from "./tree-node";
import { professionStyle, useProfessionMeta } from "@/lib/profession-colors";

function shortFieldPath(p: string): string {
  if (p.startsWith("licensure.")) return p.slice("licensure.".length);
  if (p.startsWith("profession_specific.")) return p.slice("profession_specific.".length);
  if (p.startsWith("scope.")) return p.slice("scope.".length);
  return p;
}

const AUDIENCE_LABEL: Record<StateBrowseGroup["kind"], string> = {
  universal: "Applies to everyone",
  multi: "Shared with multiple professions",
  single: "Profession-specific",
};

const AUDIENCE_DOT: Record<StateBrowseGroup["kind"], string> = {
  universal: "bg-purple-500",
  multi: "bg-emerald-500",
  single: "bg-sky-500",
};

// Tag every section's URL with its audience info for the detail panel,
// pulled from the flat sections array (cheaper than walking the tree to
// find the matching node).
function buildSectionIndex(
  sections: StateBrowseSection[],
): Map<string, StateBrowseSection> {
  const m = new Map<string, StateBrowseSection>();
  for (const s of sections) m.set(s.url, s);
  return m;
}

export function StateBrowseClient({ payload }: { payload: StateBrowsePayload }) {
  // Triggers /professions.json load — re-renders once meta resolves so
  // chips/badges get their proper colors and abbreviations instead of
  // the neutral fallback.
  useProfessionMeta();
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();

  const allProfessions = payload.professions_available;
  const sectionIndex = useMemo(() => buildSectionIndex(payload.sections), [payload.sections]);

  const [query, setQuery] = useState<string>(params.get("q") ?? "");
  // Empty set = no profession filter, show everything (default). Selecting
  // a chip = "filter to this profession." User's mental model matches:
  // clicking podiatry shows podiatry; clicking it again returns to "all."
  const urlProfs = (params.get("profs") || "").split(",").filter(Boolean);
  const [activeProfs, setActiveProfs] = useState<Set<string>>(
    () => new Set(urlProfs),
  );

  // Tree-collapse state. Default: every branch expanded so the user sees
  // the whole hierarchy on load. Stored in the URL as `?closed=` (slugs
  // the user has chosen to collapse) so links survive reload.
  const closedParam = params.get("closed") || "";
  const [collapsed, setCollapsed] = useState<Set<string>>(
    () => new Set(closedParam.split(",").filter(Boolean)),
  );
  // expanded = ALL_BRANCHES − collapsed. We track collapsed so the default
  // (everything open) takes zero URL space.
  const allSlugs = useMemo(() => {
    const all: string[] = [];
    for (const g of payload.groups) all.push(...allBranchSlugs(g.tree));
    return new Set(all);
  }, [payload.groups]);
  const expanded = useMemo(() => {
    const e = new Set(allSlugs);
    for (const slug of collapsed) e.delete(slug);
    return e;
  }, [allSlugs, collapsed]);

  const selectedKey = params.get("cite") || "";

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

  const toggleProf = (p: string) => {
    const next = new Set(activeProfs);
    if (next.has(p)) next.delete(p);
    else next.add(p);
    setActiveProfs(next);
    const arr = Array.from(next).sort();
    // Empty set = the default ("no filter, show all") so we omit the param.
    setUrl({ profs: arr.length === 0 ? null : arr.join(",") });
  };

  const toggleBranch = (slug: string) => {
    const nextCollapsed = new Set(collapsed);
    if (nextCollapsed.has(slug)) nextCollapsed.delete(slug);
    else nextCollapsed.add(slug);
    setCollapsed(nextCollapsed);
    const arr = Array.from(nextCollapsed).sort();
    setUrl({ closed: arr.length === 0 ? null : arr.join(",") });
  };
  const expandAll = () => {
    setCollapsed(new Set());
    setUrl({ closed: null });
  };
  const collapseAll = () => {
    const next = new Set(allSlugs);
    setCollapsed(next);
    setUrl({ closed: Array.from(next).sort().join(",") });
  };

  const handleSelect = (section: unknown) => {
    const s = section as StateBrowseSection;
    setUrl({ cite: `${s.url}` });
  };

  // Profession filter: empty set means "no filter, show all." When non-
  // empty, universal always still shows; multi-prof keeps sections whose
  // applies_to intersects the active set; single-prof keeps only the
  // matching profession buckets.
  const visibleGroups = useMemo<StateBrowseGroup[]>(() => {
    const filterActive = activeProfs.size > 0;
    if (!filterActive) return payload.groups;
    const out: StateBrowseGroup[] = [];
    for (const g of payload.groups) {
      if (g.kind === "universal") {
        out.push(g);
      } else if (g.kind === "single") {
        if (activeProfs.has(g.profession)) out.push(g);
      } else if (g.kind === "multi") {
        const prune = (node: TreeNode): TreeNode | null => {
          if (node.level === "section") {
            const sec = node.section as StateBrowseSection | undefined;
            const at = sec?.applies_to ?? [];
            return at.some((p) => activeProfs.has(p)) ? node : null;
          }
          const children = node.children
            .map(prune)
            .filter((c): c is TreeNode => c !== null);
          if (children.length === 0) return null;
          return { ...node, children };
        };
        const tree = g.tree.map(prune).filter((n): n is TreeNode => n !== null);
        if (tree.length > 0) out.push({ ...g, tree });
      }
    }
    return out;
  }, [payload.groups, activeProfs]);

  // Search: filter the tree to leaves whose section text/citation/label
  // contains the query. Branches with no matching descendants drop out.
  const filteredGroups = useMemo<StateBrowseGroup[]>(() => {
    const q = query.trim().toLowerCase();
    if (!q) return visibleGroups;
    const matchSection = (s: StateBrowseSection): boolean =>
      (s.text || "").toLowerCase().includes(q) ||
      (s.citation || "").toLowerCase().includes(q) ||
      (s.label || "").toLowerCase().includes(q);
    const prune = (node: TreeNode): TreeNode | null => {
      if (node.level === "section") {
        const sec = node.section as StateBrowseSection | undefined;
        return sec && matchSection(sec) ? node : null;
      }
      const children = node.children
        .map(prune)
        .filter((c): c is TreeNode => c !== null);
      if (children.length === 0) return null;
      return { ...node, children };
    };
    return visibleGroups
      .map((g) => ({ ...g, tree: g.tree.map(prune).filter((n): n is TreeNode => n !== null) }))
      .filter((g) => g.tree.length > 0);
  }, [visibleGroups, query]);

  // Find the currently-selected section so the detail panel can render
  // it. The URL stores the section URL (which is unique across the state
  // payload).
  const selected: StateBrowseSection | null = useMemo(() => {
    if (selectedKey) {
      const hit = sectionIndex.get(selectedKey);
      if (hit) return hit;
    }
    // Default: first leaf in the first visible group.
    for (const g of filteredGroups) {
      const first = firstLeaf(g.tree);
      if (first) return first;
    }
    return null;
  }, [filteredGroups, sectionIndex, selectedKey]);

  const totalShown = useMemo(
    () => filteredGroups.reduce((n, g) => n + countLeaves(g.tree), 0),
    [filteredGroups],
  );

  return (
    <div className="flex flex-col h-screen">
      <header className="border-b px-6 py-3 flex items-center gap-3 flex-wrap bg-background">
        <Link href="/" className="text-xs font-mono text-muted-foreground hover:text-foreground">
          home
        </Link>
        <span className="text-xs text-muted-foreground">›</span>
        <span className="text-xs font-mono font-medium">{payload.state}</span>
        <span className="text-xs text-muted-foreground ml-2">
          showing {totalShown} of {payload.sections.length} sections
        </span>
      </header>

      <div className="border-b px-6 py-2.5 flex items-center gap-3 flex-wrap bg-muted/30">
        <span className="text-xs text-muted-foreground">
          {activeProfs.size === 0
            ? "filter by profession:"
            : `filtered to ${activeProfs.size} of ${allProfessions.length}:`}
        </span>
        <ToggleGroup variant="outline" size="sm" spacing={1}>
          {allProfessions.map((p) => {
            const s = professionStyle(p);
            const on = activeProfs.has(p);
            return (
              <ToggleGroupItem
                key={p}
                pressed={on}
                onPressedChange={() => toggleProf(p)}
                className={
                  "text-xs px-2.5 gap-1.5 " +
                  (on ? `${s.bg} ${s.text} ${s.border}` : "")
                }
              >
                <span className={`w-2 h-2 rounded-full ${s.dot}`} />
                {p.replace(/_/g, " ")}
              </ToggleGroupItem>
            );
          })}
        </ToggleGroup>
        {activeProfs.size > 0 && (
          <button
            type="button"
            onClick={() => {
              setActiveProfs(new Set());
              setUrl({ profs: null });
            }}
            className="text-[10px] font-mono text-muted-foreground hover:text-foreground underline"
          >
            clear filter
          </button>
        )}
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
          defaultSize="35%"
          minSize="20%"
          maxSize="55%"
          className="overflow-y-auto py-2 border-r"
        >
          <div className="px-4 py-1.5 flex items-center gap-2 text-[10px] font-mono text-muted-foreground">
            <button
              type="button"
              onClick={expandAll}
              className="hover:text-foreground"
            >
              expand all
            </button>
            <span className="text-muted-foreground/40">·</span>
            <button
              type="button"
              onClick={collapseAll}
              className="hover:text-foreground"
            >
              collapse all
            </button>
          </div>
          {filteredGroups.map((g) => (
            <div key={g.key} className="mb-4">
              <div className="px-4 py-1 text-[10px] font-mono uppercase tracking-widest text-muted-foreground flex items-center gap-1.5">
                <span className={`w-1.5 h-1.5 rounded-full ${AUDIENCE_DOT[g.kind]}`} />
                {g.kind === "universal" && AUDIENCE_LABEL.universal}
                {g.kind === "multi" && <>Shared with multiple professions</>}
                {g.kind === "single" && (
                  <>{g.profession.replace(/_/g, " ")} (practice act)</>
                )}
              </div>
              {g.tree.map((top) => (
                <TreeNodeView
                  key={`${top.level}-${top.slug}`}
                  node={top}
                  depth={0}
                  selectedKey={selected?.url || ""}
                  expanded={expanded}
                  onToggle={toggleBranch}
                  onSelect={handleSelect}
                />
              ))}
            </div>
          ))}
          {filteredGroups.length === 0 && (
            <p className="px-4 py-6 text-xs text-muted-foreground italic">
              No sections match the current filters.
            </p>
          )}
        </Panel>
        <Separator className="w-1 bg-border hover:bg-foreground/20 transition-colors" />
        <Panel defaultSize="65%" minSize="45%" className="overflow-y-auto">
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

// Helpers — tree walks
function firstLeaf(forest: TreeNode[]): StateBrowseSection | null {
  for (const n of forest) {
    if (n.level === "section" && n.section) return n.section as StateBrowseSection;
    const inner = firstLeaf(n.children);
    if (inner) return inner;
  }
  return null;
}

function countLeaves(forest: TreeNode[]): number {
  let n = 0;
  for (const node of forest) {
    if (node.level === "section") n++;
    else n += countLeaves(node.children);
  }
  return n;
}

// Suppress unused-import warning — sectionKey is exported by tree-node
// and used in the per-prof browse client too; keep the import here for
// when we wire selection-by-key.
void sectionKey;

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

  const audienceKind: StateBrowseGroup["kind"] = section.audience;

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
            <span className={`w-1.5 h-1.5 rounded-full ${AUDIENCE_DOT[audienceKind]}`} />
            {AUDIENCE_LABEL[audienceKind]}
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
              title="Hover an amber span to see the field name + extracted value."
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

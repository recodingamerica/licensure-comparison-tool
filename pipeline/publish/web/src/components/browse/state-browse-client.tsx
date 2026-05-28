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
import { Input } from "@/components/ui/input";
import { MultiCheckPopover, type MultiCheckItem } from "@/components/ui/multi-check-popover";
import { Badge } from "@/components/ui/badge";
import { Search } from "lucide-react";
import {
  TreeNodeView,
  sectionKey,
  allBranchSlugs,
  firstLeafSection,
  countLeaves,
  pruneTree,
} from "./tree-node";
import { professionStyle, useProfessionMeta } from "@/lib/profession-colors";
import { AUDIENCE_LABEL, AUDIENCE_DOT } from "@/lib/audience";
import { SectionDetail } from "./section-detail";

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

  // Tree-collapse state. Default: every branch COLLAPSED so the user picks
  // what to drill into on load. Stored in the URL as `?open=` (slugs the
  // user has chosen to expand) so links survive reload. A page-wide "expand
  // all" sets `?open=*` (sentinel) — cleaner than enumerating every slug.
  const openParam = params.get("open") || "";
  const allSlugs = useMemo(() => {
    const all: string[] = [];
    for (const g of payload.groups) all.push(...allBranchSlugs(g.tree));
    return new Set(all);
  }, [payload.groups]);
  const [openSet, setOpenSet] = useState<Set<string>>(
    () =>
      openParam === "*"
        ? new Set(allSlugs)
        : new Set(openParam.split(",").filter(Boolean)),
  );
  const expanded = openSet;

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
    const nextOpen = new Set(openSet);
    if (nextOpen.has(slug)) nextOpen.delete(slug);
    else nextOpen.add(slug);
    setOpenSet(nextOpen);
    const arr = Array.from(nextOpen).sort();
    setUrl({ open: arr.length === 0 ? null : arr.join(",") });
  };
  const expandAll = () => {
    setOpenSet(new Set(allSlugs));
    setUrl({ open: "*" });
  };
  const collapseAll = () => {
    setOpenSet(new Set());
    setUrl({ open: null });
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
        const tree = pruneTree<StateBrowseSection>(g.tree, (sec) =>
          (sec.applies_to ?? []).some((p) => activeProfs.has(p)),
        );
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
    const matches = (s: StateBrowseSection) =>
      (s.text || "").toLowerCase().includes(q) ||
      (s.citation || "").toLowerCase().includes(q) ||
      (s.label || "").toLowerCase().includes(q);
    return visibleGroups
      .map((g) => ({ ...g, tree: pruneTree<StateBrowseSection>(g.tree, matches) }))
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
      const first = firstLeafSection<StateBrowseSection>(g.tree);
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
        <MultiCheckPopover
          label="Professions"
          items={allProfessions.map<MultiCheckItem>((p) => ({
            id: p,
            label: p.replace(/_/g, " "),
            swatchClass: professionStyle(p).dot,
          }))}
          // The control treats "select all" == "no filter"; map that to an
          // empty active set so the URL stays clean and the "show
          // everything" default matches a fresh load.
          selected={activeProfs.size === 0 ? new Set(allProfessions) : activeProfs}
          onChange={(next) => {
            const filterAll = next.size === allProfessions.length || next.size === 0;
            const effective = filterAll ? new Set<string>() : next;
            setActiveProfs(effective);
            setUrl({
              profs: effective.size === 0 ? null : Array.from(effective).sort().join(","),
            });
          }}
        />
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
            <StateSectionDetail section={selected} searchQuery={query} />
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

// Suppress unused-import warning — sectionKey is exported by tree-node
// and used in the per-prof browse client too; keep the import here for
// when we wire selection-by-key.
void sectionKey;

function StateSectionDetail({
  section,
  searchQuery,
}: {
  section: StateBrowseSection;
  searchQuery: string;
}) {
  const audienceKind = section.audience;
  return (
    <SectionDetail
      section={section}
      searchQuery={searchQuery}
      badges={
        <>
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
        </>
      }
    />
  );
}


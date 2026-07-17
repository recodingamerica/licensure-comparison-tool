"use client";

// Per-(state, profession) browse view. Two-pane layout:
//   left   — hierarchy tree, sections grouped by scope_layer with the
//            statute's own title/chapter/article/part nesting preserved.
//   right  — selected section's full text with extracted-quote highlights
//            (amber, hover = field + value) and search highlights (yellow).
//
// Selected section is carried in the URL as ?cite=<section-url>; layer
// chips and search text in ?layers/?q/?closed=. Links survive reload.

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { Group, Panel, Separator } from "react-resizable-panels";
import type { BrowseSection } from "@/lib/types";
import { Input } from "@/components/ui/input";
// ToggleGroup imports removed alongside the scope-layer chips — `activeLayers`
// state still exists so direct ?layers=… URLs are honored, but no inline
// toggle UI renders the chips.
import { Badge } from "@/components/ui/badge";
import { Search } from "lucide-react";
import {
  TreeNodeView,
  allBranchSlugs,
  firstLeafSection,
  countLeaves,
  pruneTree,
  type TreeNode,
} from "./tree-node";
import { useProfessionMeta } from "@/lib/profession-colors";
import { AUDIENCE_DOT, AUDIENCE_LABEL } from "@/lib/audience";
import { SectionDetail } from "./section-detail";

type LayerKey = "practice" | "umbrella_enumeration" | "umbrella_universal";

// Each browse-tree layer maps 1:1 to an audience tier; route both label and
// dot color through lib/audience.ts so we only have one source of truth and
// the colors stay aligned with /browse/[state]'s tree and the section
// badges on /professions/<X>?view=statutes.
const LAYER_LABEL: Record<LayerKey, string> = {
  practice: AUDIENCE_LABEL.single + " (practice act)",
  umbrella_enumeration: AUDIENCE_LABEL.multi,
  umbrella_universal: AUDIENCE_LABEL.universal,
};
const LAYER_DOT: Record<LayerKey, string> = {
  practice: AUDIENCE_DOT.single,
  umbrella_enumeration: AUDIENCE_DOT.multi,
  umbrella_universal: AUDIENCE_DOT.universal,
};

type BrowseGroup = { key: LayerKey; tree: TreeNode[] };

export function BrowseClient({
  state,
  profession,
  sections,
  groups,
}: {
  state: string;
  profession: string;
  sections: BrowseSection[];
  groups: BrowseGroup[];
}) {
  // Trigger /professions.json load so applies-to badges on umbrella-
  // enumeration leaves get the proper family colors / abbreviations.
  useProfessionMeta();
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();

  const sectionIndex = useMemo(() => {
    const m = new Map<string, BrowseSection>();
    for (const s of sections) m.set(s.url, s);
    return m;
  }, [sections]);

  const [query, setQuery] = useState<string>(params.get("q") ?? "");
  const [activeLayers, setActiveLayers] = useState<Set<LayerKey>>(
    () => new Set(groups.map((g) => g.key)),
  );

  // Default-collapsed; user opens what they want. Stored as ?open=… with
  // the sentinel `*` meaning "everything expanded" so expand-all doesn't
  // need to enumerate every slug in the URL.
  const openParam = params.get("open") || "";
  const allSlugs = useMemo(() => {
    const all: string[] = [];
    for (const g of groups) all.push(...allBranchSlugs(g.tree));
    return new Set(all);
  }, [groups]);
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
  const toggleLayer = (k: LayerKey) => {
    const next = new Set(activeLayers);
    if (next.has(k)) next.delete(k);
    else next.add(k);
    setActiveLayers(next);
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
    const s = section as BrowseSection;
    setUrl({ cite: s.url });
  };

  // Visible groups: layer-filter applied first, then search prunes the
  // tree to leaves whose section text/citation/label contains the query.
  const visibleGroups = useMemo<BrowseGroup[]>(
    () => groups.filter((g) => activeLayers.has(g.key)),
    [groups, activeLayers],
  );

  const filteredGroups = useMemo<BrowseGroup[]>(() => {
    const q = query.trim().toLowerCase();
    if (!q) return visibleGroups;
    const matches = (s: BrowseSection) =>
      (s.text || "").toLowerCase().includes(q) ||
      (s.citation || "").toLowerCase().includes(q) ||
      (s.label || "").toLowerCase().includes(q);
    return visibleGroups
      .map((g) => ({ ...g, tree: pruneTree<BrowseSection>(g.tree, matches) }))
      .filter((g) => g.tree.length > 0);
  }, [visibleGroups, query]);

  // When a search is active, auto-expand every surviving branch so the pruned matches
  // are actually visible. Without this a match sits inside a collapsed branch and the
  // side-tree click only toggles that branch open instead of navigating (issue #77).
  useEffect(() => {
    if (!query.trim()) return;
    const slugs = filteredGroups.flatMap((g) => allBranchSlugs(g.tree));
    if (slugs.length === 0) return;
    setOpenSet((prev) => {
      const next = new Set(prev);
      let changed = false;
      for (const s of slugs) if (!next.has(s)) { next.add(s); changed = true; }
      return changed ? next : prev;
    });
  }, [query, filteredGroups]);

  const selected: BrowseSection | null = useMemo(() => {
    if (selectedKey) {
      const hit = sectionIndex.get(selectedKey);
      if (hit) return hit;
    }
    for (const g of filteredGroups) {
      const first = firstLeafSection<BrowseSection>(g.tree);
      if (first) return first;
    }
    return null;
  }, [filteredGroups, sectionIndex, selectedKey]);

  const totalShown = useMemo(
    () => filteredGroups.reduce((n, g) => n + countLeaves(g.tree), 0),
    [filteredGroups],
  );

  // Count of layers present in the data — used to decide whether to show
  // the layer toggle (≥2) or a quiet text label (1).
  void groups.length; // layersPresent no longer used since chip removal

  return (
    <div className="flex flex-col h-screen">
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
          showing {totalShown} of {sections.length} sections
        </span>
      </header>

      <div className="border-b px-6 py-2.5 flex items-center gap-3 flex-wrap bg-muted/30">
        {/* Scope-layer chips removed — the tree on the left already groups
            sections by scope_layer with the same labels, so the chips were
            duplicate navigation. Keep `activeLayers` / `toggleLayer` in case
            a future re-introduction wants a quieter inline control. */}
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
            <button type="button" onClick={expandAll} className="hover:text-foreground">
              expand all
            </button>
            <span className="text-muted-foreground/40">·</span>
            <button type="button" onClick={collapseAll} className="hover:text-foreground">
              collapse all
            </button>
          </div>
          {filteredGroups.map((g) => (
            <div key={g.key} className="mb-4">
              <div className="px-4 py-1 text-[10px] font-mono uppercase tracking-widest text-muted-foreground flex items-center gap-1.5">
                <span className={`w-1.5 h-1.5 rounded-full ${LAYER_DOT[g.key]}`} />
                {LAYER_LABEL[g.key]}
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
            <ProfSectionDetail section={selected} searchQuery={query} />
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

function ProfSectionDetail({
  section,
  searchQuery,
}: {
  section: BrowseSection;
  searchQuery: string;
}) {
  const layer = section.scope_layer as LayerKey;
  return (
    <SectionDetail
      section={section}
      searchQuery={searchQuery}
      badges={
        <>
          <Badge variant="outline" className="font-mono text-[10px] gap-1.5">
            <span className={`w-1.5 h-1.5 rounded-full ${LAYER_DOT[layer]}`} />
            {LAYER_LABEL[layer]}
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


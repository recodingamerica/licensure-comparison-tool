"use client";

// Recursive tree-node renderer used by both browse views.
//
// Each node is either a BRANCH (title / chapter / article / part) — a
// collapsible header with children — or a LEAF (section) — a clickable
// row that pulls the section into the detail pane. Indentation tracks
// depth; collapse state is held in a shared Set the parent owns.
//
// The TreeNode shape mirrors what publish/_browse_tree.py emits:
//   { slug, level, label, url, section?, children: TreeNode[] }

import { ChevronDown, ChevronRight } from "lucide-react";
import type { BrowseEvidence } from "@/lib/types";
import { professionStyle } from "@/lib/profession-colors";

export type TreeNode = {
  slug: string;
  level: "title" | "chapter" | "article" | "part" | "section";
  label: string;
  url: string | null;
  // Only on leaves — the full section payload (text + evidence). The
  // SectionDetail panel renders this when the leaf is selected.
  // Using `unknown` here because the two browse views ship slightly
  // different section shapes (BrowseSection vs StateBrowseSection); the
  // tree component never reaches inside the section, only the parent
  // passes it through.
  section?: unknown;
  children: TreeNode[];
};

import { shortFieldPath } from "@/lib/render-layered";

type LeafPayload = {
  text?: string;
  evidence?: BrowseEvidence[];
  citation?: string;
  label?: string;
  // Only present on state-browse leaves — surfaces as a small chip on
  // multi-profession sections so users see WHICH professions a shared
  // statute applies to without having to open the detail pane.
  applies_to?: string[] | null;
  audience?: "universal" | "multi" | "single";
};

export function TreeNodeView({
  node,
  depth,
  selectedKey,
  expanded,
  onToggle,
  onSelect,
}: {
  node: TreeNode;
  depth: number;
  selectedKey: string;
  expanded: Set<string>;
  onToggle: (key: string) => void;
  onSelect: (section: unknown) => void;
}) {
  // Leaf: clickable section row.
  if (node.level === "section") {
    const active = selectedKey === sectionKey(node);
    const leaf = (node.section as LeafPayload | undefined) || {};
    const fieldNames = Array.from(
      new Set((leaf.evidence ?? []).map((e) => shortFieldPath(e.field_path))),
    );
    // Show an "applies to: X, Y" chip when the leaf is shared between
    // multiple professions — either because the state-browse aggregator
    // tagged it as "multi" audience, or because the per-prof aggregator
    // tagged it as umbrella_enumeration with multiple applies_to. The
    // chip tells the reader "this rule isn't exclusive to the profession
    // you came in by" without making them open the detail pane.
    const showApplies =
      !!leaf.applies_to &&
      leaf.applies_to.length > 1 &&
      leaf.audience !== "single";
    return (
      <button
        type="button"
        onClick={() => node.section && onSelect(node.section)}
        style={{ paddingLeft: 12 + depth * 12 }}
        className={
          "w-full text-left py-1.5 pr-3 text-xs border-l-2 transition-colors " +
          (active
            ? "bg-muted/80 border-foreground"
            : "border-transparent hover:border-foreground/20 hover:bg-muted/40")
        }
      >
        <span className="font-mono text-foreground truncate block">
          {node.label}
        </span>
        {showApplies && (
          <span
            className="flex items-center gap-1 flex-wrap mt-1"
            title={`Applies to: ${leaf.applies_to!.join(", ")}`}
          >
            {leaf.applies_to!.map((p) => {
              const s = professionStyle(p);
              return (
                <span
                  key={p}
                  className={`text-[9px] font-mono font-semibold px-1.5 py-0.5 rounded ${s.bg} ${s.text} border ${s.border}`}
                >
                  {s.abbr}
                </span>
              );
            })}
          </span>
        )}
        {fieldNames.length > 0 && (
          <span
            className="text-[10px] text-muted-foreground truncate block mt-0.5"
            title={(leaf.evidence ?? []).map((e) => e.field_path).join(", ")}
          >
            {fieldNames.join(", ")}
          </span>
        )}
      </button>
    );
  }

  // Branch: collapsible header. Slightly heavier visual treatment than
  // before — bold weight, subtle bottom border so the hierarchy reads.
  const isOpen = expanded.has(node.slug);
  return (
    <div>
      <button
        type="button"
        onClick={() => onToggle(node.slug)}
        style={{ paddingLeft: 4 + depth * 12 }}
        className={
          "w-full text-left py-1.5 text-[11px] font-mono font-semibold uppercase tracking-wide text-foreground/70 hover:text-foreground flex items-center gap-1 pr-3 " +
          (depth === 0 ? "border-b border-border/40" : "")
        }
      >
        {isOpen ? (
          <ChevronDown className="size-3 shrink-0 text-muted-foreground" />
        ) : (
          <ChevronRight className="size-3 shrink-0 text-muted-foreground" />
        )}
        <span className="truncate">{node.label}</span>
        <span className="ml-auto font-mono text-muted-foreground/70 font-normal text-[10px]">
          {countLeaves(node)}
        </span>
      </button>
      {isOpen &&
        node.children.map((c) => (
          <TreeNodeView
            key={`${c.level}-${c.slug}`}
            node={c}
            depth={depth + 1}
            selectedKey={selectedKey}
            expanded={expanded}
            onToggle={onToggle}
            onSelect={onSelect}
          />
        ))}
    </div>
  );
}

// Stable identifier for a leaf — the parent uses this to track which
// section is selected. URL alone isn't unique because some sections lack
// URLs; citation alone isn't either because state browse can have
// duplicate citations across professions.
export function sectionKey(node: TreeNode): string {
  return `${node.slug}|${node.url || ""}`;
}

// Recursive: returns all branch slugs in the forest, so callers can
// default-expand or default-collapse them.
export function allBranchSlugs(forest: TreeNode[]): string[] {
  const out: string[] = [];
  const visit = (n: TreeNode) => {
    if (n.level === "section") return;
    out.push(n.slug);
    for (const c of n.children) visit(c);
  };
  for (const top of forest) visit(top);
  return out;
}

/** First leaf section in document order — used to default-select a
 *  section when the URL doesn't carry one. Parameterized over the
 *  section type because the two browse views ship slightly different
 *  shapes. */
export function firstLeafSection<T>(forest: TreeNode[]): T | null {
  for (const n of forest) {
    if (n.level === "section" && n.section) return n.section as T;
    const inner = firstLeafSection<T>(n.children);
    if (inner) return inner;
  }
  return null;
}

/** Total number of section leaves under a node OR a forest. Used for
 *  "showing X of Y" headers and per-branch leaf counts in the tree. */
export function countLeaves(arg: TreeNode | TreeNode[]): number {
  if (Array.isArray(arg)) {
    let n = 0;
    for (const node of arg) n += countLeaves(node);
    return n;
  }
  if (arg.level === "section") return 1;
  let n = 0;
  for (const c of arg.children) n += countLeaves(c);
  return n;
}

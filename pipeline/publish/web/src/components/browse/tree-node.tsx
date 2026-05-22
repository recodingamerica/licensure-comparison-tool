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

function shortFieldPath(p: string): string {
  if (p.startsWith("licensure.")) return p.slice("licensure.".length);
  if (p.startsWith("profession_specific.")) return p.slice("profession_specific.".length);
  if (p.startsWith("scope.")) return p.slice("scope.".length);
  return p;
}

type LeafPayload = {
  text?: string;
  evidence?: BrowseEvidence[];
  citation?: string;
  label?: string;
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
    return (
      <button
        type="button"
        onClick={() => node.section && onSelect(node.section)}
        style={{ paddingLeft: 12 + depth * 12 }}
        className={
          "w-full text-left py-1 text-xs hover:bg-muted/50 border-l-2 pr-3 " +
          (active ? "bg-muted/70 border-foreground" : "border-transparent")
        }
      >
        <span className="font-mono text-foreground truncate block">
          {node.label}
        </span>
        {fieldNames.length > 0 && (
          <span
            className="text-[10px] text-muted-foreground truncate block"
            title={(leaf.evidence ?? []).map((e) => e.field_path).join(", ")}
          >
            {fieldNames.join(", ")}
          </span>
        )}
      </button>
    );
  }

  // Branch: collapsible header.
  const isOpen = expanded.has(node.slug);
  return (
    <div>
      <button
        type="button"
        onClick={() => onToggle(node.slug)}
        style={{ paddingLeft: 4 + depth * 12 }}
        className="w-full text-left py-1 text-[11px] font-mono uppercase tracking-wide text-muted-foreground hover:text-foreground flex items-center gap-1"
      >
        {isOpen ? (
          <ChevronDown className="size-3 shrink-0" />
        ) : (
          <ChevronRight className="size-3 shrink-0" />
        )}
        <span className="truncate">{node.label}</span>
        <span className="ml-auto font-mono text-muted-foreground/60 pr-3">
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

function countLeaves(node: TreeNode): number {
  if (node.level === "section") return 1;
  let n = 0;
  for (const c of node.children) n += countLeaves(c);
  return n;
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

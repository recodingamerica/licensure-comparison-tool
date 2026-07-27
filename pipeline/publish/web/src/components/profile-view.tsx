"use client";

import type * as React from "react";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { BackLink } from "@/components/ui/back-link";
import { Eyebrow } from "@/components/ui/eyebrow";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { AgGridReact, useGridFilter } from "ag-grid-react";
import type { CustomFilterProps } from "ag-grid-react";
import {
  AllCommunityModule,
  ModuleRegistry,
  themeQuartz,
  type ColDef,
  type FilterChangedEvent,
  type GridApi,
  type IDoesFilterPassParams,
  type ICellRendererParams,
} from "ag-grid-community";
import type { DiscoveredField, ProfilePayload, Row } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { humanize, findAllSpans } from "@/lib/format";
import { SEMANTIC_CLASSES as SC, CATEGORY_CLASSES, token } from "@/lib/web-colors";
import { Absent, ABSENCE } from "./absence";
import { useOpenStateDetail } from "./state-focus";
import { MapView } from "./map-view";

// AG Grid v33+ requires modules to be registered before any grid instance
// is constructed. AllCommunityModule pulls in every community module —
// fine for our bundle since we're not optimizing for size on an internal tool.
ModuleRegistry.registerModules([AllCommunityModule]);

// ---------- Cell renderer components ----------

const PILL_YES = `${SC.permissive.bg} ${SC.permissive.text} ${SC.permissive.hoverBg}`;
const PILL_NO = `${SC.restrictive.bg} ${SC.restrictive.text} ${SC.restrictive.hoverBg}`;

function YesNoCell({ value }: ICellRendererParams<Row, boolean | null>) {
  if (value === true)
    return <Badge variant="secondary" className={PILL_YES}>yes</Badge>;
  if (value === false)
    return <Badge variant="secondary" className={PILL_NO}>no</Badge>;
  return <Absent kind="unknown" compact />;
}

function TextCellRenderer({ value }: ICellRendererParams<Row, string | number | null>) {
  if (value === null || value === undefined || value === "")
    return <Absent kind="unknown" compact />;
  return <span>{value}</span>;
}

// BucketAwareCell — wraps a renderer with a per-state bucket chip above the
// value. Bucket comes from map_prep.text_buckets (the Pass-3 LLM bucket of
// not_mappable free-text fields). When a state has no bucket assignment,
// falls through to just the inner renderer's output.
function makeBucketAwareCell(
  byState: Record<string, string>,
): (p: ICellRendererParams<Row, string | number | null>) => React.ReactElement {
  return function BucketAwareCell(p) {
    const state = p.data?.state;
    const bucket = state ? byState[state] : undefined;
    const v = p.value;
    const blank = v === null || v === undefined || v === "";
    return (
      <div className="flex flex-col gap-1 leading-snug">
        {bucket && (
          <Badge
            variant="outline"
            className="self-start font-mono text-[10px] px-1.5 py-0 bg-amber-50 text-amber-900 border-amber-300"
          >
            {bucket}
          </Badge>
        )}
        {blank ? (
          <span className="text-muted-foreground">—</span>
        ) : (
          <span className="text-sm">{v}</span>
        )}
      </div>
    );
  };
}

// "Statute text" cell — shows the per-row match count when the filter is
// active, blank when not. Reads the active filter from the grid API on
// demand so we don't have to pipe state through React. The cell only re-
// renders when AG Grid recomputes the row (which happens on filter change).
function StatuteTextHitsCell(params: ICellRendererParams<Row, string>) {
  if (!params.data || params.data.coverage_gap) return null;
  const model = (params.api.getFilterModel() ?? {})["statute_text"] as
    | { filter?: unknown }
    | undefined;
  const q = typeof model?.filter === "string" ? model.filter.trim() : "";
  if (!q) return null;
  const text = params.value || "";
  const hits = findAllSpans(q, text).length;
  if (hits === 0) return null;
  return (
    <span
      className={`font-mono text-xs ${SC.highlight.text}`}
      title={`${hits} match${hits === 1 ? "" : "es"} for "${q}"`}
    >
      {hits} {hits === 1 ? "hit" : "hits"}
    </span>
  );
}

function VerifyCell({ data }: ICellRendererParams<Row>) {
  if (!data) return null;
  if (data.coverage_gap) return null;
  const u = data.evidence_unverified || 0;
  // Verified-everywhere is the common case (>99% of rows). Stay silent so
  // the eye can lock onto the rows that DO need attention.
  if (u === 0) return null;
  return (
    <span
      className={`font-mono text-xs ${SC.attention.text}`}
      title="Quotes that did not match the cleaned source verbatim"
    >
      ⚠ {u}
    </span>
  );
}

const COMPACT_FULL: Record<string, string> = {
  NLC: "Nurse Licensure Compact",
  IMLC: "Interstate Medical Licensure Compact",
  PTC: "Physical Therapy Compact",
  "ASLP-IC": "Audiology and Speech-Language Pathology Interstate Compact",
  "PSY-PACT": "Psychology Interjurisdictional Compact",
  "EMS-C": "EMS Personnel Licensure Interstate Compact",
  "OT-C": "Occupational Therapy Licensure Compact",
  CC: "Counseling Compact",
  "DDH-C": "Dentist and Dental Hygienist Compact",
  "OD-C": "Optometry Licensure Compact",
  "APRN-C": "Advanced Practice Registered Nurse Compact",
};

function CompactsCell({ value }: ICellRendererParams<Row, string[]>) {
  if (!value || value.length === 0)
    return <span className="text-muted-foreground">—</span>;
  return (
    <div className="flex flex-wrap gap-1 justify-center">
      {value.map((c) => (
        <Badge
          key={c}
          variant="secondary"
          className="bg-indigo-100 text-indigo-900 hover:bg-indigo-100 font-mono text-[10px]"
          title={COMPACT_FULL[c] || c}
        >
          {c}
        </Badge>
      ))}
    </div>
  );
}

// First word of a bucket label, for a dense chip. Generalizes across
// professions' LLM-generated bucket names (no hand-curated abbreviation map);
// the full label + count shows on hover and in the tag-sheet panel.
function shortCategory(label: string): string {
  return label.split(/\s*&\s*|\s+/)[0] || label;
}

// Resolve a row's per-state category tags for a given per-item field. The
// disciplinary field has its own top-level key; every other list field lives
// under list_field_categories keyed by dotted field name.
function categoriesFor(
  data: Row | undefined,
  key: string,
): { label: string; count: number }[] {
  if (!data) return [];
  if (key === "licensure.disciplinary_grounds")
    return data.disciplinary_categories ?? [];
  return data.list_field_categories?.[key] ?? [];
}

// Per-state content-tag chips ("Fraud 2", "Capsulotomy (YAG) 1", …) so the
// table surfaces WHICH items a state has, not just how many or a raw blob.
// The backing field is passed via cellRendererParams.categoriesKey; the
// column's valueGetter exposes the labels as an array for the multicheck
// filter. Generic across disciplinary grounds and every discovered list field.
function CategoryChipsCell(
  p: ICellRendererParams<Row, string[]> & {
    categoriesKey?: string;
  },
) {
  const cats = categoriesFor(p.data, p.categoriesKey ?? "");
  if (cats.length === 0)
    return <span className="text-muted-foreground">—</span>;
  return (
    <div className="flex flex-wrap gap-1 leading-tight">
      {cats.map((c) => (
        <Badge
          key={c.label}
          variant="secondary"
          // data-category is read back off the click event by handleCellClick, so the
          // Sheet can open ON the category you actually clicked instead of just the
          // column. Cheaper than threading a callback through static column defs.
          data-category={c.label}
          // Keyboard-reachable: Enter/Space dispatch a real click, which bubbles to the
          // same cell handler the mouse path uses, so both routes behave identically.
          role="button"
          tabIndex={0}
          onKeyDown={(e: React.KeyboardEvent<HTMLElement>) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              e.currentTarget.click();
            }
          }}
          className={`${SC.restrictive.bg} ${SC.restrictive.text} ${SC.restrictive.hoverBg} font-normal text-[10px] px-1.5 py-0 cursor-pointer hover:ring-1 hover:ring-current/40 focus-visible:outline-none focus-visible:ring-2 ${SC.interaction.focusRing}`}
          title={`${c.label} — ${c.count} · click to open this state's ${c.label} items`}
        >
          {shortCategory(c.label)}
          <span className="ml-1 font-mono opacity-70">{c.count}</span>
        </Badge>
      ))}
    </div>
  );
}

function RegulatoryModelCell({ data, value }: ICellRendererParams<Row, string | null>) {
  if (data?.coverage_gap) {
    return (
      <span
        className="text-xs italic text-muted-foreground"
        // Keep the per-cell reason when we have it — it says WHY, which the generic
        // vocabulary can't. Fall back to the shared wording so the phrasing is
        // consistent when we don't.
        title={data.coverage_gap_reason || ABSENCE["no-statute"].help}
      >
        {data.coverage_gap_label || ABSENCE["no-statute"].label}
      </span>
    );
  }
  if (!value) return <span className="text-muted-foreground">—</span>;
  const c = CATEGORY_CLASSES.regulatory[value];
  const cls = c ? `${c.bg} ${c.text} ${c.hoverBg}` : "bg-muted text-muted-foreground";
  return (
    <Badge variant="secondary" className={cls}>
      {humanize(value)}
    </Badge>
  );
}

function CredentialTypeCell({ data }: ICellRendererParams<Row>) {
  if (!data || data.coverage_gap) return <span className="text-muted-foreground">—</span>;
  const ct = data.credential_type;
  const mandatory = data.is_mandatory;
  if (!ct && mandatory === null) return <span className="text-muted-foreground">—</span>;
  const c = ct ? CATEGORY_CLASSES.regulatory[ct] : undefined;
  const cls = ct ? (c ? `${c.bg} ${c.text}` : "bg-muted text-muted-foreground") : "";
  // The mandatory/voluntary annotation only adds information when the
  // credential type doesn't already imply it. License + registration are
  // mandatory by definition; "none" + "exemption" don't have a meaningful
  // mandatory axis. Only certification genuinely splits mandatory vs
  // voluntary, so only render the annotation for that case.
  const mandLabel =
    ct === "certification"
      ? mandatory === true
        ? "mandatory"
        : mandatory === false
          ? "voluntary"
          : null
      : null;
  return (
    <div className="flex flex-col items-start gap-0.5 py-1">
      {ct && (
        <Badge variant="secondary" className={cls + " hover:" + cls}>
          {humanize(ct)}
        </Badge>
      )}
      {mandLabel && (
        <span
          className={
            "text-[10px] font-mono uppercase tracking-wide " +
            (mandatory ? "text-foreground" : "text-muted-foreground italic")
          }
        >
          {mandLabel}
        </span>
      )}
    </div>
  );
}

function CeCell({ data }: ICellRendererParams<Row>) {
  if (!data) return null;
  if (data.ce_hours == null && data.ce_period_years == null)
    return <span className="text-muted-foreground">—</span>;
  return (
    <span className="whitespace-nowrap">
      {data.ce_hours ?? "—"} / {data.ce_period_years ?? "—"}
    </span>
  );
}

// ---------- Column visibility popover (state-managed, no portal) ----------
// Rolled by hand rather than via Base UI's DropdownMenu — the Base UI
// dropdown was the source of two prior client-side errors, and a small
// custom popover keeps this control isolated from that ecosystem.

function ColumnVisibilityPopover({
  columns,
  visible,
  onToggle,
}: {
  // `category` is the field's discovered_fields[].category (for profession-
  // specific columns) or undefined for the universal cross-state columns.
  // When present, the popover groups items under indented category headers
  // — matches how StateDetailDialog organizes the same fields in its
  // side modal so the two surfaces feel consistent.
  columns: Array<{ id: string; label: string; category?: string }>;
  visible: Set<string>;
  onToggle: (id: string, v: boolean) => void;
}) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const ref = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);

  // Close on outside click + Escape
  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onClick);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  // Focus the search box on open and reset the filter on close so re-opening
  // doesn't show a stale query.
  useEffect(() => {
    if (open) {
      searchRef.current?.focus();
    } else {
      setQuery("");
    }
  }, [open]);

  // Group by category (universal columns get the "Cross-state fields"
  // bucket; profession-specific ones get their discovered_fields.category).
  // Within each group, sort alphabetically. With a search query, prune to
  // matching items first, then drop empty groups.
  const grouped = useMemo(() => {
    const UNIVERSAL = "Cross-state fields";
    const q = query.trim().toLowerCase();
    const matches = !q
      ? [...columns]
      : columns.filter((c) => c.label.toLowerCase().includes(q));
    const byCat = new Map<string, typeof columns>();
    for (const c of matches) {
      const cat = c.category || UNIVERSAL;
      if (!byCat.has(cat)) byCat.set(cat, []);
      byCat.get(cat)!.push(c);
    }
    // Sort items inside each group; sort group keys alphabetically with
    // UNIVERSAL pinned to the top so the cross-state core lives first.
    const result: Array<[string, typeof columns]> = [];
    const cats = Array.from(byCat.keys()).sort((a, b) => {
      if (a === UNIVERSAL) return -1;
      if (b === UNIVERSAL) return 1;
      return a.localeCompare(b);
    });
    for (const cat of cats) {
      const items = byCat.get(cat)!.slice().sort((a, b) => a.label.localeCompare(b.label));
      result.push([cat, items]);
    }
    return result;
  }, [columns, query]);
  const totalFiltered = useMemo(
    () => grouped.reduce((n, [, items]) => n + items.length, 0),
    [grouped],
  );

  // Keep the panel on-screen: it's anchored `right-0` off the trigger, so when
  // the trigger sits near a viewport edge the fixed-width panel would spill off
  // (Atharv #75: "shows up half off-screen"). After it opens, measure and nudge
  // it horizontally so both edges stay within an 8px margin.
  const menuRef = useRef<HTMLDivElement>(null);
  const [shiftX, setShiftX] = useState(0);
  useEffect(() => {
    if (!open) {
      setShiftX(0);
      return;
    }
    const el = menuRef.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    const M = 8;
    if (r.left < M) setShiftX(M - r.left);
    else if (r.right > window.innerWidth - M) setShiftX(window.innerWidth - M - r.right);
  }, [open]);

  return (
    <div ref={ref} className="relative inline-block">
      <Button
        variant="outline"
        size="sm"
        className="font-mono text-xs"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
      >
        Columns ({visible.size}/{columns.length}) ▾
      </Button>
      {open && (
        <div
          ref={menuRef}
          role="menu"
          style={shiftX ? { transform: `translateX(${shiftX}px)` } : undefined}
          className="absolute right-0 top-full mt-1 w-80 max-h-[70vh] flex flex-col rounded-md border bg-popover text-popover-foreground shadow-md z-50"
        >
          <div className="px-2 pt-2 pb-1.5 text-xs font-mono uppercase tracking-widest text-muted-foreground">
            Show / hide columns
          </div>
          <div className="px-2 pb-2">
            <input
              ref={searchRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search columns…"
              className="w-full rounded border bg-background px-2 py-1 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            />
          </div>
          <div className="px-2 pb-1.5 text-xs text-muted-foreground flex items-center justify-between gap-2">
            <span>
              {totalFiltered === columns.length
                ? `${columns.length} columns`
                : `${totalFiltered} of ${columns.length} match`}
            </span>
            {/* Bulk actions act on the CURRENT filtered set so users can e.g.
                search "ce_" then click "hide all" to hide every CE column. */}
            <div className="flex gap-1">
              <button
                className="hover:text-foreground underline"
                onClick={() =>
                  grouped.forEach(([, items]) => items.forEach((c) => onToggle(c.id, true)))
                }
              >
                show all
              </button>
              <span>·</span>
              <button
                className="hover:text-foreground underline"
                onClick={() =>
                  grouped.forEach(([, items]) => items.forEach((c) => onToggle(c.id, false)))
                }
              >
                hide all
              </button>
            </div>
          </div>
          <div className="my-1 h-px bg-border" />
          <div className="overflow-y-auto p-1">
            {totalFiltered === 0 ? (
              <div className="px-2 py-3 text-sm text-muted-foreground text-center">
                no columns match "{query}"
              </div>
            ) : (
              grouped.map(([cat, items]) => (
                <div key={cat} className="mb-1">
                  <div className="px-2 pt-1.5 pb-1 text-[11px] font-mono uppercase tracking-widest text-muted-foreground flex items-center justify-between gap-2">
                    <span>{cat}</span>
                    <span className="flex gap-1 text-[10px]">
                      <button
                        type="button"
                        className="hover:text-foreground underline"
                        onClick={() => items.forEach((c) => onToggle(c.id, true))}
                      >
                        all
                      </button>
                      <span>·</span>
                      <button
                        type="button"
                        className="hover:text-foreground underline"
                        onClick={() => items.forEach((c) => onToggle(c.id, false))}
                      >
                        none
                      </button>
                    </span>
                  </div>
                  {items.map((c) => (
                    <label
                      key={c.id}
                      className="flex items-center gap-2 pl-5 pr-2 py-1.5 rounded text-sm hover:bg-accent hover:text-accent-foreground cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={visible.has(c.id)}
                        onChange={(e) => onToggle(c.id, e.target.checked)}
                        className="h-4 w-4 rounded border-input"
                      />
                      <span>{c.label}</span>
                    </label>
                  ))}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ---------- Filter chip ----------

function FilterChip({
  label,
  value,
  onRemove,
}: {
  label: string;
  value: string;
  onRemove: () => void;
}) {
  return (
    <Badge
      variant="secondary"
      className="bg-amber-50 border border-amber-200 text-amber-900 hover:bg-amber-50 gap-1 font-mono text-xs pl-2 pr-1 py-0.5"
    >
      <span className="font-semibold">{label}:</span>
      <span className="font-normal">{value}</span>
      <button
        type="button"
        onClick={onRemove}
        className="ml-0.5 hover:bg-amber-200 rounded-full w-4 h-4 inline-flex items-center justify-center text-amber-900"
        aria-label={`Remove ${label} filter`}
      >
        ×
      </button>
    </Badge>
  );
}

// ---------- Custom multi-checkbox filter ----------
// AG Grid Community's built-in Set Filter (the multiselect-of-unique-values
// pattern from pull_usaspending) is Enterprise. This is a small workalike:
// scans the visible rows for unique values, renders one checkbox per value,
// passes when the cell's value is in the selected set.
//
// Implemented against AG Grid React's v35 `CustomFilterProps` API:
// the grid passes `model` + `onModelChange`; we push the current
// selection up via `onModelChange` and the grid re-runs `doesFilterPass`
// (registered with `useGridFilter`). The earlier forwardRef + ref API
// (`props.filterChangedCallback`) silently no-ops in v35 — that prop
// doesn't exist, so clicking a checkbox would throw and the filter
// never applied.

type MulticheckModel = { values: string[] } | null;

function MulticheckFilter(
  props: CustomFilterProps<Row, unknown, MulticheckModel>
) {
  const { model, onModelChange, api, getValue } = props;
  const [query, setQuery] = useState("");

  // Selected values come from the grid-owned model; React state is only
  // used for the in-popup search query.
  const selected = useMemo(
    () => new Set<string>(model?.values ?? []),
    [model],
  );

  // Unique non-null values across all loaded rows for this column.
  const uniqueValues = useMemo(() => {
    const set = new Set<string>();
    api.forEachNode((node) => {
      if (!node.data) return;
      const v = getValue(node);
      if (v == null || v === "") return;
      if (Array.isArray(v)) {
        for (const x of v) {
          if (x != null && x !== "") set.add(String(x));
        }
      } else {
        set.add(String(v));
      }
    });
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }, [api, getValue]);

  const filteredValues = useMemo(
    () =>
      query
        ? uniqueValues.filter((v) =>
            v.toLowerCase().includes(query.toLowerCase()),
          )
        : uniqueValues,
    [uniqueValues, query],
  );

  // Register the per-row filter predicate with the grid. Re-registers
  // whenever `selected` changes so doesFilterPass sees the current set.
  const doesFilterPass = useCallback(
    (params: IDoesFilterPassParams<Row>) => {
      const v = getValue(params.node);
      if (Array.isArray(v)) return v.some((x) => selected.has(String(x)));
      if (v == null) return false;
      return selected.has(String(v));
    },
    [getValue, selected],
  );
  useGridFilter({ doesFilterPass });

  const setSelected = (next: Set<string>) => {
    onModelChange(next.size > 0 ? { values: Array.from(next) } : null);
  };

  const toggle = (v: string) => {
    const next = new Set(selected);
    if (next.has(v)) next.delete(v);
    else next.add(v);
    setSelected(next);
  };

  return (
    <div className="p-2 w-56 text-sm">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Filter values…"
        className="w-full mb-2 px-2 py-1 border rounded text-xs"
      />
      <div className="flex items-center justify-between text-[10px] font-mono uppercase tracking-widest text-muted-foreground mb-1">
        <button
          type="button"
          onClick={() => setSelected(new Set(uniqueValues))}
          className="hover:text-foreground"
        >
          all
        </button>
        <span>{selected.size} selected</span>
        <button
          type="button"
          onClick={() => setSelected(new Set())}
          className="hover:text-foreground"
        >
          none
        </button>
      </div>
      <div className="max-h-60 overflow-y-auto">
        {filteredValues.length === 0 && (
          <div className="text-muted-foreground text-xs py-1">No values.</div>
        )}
        {filteredValues.map((v) => (
          <label
            key={v}
            className="flex items-center gap-2 px-1 py-0.5 rounded hover:bg-accent cursor-pointer"
          >
            <input
              type="checkbox"
              checked={selected.has(v)}
              onChange={() => toggle(v)}
              className="h-4 w-4"
            />
            <span className="truncate" title={v}>
              {humanize(v)}
            </span>
          </label>
        ))}
      </div>
    </div>
  );
}


// ---------- Helpers for drilling into the structured record ----------

type EvidenceLike = { value: unknown; quote?: unknown; citation?: unknown; unverified?: boolean };

function isEvidence(x: unknown): x is EvidenceLike {
  return (
    typeof x === "object" &&
    x !== null &&
    "value" in (x as Record<string, unknown>)
  );
}

function ev(data: Row | undefined, ...path: string[]): unknown {
  if (!data || !data._full) return undefined;
  let cur: unknown = data._full;
  for (const p of path) {
    if (cur == null || typeof cur !== "object") return undefined;
    cur = (cur as Record<string, unknown>)[p];
  }
  if (isEvidence(cur)) return cur.value;
  return cur;
}

// Like ev(), but returns true when the Evidence node at the given path
// has unverified: true. Used to drive per-cell .cell-unverified styling.
function evUnverified(data: Row | undefined, ...path: string[]): boolean {
  if (!data || !data._full) return false;
  let cur: unknown = data._full;
  for (const p of path) {
    if (cur == null || typeof cur !== "object") return false;
    cur = (cur as Record<string, unknown>)[p];
  }
  return isEvidence(cur) && cur.unverified === true;
}


// ---------- Column definitions ----------
// AG Grid's per-column filter gives us the popover-from-the-header pattern
// users are used to. Categorical columns get MulticheckFilter (Community
// workalike for the Enterprise Set Filter); text/number columns use the
// built-in text/number filters.
//
// `initialHide: true` means the column is registered but not shown by
// default — users opt in via the Columns ▾ dropdown. Why `initialHide`
// instead of `hide`: in AG Grid v35, `hide` in colDef is reapplied on
// every render, which clobbers `applyColumnState` calls. `initialHide`
// is consulted ONLY on first registration, so toggle stays sticky.
// (Atharv's issue #11: column appeared "toggled on" but never showed.)

// Cardinality threshold for auto-choosing the multi-checkbox filter. Columns
// whose unique-value count across the dataset falls at or below this number
// get MulticheckFilter; anything higher falls back to the text/number filter
// appropriate for the column's underlying type. 25 picked empirically — most
// "categorical-ish" columns (regulation rung, compacts, accrediting bodies,
// renewal years, supervisor titles) sit well under that; free-text columns
// like Licensing Authority blow past it.
const MULTICHECK_CARDINALITY_THRESHOLD = 25;

// Extract a row's value for a given column def, mirroring what AG Grid would
// compute. Used at build time to count unique values so we can pick the
// right filter type.
function extractColValue(c: ColDef<Row>, row: Row): unknown {
  // A filterValueGetter overrides field/valueGetter for what the filter sees
  // (getValue), so cardinality must be counted on it too — otherwise a column
  // whose cells show free text but filters on a small normalized enum (e.g.
  // Education → degree_level) would be miscounted as high-cardinality and lose
  // its multicheck dropdown.
  if (typeof c.filterValueGetter === "function") {
    return (
      c.filterValueGetter as unknown as (p: { data: Row; node: { data: Row } }) => unknown
    )({ data: row, node: { data: row } });
  }
  if (c.field) {
    return (row as unknown as Record<string, unknown>)[c.field as string];
  }
  if (typeof c.valueGetter === "function") {
    // valueGetter expects a ValueGetterParams; only data/node.data matter
    // for our defs. Cast minimally; nothing else is read.
    return (
      c.valueGetter as unknown as (p: { data: Row; node: { data: Row } }) => unknown
    )({ data: row, node: { data: row } });
  }
  return undefined;
}

// Count distinct non-null values across rows. Treats array elements as
// individual values (so "compacts: [NLC]" contributes "NLC"). Short-circuits
// once we exceed the threshold so big string columns don't waste cycles.
function uniqueValueCount(
  c: ColDef<Row>,
  rows: Row[],
  earlyExitAt: number
): number {
  const seen = new Set<string>();
  for (const r of rows) {
    const v = extractColValue(c, r);
    if (v == null || v === "") continue;
    if (Array.isArray(v)) {
      for (const x of v) {
        if (x != null && x !== "") seen.add(String(x));
      }
    } else {
      seen.add(String(v));
    }
    if (seen.size > earlyExitAt) return seen.size;
  }
  return seen.size;
}

// Decide which AG Grid filter to use for a column based on observed
// cardinality. Numeric / string / list columns all collapse to multicheck
// once we know there's a small set of distinct values — that's what the
// user almost always wants ("show me states where renewal is 1 or 2",
// "show me only NLC compacts"). Anything broader stays a contains-text
// filter (or number filter for explicit numeric columns).
function inferFilter(
  c: ColDef<Row>,
  rows: Row[]
): ColDef<Row>["filter"] {
  const n = uniqueValueCount(c, rows, MULTICHECK_CARDINALITY_THRESHOLD);
  if (n === 0) return c.filter ?? "agTextColumnFilter";
  if (n <= MULTICHECK_CARDINALITY_THRESHOLD) return MulticheckFilter;
  return c.filter === "agNumberColumnFilter"
    ? "agNumberColumnFilter"
    : "agTextColumnFilter";
}

// Maps colId / field name → the _full path whose Evidence.unverified flag
// controls per-cell amber styling. Each entry is the argument list for
// evUnverified(data, ...path). Compound columns (continuing_ed) that draw
// from two Evidence nodes are listed under UNVERIFIED_COMPOUND.
const UNVERIFIED_PATHS: Record<string, string[]> = {
  regulatory_model:          ["licensure", "regulatory_model"],
  issuing_authority:         ["licensure", "issuing_authority"],
  education_degree:          ["licensure", "education", "degree_required"],
  post_degree_duration:      ["licensure", "post_degree_experience", "duration"],
  renewal_years:             ["licensure", "renewal", "interval_years"],
  reciprocity_available:     ["licensure", "reciprocity", "available"],
  advisory_board_exists:     ["licensure", "advisory_board", "exists"],
  national_certification:    ["licensure", "national_certification"],
  national_association:      ["licensure", "national_association"],
  renewal_fee_usd:           ["licensure", "renewal_fee_usd"],
  credential_type:           ["licensure", "credential_type"],
  license_required:          ["licensure", "license_required"],
  title_protection:          ["licensure", "title_protection"],
  scope_protection:          ["licensure", "scope_protection"],
  is_mandatory:              ["licensure", "is_mandatory"],
  age_minimum:               ["licensure", "age_minimum"],
  moral_character_required:  ["licensure", "moral_character_required"],
  education_accrediting_body:["licensure", "education", "accrediting_body"],
  education_degree_level:    ["licensure", "education", "degree_level"],
  education_approval_basis:  ["licensure", "education", "school_approval_basis"],
  education_credential_pegged:["licensure", "education", "credential_pegged"],
  post_degree_required:      ["licensure", "post_degree_experience", "required"],
  post_degree_kind:          ["licensure", "post_degree_experience", "kind"],
  experience_source:         ["licensure", "post_degree_experience", "experience_source"],
  ce_required:               ["licensure", "continuing_education", "required"],
  ce_hours_per_period:       ["licensure", "continuing_education", "hours_per_period"],
  ce_period_years:           ["licensure", "continuing_education", "period_years"],
  ce_topical_requirements:   ["licensure", "continuing_education", "topical_requirements"],
  reciprocity_requirements:  ["licensure", "reciprocity", "requirements"],
  scope_definition:          ["scope", "definition_quote"],
  scope_methods:             ["scope", "methods_authorized"],
  scope_drug_authority:      ["scope", "drug_authority"],
};

// Columns whose value comes from more than one Evidence node — flag the cell
// if ANY of its backing nodes is unverified.
const UNVERIFIED_COMPOUND: Record<string, string[][]> = {
  continuing_ed: [
    ["licensure", "continuing_education", "hours_per_period"],
    ["licensure", "continuing_education", "period_years"],
  ],
};

// Maps universal column field → dotted path used as the key in
// map_prep.text_buckets. Keep aligned with UNVERIFIED_PATHS where applicable.
const BUCKET_PATHS: Record<string, string> = {
  issuing_authority: "licensure.issuing_authority",
  education_degree: "licensure.education.degree_required",
  post_degree_duration: "licensure.post_degree_experience.duration",
};

// Format a raw grid cell value for export (CSV + XLSX) so the file carries the
// same human-readable layer the grid renders through React cellRenderers — which
// AG Grid's exporters can't see. Mirrors YesNoCell and makeBucketAwareCell, and
// strips newlines so a multi-line cell can't be split on import (#28). Shared by
// both export buttons so the two outputs never drift.
type ExportTextBuckets = Record<string, { by_state: Record<string, string> }>;
function exportCellValue(
  value: unknown,
  colId: string | undefined,
  state: string | undefined,
  textBuckets: ExportTextBuckets,
): string {
  let out: string;
  if (value == null || value === "") out = "";
  else if (typeof value === "boolean") out = value ? "Yes" : "No";
  else if (Array.isArray(value)) out = value.join("; ");
  else if (typeof value === "object") out = JSON.stringify(value);
  else out = String(value);
  out = out.replace(/\s*\r?\n\s*/g, " ").trim();
  const bucketPath = colId ? BUCKET_PATHS[colId] : undefined;
  const bucket =
    bucketPath && state ? textBuckets[bucketPath]?.by_state?.[state] : undefined;
  if (bucket) out = out ? `${bucket} — ${out}` : bucket;
  return out;
}

// UORF six-rung ladder, low → high strictness (matches RegulatoryModel enum in
// pipeline/extract/standard_model.py). Used as a sort ordinal only — the rung
// names are categorical and we never display the number. Sorting on the raw
// string would order alphabetically (license < market_forces < …), which is wrong.
const UORF_RUNG_ORDER: Record<string, number> = {
  market_forces: 0,
  voluntary_certification: 1,
  registration: 2,
  exemption: 3,
  mandatory_certification: 4,
  license: 5,
};

function regulatoryModelComparator(
  a: string | null | undefined,
  b: string | null | undefined,
): number {
  const rank = (v: string | null | undefined) =>
    v != null && v in UORF_RUNG_ORDER ? UORF_RUNG_ORDER[v] : 99; // null/unknown sort last
  return rank(a) - rank(b);
}

// Education floor, low -> high (matches DegreeLevel enum in standard_model.py).
// Sort ordinal only; same reason as UORF — alphabetical would order the rungs
// nonsensically (associate < bachelor < doctorate is right; alpha isn't).
const DEGREE_LEVEL_ORDER: Record<string, number> = {
  none: 0,
  high_school: 1,
  associate: 2,
  bachelor: 3,
  master: 4,
  doctorate: 5,
};

function degreeLevelComparator(
  a: string | null | undefined,
  b: string | null | undefined,
): number {
  const rank = (v: string | null | undefined) =>
    v != null && v in DEGREE_LEVEL_ORDER ? DEGREE_LEVEL_ORDER[v] : 99;
  return rank(a) - rank(b);
}

function buildColumnDefs(
  discoveredFields: DiscoveredField[],
  rows: Row[],
  textBuckets: Record<string, { bucket_set: string[]; rationale: string; by_state: Record<string, string> }>,
): ColDef<Row>[] {
  const cols: ColDef<Row>[] = [
  {
    field: "state",
    headerName: "State",
    width: 100,
    pinned: "left",
    filter: "agTextColumnFilter",
    lockVisible: true, // can't hide the state identifier column
  },
  {
    field: "regulatory_model",
    headerName: "Regulation (UORF)",
    width: 170,
    cellRenderer: RegulatoryModelCell,
    filter: MulticheckFilter,
    comparator: regulatoryModelComparator, // sort by rung strictness, not alphabetically
    headerTooltip: "Six-rung UORF ladder",
  },
  {
    colId: "credential_type",
    headerName: "Credential type",
    width: 150,
    valueGetter: (p) => p.data?.credential_type,
    cellRenderer: CredentialTypeCell,
    filter: MulticheckFilter,
    headerTooltip:
      "Orthogonal to UORF rung: license / certification / registration / exemption + mandatory/voluntary",
    // Hidden by default — for the common "license × mandatory" case it
    // duplicates the Regulation (UORF) column. Users opt in via the
    // Columns ▾ dropdown when they want the orthogonal decomposition.
    initialHide: true,
  },
  {
    field: "issuing_authority",
    headerName: "Licensing Authority",
    width: 230,
    cellRenderer: textBuckets[BUCKET_PATHS.issuing_authority]
      ? makeBucketAwareCell(textBuckets[BUCKET_PATHS.issuing_authority].by_state)
      : TextCellRenderer,
    filter: "agTextColumnFilter",
    wrapText: true,
    cellClass: "leading-snug",
  },
  {
    field: "education_degree",
    context: { fieldPath: "licensure.education.degree_required" },
    headerName: "Education (Min. Degree)",
    width: 260,
    cellRenderer: textBuckets[BUCKET_PATHS.education_degree]
      ? makeBucketAwareCell(textBuckets[BUCKET_PATHS.education_degree].by_state)
      : TextCellRenderer,
    // Cells show the verbatim degree text, but filter on the normalized
    // degree_level enum so the header dropdown offers a short tag list
    // (Associate/Bachelor's/… ) instead of dozens of free-text strings
    // (Atharv #75). filterValueGetter drives both the dropdown values and the
    // pass predicate via the filter's getValue.
    filterValueGetter: (p) => ev(p.data, "licensure", "education", "degree_level"),
    filter: MulticheckFilter,
    wrapText: true,
    cellClass: "leading-snug",
  },
  {
    field: "post_degree_duration",
    context: { fieldPath: "licensure.post_degree_experience.duration" },
    headerName: "Professional Experience",
    width: 180,
    cellRenderer: textBuckets[BUCKET_PATHS.post_degree_duration]
      ? makeBucketAwareCell(textBuckets[BUCKET_PATHS.post_degree_duration].by_state)
      : TextCellRenderer,
    filter: "agTextColumnFilter",
    wrapText: true,
    cellClass: "leading-snug",
  },
  {
    field: "exams_count",
    // Summarizes a list, so it points at the Sheet SECTION rather than one field.
    context: { section: "Exams" },
    headerName: "Exams",
    width: 95,
    cellRenderer: TextCellRenderer,
    filter: "agNumberColumnFilter",
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    field: "renewal_years",
    context: { fieldPath: "licensure.renewal.interval_years" },
    headerName: "Renewal (yrs)",
    width: 130,
    cellRenderer: TextCellRenderer,
    filter: MulticheckFilter,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "continuing_ed",
    context: { fieldPath: "licensure.continuing_education.required" },
    headerName: "Continuing Ed",
    width: 130,
    valueGetter: (p) =>
      p.data && (p.data.ce_hours != null || p.data.ce_period_years != null)
        ? `${p.data.ce_hours ?? "—"} / ${p.data.ce_period_years ?? "—"}`
        : null,
    cellRenderer: CeCell,
    filter: "agTextColumnFilter",
    cellClass: "text-center",
    headerClass: "text-center",
    headerTooltip: "CE hours required / renewal period in years",
  },
  {
    field: "reciprocity_available",
    context: { fieldPath: "licensure.reciprocity.available" },
    headerName: "Reciprocity",
    width: 120,
    cellRenderer: YesNoCell,
    filter: MulticheckFilter,
    valueFormatter: (p) =>
      p.value === true ? "yes" : p.value === false ? "no" : "",
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    field: "compacts",
    headerName: "Compacts",
    width: 130,
    cellRenderer: CompactsCell,
    filter: MulticheckFilter,
    valueFormatter: (p) =>
      Array.isArray(p.value) ? p.value.join(" ") : "",
    cellClass: "text-center",
    headerClass: "text-center",
  },
  // ── Universal-comparison fields aligned with Atharv's cross-state schema.
  // Header names use his vocabulary from the PDF table so the column labels
  // line up with what he uses in his own analysis.
  {
    field: "advisory_board_exists",
    context: { fieldPath: "licensure.advisory_board.exists" },
    headerName: "Advisory Board",
    width: 130,
    cellRenderer: YesNoCell,
    filter: MulticheckFilter,
    headerTooltip:
      "Does a profession-specific advisory body sit alongside a generic licensing board? `no` when the licensing board itself is profession-specific.",
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    field: "advisory_board_name",
    context: { fieldPath: "licensure.advisory_board.name" },
    headerName: "Advisory Board Name",
    width: 220,
    cellRenderer: TextCellRenderer,
    filter: "agTextColumnFilter",
    wrapText: true,
    cellClass: "leading-snug",
    initialHide: true, // mostly empty (only states with a separate advisory body)
  },
  {
    field: "advisory_board_authority",
    context: { fieldPath: "licensure.advisory_board.authority" },
    headerName: "Advisory Board Authority",
    width: 260,
    cellRenderer: TextCellRenderer,
    filter: "agTextColumnFilter",
    wrapText: true,
    cellClass: "leading-snug",
    initialHide: true, // long free text from the statute
  },
  {
    field: "national_certification",
    headerName: "National Certification",
    width: 220,
    cellRenderer: TextCellRenderer,
    filter: MulticheckFilter,
    wrapText: true,
    cellClass: "leading-snug",
    headerTooltip:
      "National certifying body the statute recognizes or requires (e.g. NBPME, ABPS, ECFMG).",
  },
  {
    field: "national_association",
    headerName: "National Association",
    width: 220,
    cellRenderer: TextCellRenderer,
    filter: MulticheckFilter,
    wrapText: true,
    cellClass: "leading-snug",
    headerTooltip:
      "Professional association the statute references (e.g. APMA, ADA, AMA). Distinct from the certifying body.",
  },
  {
    field: "renewal_fee_usd",
    context: { fieldPath: "licensure.renewal_fee_usd" },
    headerName: "Renewal Fee ($)",
    width: 130,
    cellRenderer: TextCellRenderer,
    filter: "agNumberColumnFilter",
    cellClass: "text-center",
    headerClass: "text-center",
    headerTooltip:
      "License renewal fee in USD when fixed by statute. Blank when the statute leaves the amount to board discretion.",
  },
  {
    colId: "statute_text",
    headerName: "Statute text",
    width: 130,
    // Hidden full corpus of statute language for this (state, profession).
    // Cell shows match count when the filter is active, otherwise blank —
    // gives the column visible signal during a search without cluttering
    // it when not in use. AG Grid's built-in agTextColumnFilter does
    // case-insensitive substring matching against the valueGetter result;
    // rows whose section_text_full contains the query stay visible.
    valueGetter: (p) => p.data?.section_text_full ?? "",
    cellRenderer: StatuteTextHitsCell,
    filter: "agTextColumnFilter",
    filterParams: {
      // Default to "contains" so users don't have to pick an operator.
      defaultOption: "contains",
      // Hide the operator dropdown — too much UI for a use case where 99%
      // of queries are "find this phrase somewhere in the statute".
      suppressAndOrCondition: true,
      filterOptions: ["contains"],
      buttons: ["reset"],
      // Don't surface the giant string in the popover's value preview.
      caseSensitive: false,
    },
    cellClass: "text-center",
    headerClass: "text-center",
    initialHide: true,
    headerTooltip:
      "Search the full statute text shipped for this state. Case-insensitive substring match. Matches anywhere in the combined chapter + umbrella text.",
  },
  {
    colId: "evidence",
    headerName: "Unverified",
    width: 110,
    initialHide: true,
    // Only the count of NOT-matched quotes per state. Cell renders blank when 0
    // so visual scanning surfaces only the rows that need attention. Auto-
    // multicheck picks this up — values are 0 / 1 / ... so users see
    // checkboxes for each level and check whichever they want.
    valueGetter: (p) => p.data?.evidence_unverified ?? 0,
    cellRenderer: VerifyCell,
    cellClass: "text-center",
    headerClass: "text-center",
    headerTooltip:
      "How many quotes in this state's record aren't a word-for-word span of the statute (the model paraphrased or shortened the wording). It flags the quote text, not whether the values are correct. Blank means every quote matched verbatim.",
  },

  // ── Additional universal columns (default-hidden; opt in via Columns ▾)
  {
    colId: "license_required",
    headerName: "License required?",
    valueGetter: (p) => ev(p.data, "licensure", "license_required"),
    // Dotted record path, co-located with the column that owns it: the Sheet
    // filters by path, so nothing has to keep a colId->label table in sync.
    context: { fieldPath: "licensure.license_required" },
    cellRenderer: YesNoCell,
    filter: MulticheckFilter,
    width: 130,
    initialHide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "title_protection",
    headerName: "Title protection",
    valueGetter: (p) => p.data?.title_protection,
    cellRenderer: YesNoCell,
    filter: MulticheckFilter,
    width: 130,
    initialHide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "scope_protection",
    headerName: "Scope protection",
    valueGetter: (p) => p.data?.scope_protection,
    cellRenderer: YesNoCell,
    filter: MulticheckFilter,
    width: 130,
    initialHide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "is_mandatory",
    headerName: "Mandatory?",
    valueGetter: (p) => p.data?.is_mandatory,
    cellRenderer: YesNoCell,
    filter: MulticheckFilter,
    width: 130,
    initialHide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "age_minimum",
    headerName: "Age minimum",
    valueGetter: (p) => ev(p.data, "licensure", "age_minimum"),
    // Dotted record path, co-located with the column that owns it: the Sheet
    // filters by path, so nothing has to keep a colId->label table in sync.
    context: { fieldPath: "licensure.age_minimum" },
    cellRenderer: TextCellRenderer,
    filter: "agNumberColumnFilter",
    width: 130,
    initialHide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "moral_character_required",
    headerName: "Moral character required?",
    valueGetter: (p) => ev(p.data, "licensure", "moral_character_required"),
    // Dotted record path, co-located with the column that owns it: the Sheet
    // filters by path, so nothing has to keep a colId->label table in sync.
    context: { fieldPath: "licensure.moral_character_required" },
    cellRenderer: YesNoCell,
    filter: MulticheckFilter,
    width: 160,
    initialHide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "education_accrediting_body",
    headerName: "Accrediting body",
    valueGetter: (p) => ev(p.data, "licensure", "education", "accrediting_body"),
    // Dotted record path, co-located with the column that owns it: the Sheet
    // filters by path, so nothing has to keep a colId->label table in sync.
    context: { fieldPath: "licensure.education.accrediting_body" },
    cellRenderer: TextCellRenderer,
    filter: MulticheckFilter,
    width: 200,
    initialHide: true,
    wrapText: true,
  },
  {
    // #35: normalized education floor (enum), sorted by rung not alphabetically.
    colId: "education_degree_level",
    headerName: "Min degree (level)",
    valueGetter: (p) => ev(p.data, "licensure", "education", "degree_level"),
    // Dotted record path, co-located with the column that owns it: the Sheet
    // filters by path, so nothing has to keep a colId->label table in sync.
    context: { fieldPath: "licensure.education.degree_level" },
    cellRenderer: TextCellRenderer,
    filter: MulticheckFilter,
    comparator: degreeLevelComparator,
    width: 150,
    initialHide: true,
  },
  {
    // #35: who decides a school counts (board vs national accreditor).
    colId: "education_approval_basis",
    headerName: "School approval basis",
    valueGetter: (p) => ev(p.data, "licensure", "education", "school_approval_basis"),
    // Dotted record path, co-located with the column that owns it: the Sheet
    // filters by path, so nothing has to keep a colId->label table in sync.
    context: { fieldPath: "licensure.education.school_approval_basis" },
    cellRenderer: TextCellRenderer,
    filter: MulticheckFilter,
    width: 180,
    initialHide: true,
  },
  {
    // #35: pegged to a national credential (NBEO/CDR) rather than a stated degree.
    colId: "education_credential_pegged",
    headerName: "Credential-pegged?",
    valueGetter: (p) => ev(p.data, "licensure", "education", "credential_pegged"),
    // Dotted record path, co-located with the column that owns it: the Sheet
    // filters by path, so nothing has to keep a colId->label table in sync.
    context: { fieldPath: "licensure.education.credential_pegged" },
    cellRenderer: YesNoCell,
    filter: MulticheckFilter,
    width: 150,
    initialHide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    // #36: where the post-degree experience requirement lives.
    colId: "experience_source",
    headerName: "Experience source",
    valueGetter: (p) => ev(p.data, "licensure", "post_degree_experience", "experience_source"),
    // Dotted record path, co-located with the column that owns it: the Sheet
    // filters by path, so nothing has to keep a colId->label table in sync.
    context: { fieldPath: "licensure.post_degree_experience.experience_source" },
    cellRenderer: TextCellRenderer,
    filter: MulticheckFilter,
    width: 180,
    initialHide: true,
  },
  {
    colId: "post_degree_required",
    headerName: "Post-degree required?",
    valueGetter: (p) => ev(p.data, "licensure", "post_degree_experience", "required"),
    // Dotted record path, co-located with the column that owns it: the Sheet
    // filters by path, so nothing has to keep a colId->label table in sync.
    context: { fieldPath: "licensure.post_degree_experience.required" },
    cellRenderer: YesNoCell,
    filter: MulticheckFilter,
    width: 160,
    initialHide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "post_degree_kind",
    headerName: "Post-degree kind",
    valueGetter: (p) => ev(p.data, "licensure", "post_degree_experience", "kind"),
    // Dotted record path, co-located with the column that owns it: the Sheet
    // filters by path, so nothing has to keep a colId->label table in sync.
    context: { fieldPath: "licensure.post_degree_experience.kind" },
    cellRenderer: TextCellRenderer,
    filter: MulticheckFilter,
    width: 180,
    initialHide: true,
    wrapText: true,
  },
  {
    colId: "ce_required",
    headerName: "CE required?",
    valueGetter: (p) => ev(p.data, "licensure", "continuing_education", "required"),
    // Dotted record path, co-located with the column that owns it: the Sheet
    // filters by path, so nothing has to keep a colId->label table in sync.
    context: { fieldPath: "licensure.continuing_education.required" },
    cellRenderer: YesNoCell,
    filter: MulticheckFilter,
    width: 130,
    initialHide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "ce_hours_per_period",
    headerName: "CE hours/period",
    valueGetter: (p) => ev(p.data, "licensure", "continuing_education", "hours_per_period"),
    // Dotted record path, co-located with the column that owns it: the Sheet
    // filters by path, so nothing has to keep a colId->label table in sync.
    context: { fieldPath: "licensure.continuing_education.hours_per_period" },
    cellRenderer: TextCellRenderer,
    filter: "agNumberColumnFilter",
    width: 130,
    initialHide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "ce_period_years",
    headerName: "CE period (yrs)",
    valueGetter: (p) => ev(p.data, "licensure", "continuing_education", "period_years"),
    // Dotted record path, co-located with the column that owns it: the Sheet
    // filters by path, so nothing has to keep a colId->label table in sync.
    context: { fieldPath: "licensure.continuing_education.period_years" },
    cellRenderer: TextCellRenderer,
    filter: "agNumberColumnFilter",
    width: 130,
    initialHide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "ce_topical_requirements",
    context: { fieldPath: "licensure.continuing_education.topical_requirements" },
    headerName: "CE topical requirements",
    valueGetter: (p) => {
      const v = ev(p.data, "licensure", "continuing_education", "topical_requirements");
      return Array.isArray(v) ? v.join(", ") : v;
    },
    cellRenderer: TextCellRenderer,
    filter: "agTextColumnFilter",
    width: 220,
    initialHide: true,
    wrapText: true,
  },
  {
    colId: "reciprocity_requirements",
    headerName: "Reciprocity details",
    valueGetter: (p) => ev(p.data, "licensure", "reciprocity", "requirements"),
    // Dotted record path, co-located with the column that owns it: the Sheet
    // filters by path, so nothing has to keep a colId->label table in sync.
    context: { fieldPath: "licensure.reciprocity.requirements" },
    cellRenderer: TextCellRenderer,
    filter: "agTextColumnFilter",
    width: 260,
    initialHide: true,
    wrapText: true,
  },
  {
    colId: "disciplinary_categories",
    headerName: "Disciplinary categories",
    // Array of bucket labels so the multicheck filter can match a state that
    // has, e.g., "False Advertising". The cell renderer shows label + count.
    valueGetter: (p) =>
      (p.data?.disciplinary_categories ?? []).map((c) => c.label),
    valueFormatter: (p) => (Array.isArray(p.value) ? p.value.join(", ") : ""),
    cellRenderer: CategoryChipsCell,
    cellRendererParams: { categoriesKey: "licensure.disciplinary_grounds" },
    filter: MulticheckFilter,
    width: 300,
    wrapText: true,
  },
  {
    colId: "disciplinary_grounds_count",
    context: { section: "Disciplinary grounds" },
    headerName: "Disciplinary grounds (#)",
    valueGetter: (p) => p.data?.disciplinary_grounds_count,
    cellRenderer: TextCellRenderer,
    filter: "agNumberColumnFilter",
    width: 130,
    initialHide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "exam_names",
    // Summarizes a list, so it points at the Sheet SECTION rather than one field.
    context: { section: "Exams" },
    headerName: "Exam names",
    valueGetter: (p) => {
      const exams = (p.data?._full?.licensure?.exams || []) as Array<{ name?: string }>;
      return exams.map((e) => e.name).filter(Boolean).join(", ");
    },
    cellRenderer: TextCellRenderer,
    filter: "agTextColumnFilter",
    width: 240,
    initialHide: true,
    wrapText: true,
  },
  {
    colId: "scope_definition",
    headerName: "Scope of practice (definition)",
    valueGetter: (p) => ev(p.data, "scope", "definition_quote"),
    // Dotted record path, co-located with the column that owns it: the Sheet
    // filters by path, so nothing has to keep a colId->label table in sync.
    context: { fieldPath: "scope.definition_quote" },
    cellRenderer: TextCellRenderer,
    filter: "agTextColumnFilter",
    width: 320,
    wrapText: true,
  },
  {
    colId: "scope_methods",
    context: { fieldPath: "scope.methods_authorized" },
    headerName: "Scope methods authorized",
    valueGetter: (p) => {
      const v = ev(p.data, "scope", "methods_authorized");
      return Array.isArray(v) ? v.join(", ") : v;
    },
    cellRenderer: TextCellRenderer,
    filter: "agTextColumnFilter",
    width: 220,
    initialHide: true,
    wrapText: true,
  },
  {
    colId: "scope_drug_authority",
    headerName: "Scope drug authority",
    valueGetter: (p) => ev(p.data, "scope", "drug_authority"),
    // Dotted record path, co-located with the column that owns it: the Sheet
    // filters by path, so nothing has to keep a colId->label table in sync.
    context: { fieldPath: "scope.drug_authority" },
    cellRenderer: TextCellRenderer,
    filter: "agTextColumnFilter",
    width: 220,
    initialHide: true,
    wrapText: true,
  },
  ];

  // Discovered list fields that the per-item bucketing pass tagged (laser
  // procedures, injections, license tiers, …). For these we chip-render the
  // content categories instead of the raw joined string.
  const bucketedListFields = new Set<string>();
  for (const r of rows) {
    if (r.list_field_categories) {
      for (const k of Object.keys(r.list_field_categories)) bucketedListFields.add(k);
    }
  }

  // ── Dynamic profession-specific columns (varies per profession) ──
  // discoveredFields lists every per-profession discovered field. We pull
  // .value out of each row's profession_specific[field.name] Evidence wrapper.
  // All default-hidden so they don't clutter the initial view.
  for (const f of discoveredFields) {
    const dotted = `profession_specific.${f.name}`;
    // A list field with content buckets → render category chips + multicheck
    // filter, the same treatment disciplinary grounds gets.
    if (bucketedListFields.has(dotted)) {
      cols.push({
        colId: `ps_${f.name}`,
        headerName: humanize(f.name),
        headerTooltip: f.description,
        valueGetter: (p) =>
          (p.data?.list_field_categories?.[dotted] ?? []).map((c) => c.label),
        valueFormatter: (p) => (Array.isArray(p.value) ? p.value.join(", ") : ""),
        cellRenderer: CategoryChipsCell,
        cellRendererParams: { categoriesKey: dotted },
        filter: MulticheckFilter,
        width: 240,
        initialHide: true,
        wrapText: true,
      });
      continue;
    }
    cols.push({
      colId: `ps_${f.name}`,
      headerName: humanize(f.name),
      headerTooltip: f.description,
      valueGetter: (p) => {
        const ps = p.data?._full?.profession_specific;
        if (!ps) return undefined;
        const node = (ps as Record<string, unknown>)[f.name];
        if (isEvidence(node)) {
          const v = node.value;
          return Array.isArray(v) ? v.join(", ") : v;
        }
        return undefined;
      },
      cellRenderer: f.type === "bool" ? YesNoCell : TextCellRenderer,
      // Hint at the right "fallback" filter when cardinality is too high
      // for the multicheck heuristic to pick it.
      filter: f.type === "int" ? "agNumberColumnFilter" : "agTextColumnFilter",
      width: 200,
      initialHide: true,
      wrapText: true,
      cellClassRules: {
        "cell-unverified": (p) => {
          const ps = p.data?._full?.profession_specific;
          if (!ps) return false;
          const node = (ps as Record<string, unknown>)[f.name];
          return isEvidence(node) && node.unverified === true;
        },
      },
    });
  }

  // ── Auto-decide multicheck vs text/number filter per column ──
  // One rule for everything: if the column's distinct-value count across
  // the dataset is <= threshold, give it the multicheckbox filter.
  // Otherwise fall back to its original type-appropriate filter. The
  // hand-coded MulticheckFilter assignments above act as the initial
  // guess; this pass corrects them based on actual data.
  for (const c of cols) {
    if (c.lockVisible) continue; // state column — always text-searchable
    c.filter = inferFilter(c, rows);
  }

  // ── Wire per-cell unverified styling (amber italic border) ──
  // For every column that has a single backing Evidence node, use
  // UNVERIFIED_PATHS to attach cellClassRules. Compound columns that draw
  // from multiple nodes (continuing_ed) use UNVERIFIED_COMPOUND instead.
  // Discovered ps_* columns are handled inline in the loop above.
  for (const c of cols) {
    const id = (c.field as string | undefined) ?? c.colId;
    if (!id) continue;
    const single = UNVERIFIED_PATHS[id];
    const multi = UNVERIFIED_COMPOUND[id];
    const paths = single ? [single] : multi ?? [];
    if (paths.length === 0) continue;
    c.cellClassRules = {
      ...c.cellClassRules,
      "cell-unverified": (p) => paths.some((path) => evUnverified(p.data, ...path)),
    };
  }

  // ── Ensure each column is at least wide enough for its header label ──
  // Single-line headers, no truncation. The starting `width` is the
  // ergonomic content width I picked; `minWidth` is computed from the
  // header label length + icon overhead so the column expands when its
  // header would otherwise be cut off. User-driven resize still works.
  const HEADER_CHAR_PX = 8; // rough char width for the header font
  const HEADER_ICON_OVERHEAD_PX = 55; // sort icon + filter icon + padding
  for (const c of cols) {
    const label = (c.headerName as string) || "";
    const needed = label.length * HEADER_CHAR_PX + HEADER_ICON_OVERHEAD_PX;
    c.minWidth = Math.max(c.minWidth ?? 0, needed);
    if ((c.width ?? 0) < needed) c.width = needed;
  }

  return cols;
}

// ---------- AG Grid theme: Quartz, tuned to read like the rest of the site
const gridTheme = themeQuartz.withParams({
  // Match the rest of the app (Geist) rather than a system font.
  fontFamily: "var(--font-geist-sans), ui-sans-serif, system-ui, sans-serif",
  fontSize: 14,
  headerFontWeight: 600,
  headerBackgroundColor: token("grid-header"),
  oddRowBackgroundColor: token("grid-row"),
  rowHoverColor: token("grid-hover"),
  borderColor: token("grid-border"),
  wrapperBorderRadius: 8,
});

// Column id list + label map built dynamically per profession; see
// ProfileView for the live values (depends on payload.discovered_fields).

function colId(c: ColDef<Row>): string {
  return (c.field as string) || (c.colId as string);
}

// ============================================================================

export function ProfileView({
  payload,
  // When ProfileView is rendered as the body of a parent route that already
  // provides its own page chrome (heading, breadcrumb), pass embedded=true so
  // ProfileView skips the duplicate header + back-link + outer <main>.
  embedded = false,
  // When the parent provides view-switching as outer tabs, pass `view` to
  // force the rendered sub-view and we'll suppress the internal table/map/
  // hierarchy toggle to avoid two competing tab rows.
  view: viewOverride,
}: { payload: ProfilePayload; embedded?: boolean; view?: "table" | "map" }) {
  const { rows, evidence_summary, discovered_fields } = payload;
  const display = payload.display || payload.profession;
  const covered = rows.filter((r) => !r.coverage_gap).length;
  const gaps = rows.length - covered;
  const unverifiedCount = evidence_summary?.unverified || 0;

  const gridRef = useRef<AgGridReact<Row>>(null);
  const [api, setApi] = useState<GridApi<Row> | null>(null);
  // The state-detail Sheet is owned by the PAGE (app/professions/[id]/page.tsx) so every
  // tab can open it, not just this one. We only ask it to open.
  const openStateDetail = useOpenStateDetail();
  // Force re-render of the chip bar whenever AG Grid's filter model changes.
  // We track a tick rather than mirror the filter model into React state,
  // since the source of truth is the grid itself.
  const [filterTick, setFilterTick] = useState(0);

  // Build per-profession column defs from the static universal set + the
  // dynamic discovered fields, with each column's filter type auto-decided
  // from observed cardinality. Memoized so AG Grid sees stable refs.
  const columnDefs = useMemo(
    () => buildColumnDefs(discovered_fields, rows, payload.map_prep?.text_buckets ?? {}),
    [discovered_fields, rows]
  );
  const toggleableColumns = useMemo(
    () => columnDefs.filter((c) => !c.lockVisible),
    [columnDefs]
  );
  const allToggleableIds = useMemo(
    () => toggleableColumns.map(colId),
    [toggleableColumns]
  );
  const columnLabel = useMemo(() => {
    const m: Record<string, string> = {};
    for (const c of columnDefs)
      m[colId(c)] = (c.headerName as string) || colId(c);
    return m;
  }, [columnDefs]);

  // visibleColumns tracks ONLY toggleable columns (state is always shown
  // via lockVisible). Default: columns whose initialHide isn't true.
  const [visibleColumns, setVisibleColumns] = useState<Set<string>>(
    () =>
      new Set(
        columnDefs
          .filter((c) => !c.lockVisible && !(c as { initialHide?: boolean }).initialHide)
          .map(colId)
      )
  );

  // Which #19 view preset is active (null = custom / default). Cleared the
  // moment the user hand-toggles a column, since the set no longer matches.
  const [activePreset, setActivePreset] = useState<string | null>(null);

  // Profession slug for browse URLs. payload.profession is canonical
  // (e.g. "podiatry"); ensure it survives even if the URL was navigated
  // to with a casing variation.
  const profSlug = payload.profession;
  // URL-driven view + map field (unchanged from prior version)
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();
  const viewParam = params.get("view");
  const view: "table" | "map" =
    viewOverride ??
    (viewParam === "map" && payload.map_prep ? "map" : "table");
  const urlField = params.get("f");
  const updateParams = useCallback(
    (patch: Record<string, string | null>) => {
      const next = new URLSearchParams(params.toString());
      for (const [k, v] of Object.entries(patch)) {
        if (v === null || v === "") next.delete(k);
        else next.set(k, v);
      }
      router.replace(`${pathname}?${next.toString()}`, { scroll: false });
    },
    [params, pathname, router]
  );
  const setView = (v: "table" | "map") =>
    updateParams({ view: v === "table" ? null : v });
  const setMapField = (f: string | null) => updateParams({ f });

  const onFilterChanged = (_e: FilterChangedEvent) => setFilterTick((t) => t + 1);

  // Active query for the "Statute text" filter, pulled from AG Grid's filter
  // model so it stays in sync with the chip bar. Passed down to the Sheet
  // so it can highlight matches against the same string the table was
  // filtered by — one query, two consumers.
  const statuteTextQuery = useMemo<string>(() => {
    void filterTick; // recompute when AG Grid's filter model changes
    if (!api) return "";
    const fm = api.getFilterModel() || {};
    const m = fm["statute_text"] as { filter?: unknown } | undefined;
    return typeof m?.filter === "string" ? m.filter : "";
  }, [api, filterTick]);

  // Cell click (not row click) so we know WHICH column was clicked (#34) and
  // can scroll the Sheet straight to that field. State column is excluded —
  // it's the row identifier, not a data field worth focusing.
  const handleCellClick = useCallback(
    (event: {
      data?: Row;
      column?: {
        getColId: () => string;
        getColDef?: () => { context?: { fieldPath?: string; section?: string } };
      };
      event?: Event | null;
    }) => {
      if (!event.data || !openStateDetail) return;
      const col = event.column?.getColId();
      // The column knows its own record path (co-located on the def), so the click
      // carries it and nothing downstream has to translate colId -> label.
      const colDefCtx = event.column?.getColDef?.()?.context;
      const fieldPath = colDefCtx?.fieldPath ?? null;
      const section = colDefCtx?.section ?? null;
      // If the click landed on a specific category chip ("Fraud 3"), carry that
      // category through so the Sheet lands on those items. Without it, clicking any
      // chip in the cell looked identical — you couldn't tell it had taken you to the
      // thing you actually clicked.
      const target = event.event?.target;
      const chip =
        target instanceof Element ? target.closest("[data-category]") : null;
      openStateDetail(event.data.state, {
        colId: col && col !== "state" ? col : null,
        category: chip?.getAttribute("data-category") ?? null,
        fieldPath,
        section,
        searchQuery: statuteTextQuery,
      });
    },
    [openStateDetail, statuteTextQuery]
  );

  // ── Chips: derive from grid's filterModel ─────
  type Chip = { key: string; label: string; value: string; onRemove: () => void };
  const activeChips: Chip[] = useMemo(() => {
    void filterTick; // dependency: re-run when the grid filter model changes
    const chips: Chip[] = [];
    if (api) {
      const fm = api.getFilterModel() || {};
      for (const [columnId, model] of Object.entries(fm)) {
        const m = model as { filter?: unknown; type?: string; values?: string[] };
        const label = columnLabel[columnId] || columnId;
        let displayValue: string;
        if (Array.isArray(m.values)) {
          // MulticheckFilter model
          displayValue =
            m.values.length <= 3
              ? m.values.map((v) => humanize(v)).join(", ")
              : `${m.values.length} values`;
        } else if (m.type === "equals" && typeof m.filter === "string") {
          displayValue = humanize(m.filter);
        } else if (typeof m.filter === "string") {
          displayValue = `contains "${m.filter}"`;
        } else if (typeof m.filter === "number") {
          displayValue = `${m.type ?? ""} ${m.filter}`.trim();
        } else {
          displayValue = JSON.stringify(m);
        }
        chips.push({
          key: `col-${columnId}`,
          label,
          value: displayValue,
          onRemove: () => {
            const next = { ...api.getFilterModel() };
            delete next[columnId];
            api.setFilterModel(next);
          },
        });
      }
    }
    return chips;
  }, [api, filterTick, columnLabel]);

  const clearAllFilters = () => {
    api?.setFilterModel(null);
  };

  // ── Column visibility: drive AG Grid via applyColumnState (v35 canonical) ──
  // `setColumnsVisible([id], v)` silently no-ops for columns whose colId
  // wasn't auto-promoted from `field` (the discovered ps_* columns declare
  // an explicit colId only). applyColumnState is the stable path.
  //
  // After making a column visible, scroll it into view: the table's total
  // width is ~3300px on common viewports (~1050px), so a new column added
  // at the far right is off-screen and the user can mistake "toggled on"
  // for "didn't work" (issue #11 / Atharv's "doesn't show up when toggled").
  const toggleColumnVisible = (id: string, visible: boolean) => {
    setActivePreset(null); // hand-edit → no longer matches a preset
    setVisibleColumns((prev) => {
      const next = new Set(prev);
      if (visible) next.add(id);
      else next.delete(id);
      return next;
    });
    if (!api) return;
    api.applyColumnState({ state: [{ colId: id, hide: !visible }] });
    if (visible) {
      // Defer one frame so AG Grid finishes the column-layout pass before we
      // ask it to scroll — without the delay, ensureColumnVisible can no-op
      // because the column's position isn't computed yet.
      requestAnimationFrame(() => api.ensureColumnVisible(id, "middle"));
    }
  };

  // ── View presets (#19): one-click column sets so users can focus on a
  // dimension instead of the full ~70-column table. "Scope" pulls in the new
  // per-item tag columns (laser, injections, …); "Discipline" the disciplinary
  // tags; "Priority" the five headline fields. "All columns" restores the
  // default set. Each replaces the visible set entirely (a focused view).
  const scopeTagColIds = useMemo(() => {
    const ids = new Set<string>();
    for (const r of rows) {
      if (!r.list_field_categories) continue;
      for (const k of Object.keys(r.list_field_categories))
        ids.add("ps_" + k.replace("profession_specific.", ""));
    }
    return [...ids];
  }, [rows]);

  const viewPresets = useMemo(
    () => [
      {
        key: "full",
        label: "Basic",
        ids: columnDefs
          .filter((c) => !c.lockVisible && !(c as { initialHide?: boolean }).initialHide)
          .map(colId),
      },
      {
        key: "priority",
        label: "Priority",
        ids: [
          "regulatory_model",
          "education_degree",
          "post_degree_duration",
          "issuing_authority",
          "scope_definition",
          "disciplinary_categories",
        ],
      },
      {
        // Mirrors the field dictionary's "Licensure" bucket (Atharv #75): the
        // credential model, authority, entry requirements, CE, renewal, reciprocity.
        key: "license",
        label: "License",
        ids: [
          "regulatory_model",
          "license_required",
          "issuing_authority",
          "education_degree",
          "exams_count",
          "post_degree_duration",
          "age_minimum",
          "moral_character_required",
          "continuing_ed",
          "renewal_years",
          "reciprocity_available",
        ],
      },
      {
        key: "scope",
        label: "Scope of practice",
        ids: [
          "scope_definition",
          "scope_methods",
          "scope_drug_authority",
          ...scopeTagColIds,
        ],
      },
      {
        key: "discipline",
        label: "Disciplinary grounds",
        ids: ["disciplinary_categories", "disciplinary_grounds_count"],
      },
      {
        key: "all",
        label: "All",
        ids: allToggleableIds,
      },
    ],
    [scopeTagColIds, columnDefs, allToggleableIds]
  );

  const applyPreset = (key: string) => {
    const preset = viewPresets.find((p) => p.key === key);
    if (!preset) return;
    const show = new Set(preset.ids.filter((id) => allToggleableIds.includes(id)));
    setVisibleColumns(show);
    setActivePreset(key);
    if (api) {
      api.applyColumnState({
        state: allToggleableIds.map((id) => ({ colId: id, hide: !show.has(id) })),
      });
    }
  };

  // Sync visibility set to grid once the grid is ready.
  useEffect(() => {
    if (!api) return;
    const state = allToggleableIds.map((id) => ({
      colId: id,
      hide: !visibleColumns.has(id),
    }));
    api.applyColumnState({ state });
    // Run only when api or the toggleable id list changes; visibility
    // changes are pushed synchronously in toggleColumnVisible.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [api, allToggleableIds]);

  const Wrapper = embedded ? "div" : "main";
  return (
    <Wrapper className={embedded ? "" : "mx-auto max-w-7xl px-6 py-10"}>
      {!embedded && (
        <>
          <BackLink href="/">all professions</BackLink>

          <Eyebrow className="mt-6">Profession profile</Eyebrow>
          <h1 className="text-3xl font-semibold tracking-tight mt-1 mb-2">
            {display}
          </h1>
          <p className="text-muted-foreground max-w-3xl mb-6">
            Side-by-side licensure and scope of practice across 50 states,
            auto-extracted from state statutes. Every claim is backed by a
            verbatim quote validated against the source — click any row to see
            the quotes and citations. Click any column header for per-column
            filtering.
          </p>
        </>
      )}

      <div className="flex flex-wrap gap-x-8 gap-y-2 rounded-lg border bg-muted/30 px-4 py-3 mb-8 text-sm">
        <Stat label="states with extracted records" value={covered} />
        <Stat label="coverage gaps" value={gaps} />
        <Stat label="auto-discovered profession-specific fields" value={discovered_fields.length} />
        {/* Only surface the unverified-quote count when there's something to see. */}
        {unverifiedCount > 0 && (
          <Stat label="unverified quotes" value={unverifiedCount} />
        )}
      </div>

      {/* Internal view toggle. Suppressed when the parent supplies the
          `view` prop (i.e. /professions/[id] is rendering outer tabs that
          do this job — having two rows of tab-like buttons looked janky). */}
      {!viewOverride && (
        <div className="mb-4 inline-flex rounded-md border bg-muted/30 p-1 text-xs font-mono">
          <button
            onClick={() => setView("table")}
            className={
              "px-3 py-1 rounded " +
              (view === "table"
                ? "bg-background shadow-sm text-foreground"
                : "text-muted-foreground hover:text-foreground")
            }
          >
            table
          </button>
          <button
            onClick={() => setView("map")}
            className={
              "px-3 py-1 rounded " +
              (view === "map"
                ? "bg-background shadow-sm text-foreground"
                : "text-muted-foreground hover:text-foreground")
            }
            disabled={!payload.map_prep}
            title={
              payload.map_prep ? "" : "no map data yet — run map_prep for this profession"
            }
          >
            map
          </button>
        </div>
      )}

      {view === "map" && payload.map_prep && (
        <MapView
          mapPrep={payload.map_prep}
          fieldName={urlField}
          onFieldChange={setMapField}
        />
      )}

      {view === "table" && (
        <>
          <div className="flex flex-wrap gap-3 items-center mb-4">
            {/* #19 view presets: focus the table on one dimension. */}
            <div className="inline-flex items-center gap-1 rounded-md border bg-muted/40 p-0.5 text-xs">
              <span className="px-2 font-mono uppercase tracking-wider text-muted-foreground">
                view
              </span>
              {viewPresets.map((p) => (
                <button
                  key={p.key}
                  onClick={() => applyPreset(p.key)}
                  className={
                    "px-2.5 py-1 rounded " +
                    (activePreset === p.key
                      ? "bg-background shadow-sm text-foreground"
                      : "text-muted-foreground hover:text-foreground")
                  }
                >
                  {p.label}
                </button>
              ))}
            </div>

            <span className="text-xs font-mono text-muted-foreground">
              Filter per column by clicking its header (
              <span className="text-foreground">≡</span> icon). Or pick a view
              above; toggle individual columns at right.
            </span>

            {/* CE units atlas (Atharv #75): the "24 / 2" format is cryptic, so
                explain it inline whenever the Continuing Ed column is showing. */}
            {visibleColumns.has("continuing_ed") && (
              <span className="text-xs inline-flex items-center gap-1.5 rounded border bg-muted/30 px-2 py-1 text-muted-foreground">
                <span className="font-medium text-foreground">Continuing&nbsp;Ed</span>
                reads <span className="font-mono">hours&nbsp;/&nbsp;years</span> — e.g.{" "}
                <span className="font-mono text-foreground">24&nbsp;/&nbsp;2</span> = 24 CE
                hours every 2-year renewal.
              </span>
            )}

            <ColumnVisibilityPopover
              columns={toggleableColumns.map((c) => {
                const id = colId(c);
                // ps_<name> columns are discovered fields — pull the
                // category from the discovered_fields list. Others remain
                // in the universal "Cross-state fields" bucket.
                const psName = id.startsWith("ps_") ? id.slice(3) : null;
                const category = psName
                  ? discovered_fields.find((f) => f.name === psName)?.category
                  : undefined;
                return {
                  id,
                  label: (c.headerName as string) || id,
                  category,
                };
              })}
              visible={visibleColumns}
              onToggle={toggleColumnVisible}
            />

            <Button
              variant="outline"
              size="sm"
              className="font-mono text-xs"
              disabled={!api}
              onClick={() => {
                if (!api) return;
                // allColumns:true exports every column in the columnDefs
                // regardless of current visibility — what users want from
                // "Download CSV" is the full dataset, not just the columns
                // they happen to have toggled on. Filtered rows still
                // respected (so an active filter narrows the export).
                const textBuckets = payload.map_prep?.text_buckets ?? {};
                api.exportDataAsCsv({
                  fileName: `${profSlug}.csv`,
                  allColumns: true,
                  processCellCallback: (p) =>
                    exportCellValue(
                      p.value,
                      p.column?.getColId?.(),
                      (p.node?.data as Row | undefined)?.state,
                      textBuckets,
                    ),
                });
              }}
            >
              Download CSV ↓
            </Button>

            <Button
              variant="outline"
              size="sm"
              className="font-mono text-xs"
              disabled={!api}
              onClick={async () => {
                if (!api) return;
                // Workbook export (#28.3): tab 1 is the same flat table as the
                // CSV; then one tab per state with that state's statute sections.
                // SheetJS is ~430 KB minified, so load it on demand rather than
                // shipping it in the route bundle for everyone.
                const XLSX = await import("xlsx");
                const textBuckets = payload.map_prep?.text_buckets ?? {};
                const wb = XLSX.utils.book_new();

                // Sheet 1 — reuse AG Grid's CSV writer (same filter + the shared
                // cell formatting) and parse it back into a worksheet, so the
                // flat sheet never drifts from "Download CSV".
                const csv =
                  api.getDataAsCsv({
                    allColumns: true,
                    processCellCallback: (p) =>
                      exportCellValue(
                        p.value,
                        p.column?.getColId?.(),
                        (p.node?.data as Row | undefined)?.state,
                        textBuckets,
                      ),
                  }) ?? "";
                const flat = XLSX.read(csv, { type: "string" });
                XLSX.utils.book_append_sheet(
                  wb,
                  flat.Sheets[flat.SheetNames[0]],
                  "All states",
                );

                // One tab per state, filtered + sorted to match the table.
                // Newlines are preserved here (xlsx cells are multi-line), so
                // the per-state statute text stays readable.
                const used = new Set<string>();
                api.forEachNodeAfterFilterAndSort((node) => {
                  const r = node.data as Row | undefined;
                  if (!r) return;
                  // Sheet names: ≤31 chars, unique. State codes are 2 chars, so
                  // the dedup guard is just belt-and-suspenders.
                  let name = (r.state || "??").slice(0, 31);
                  while (used.has(name))
                    name = `${name.slice(0, 28)}_${used.size % 10}`;
                  used.add(name);

                  const aoa: string[][] = [
                    ["Citation", "Section", "Statute text", "Source URL"],
                  ];
                  const secs = Array.isArray(r.sections) ? r.sections : [];
                  for (const s of secs)
                    aoa.push([
                      s.citation || "",
                      s.label || "",
                      s.text || "",
                      s.url || "",
                    ]);
                  if (secs.length === 0)
                    aoa.push([
                      r.coverage_gap
                        ? r.coverage_gap_label || "No data found"
                        : "No statute sections",
                      "",
                      "",
                      "",
                    ]);
                  XLSX.utils.book_append_sheet(
                    wb,
                    XLSX.utils.aoa_to_sheet(aoa),
                    name,
                  );
                });

                // Excel caps a single cell at 32767 chars; a long concatenated
                // statute (or one giant section) blows past that and the writer
                // throws. Clamp every string cell so the export never fails —
                // the per-state tabs + Source URL still give the full text.
                const CELL_MAX = 32767;
                for (const sn of wb.SheetNames) {
                  const ws = wb.Sheets[sn];
                  for (const addr of Object.keys(ws)) {
                    if (addr[0] === "!") continue;
                    const cell = ws[addr] as { v?: unknown; w?: string };
                    if (typeof cell.v === "string" && cell.v.length > CELL_MAX) {
                      cell.v = cell.v.slice(0, CELL_MAX - 14) + " …[truncated]";
                      delete cell.w;
                    }
                  }
                }

                XLSX.writeFile(wb, `${profSlug}.xlsx`);
              }}
            >
              Download workbook ↓
            </Button>
          </div>

          {/* Chip bar — every active filter shows as a removable chip.
              Sticky to the viewport top so that while scrolling a long
              table the user always sees what's filtering the rows below.
              The bg fade + border-bottom prevent table cells bleeding
              through when scrolled under. */}
          {activeChips.length > 0 && (
            <div className="sticky top-0 z-10 -mx-1 mb-3 bg-background/95 supports-[backdrop-filter]:bg-background/80 backdrop-blur border-b border-border/60 px-1 py-2 flex flex-wrap gap-2 items-center">
              <span className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                Active filters:
              </span>
              {activeChips.map((c) => (
                <FilterChip
                  key={c.key}
                  label={c.label}
                  value={c.value}
                  onRemove={c.onRemove}
                />
              ))}
              <button
                type="button"
                onClick={clearAllFilters}
                className="text-xs font-mono text-muted-foreground hover:text-foreground underline"
              >
                clear all
              </button>
            </div>
          )}

          <div style={{ width: "100%" }}>
            <AgGridReact<Row>
              ref={gridRef}
              theme={gridTheme}
              rowData={rows}
              columnDefs={columnDefs}
              rowHeight={73}
              enableBrowserTooltips={true}
              defaultColDef={{
                sortable: true,
                resizable: true,
                filter: true,
                // Header on a single line. If a label is too long for its
                // column width, AG Grid truncates with ellipsis (cleaner
                // than mid-word wrap like "Reciprocit/y"). Per-column
                // widths below are sized so this doesn't happen.
                wrapHeaderText: false,
                autoHeaderHeight: false,
                // Show full cell value on hover as a native browser tooltip,
                // but only for content that is likely to be clipped (long
                // strings). Falsy/zero/short values are already fully visible
                // so a tooltip is redundant — and for things like the
                // Unverified column the raw value (0) would contradict the
                // blank display.
                tooltipValueGetter: (p) => {
                  if (p.value == null || p.value === "" || p.value === 0 || p.value === false) return undefined;
                  const s = String(p.value);
                  return s.length > 50 ? s : undefined;
                },
                // Tighten wrapped-text line spacing — AG Grid's default
                // leaves a paragraph-break-sized gap between wrapped lines.
                cellStyle: {
                  lineHeight: "1.35",
                  paddingTop: "8px",
                  paddingBottom: "8px",
                  display: "flex",
                  alignItems: "flex-start",
                  overflow: "hidden",
                },
              }}
              domLayout="autoHeight"
              onGridReady={(e) => setApi(e.api)}
              onCellClicked={handleCellClick}
              onFilterChanged={onFilterChanged}
              rowClassRules={{
                "ag-row-coverage-gap": (params) =>
                  Boolean((params.data as Row | undefined)?.coverage_gap),
              }}
              suppressCellFocus
              animateRows={true}
            />
          </div>
        </>
      )}

    </Wrapper>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <span className="font-semibold text-foreground">{value}</span>{" "}
      <span className="text-muted-foreground">{label}</span>
    </div>
  );
}

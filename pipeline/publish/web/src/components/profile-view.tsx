"use client";

import {
  forwardRef,
  useCallback,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
} from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { AgGridReact } from "ag-grid-react";
import {
  AllCommunityModule,
  ModuleRegistry,
  themeQuartz,
  type ColDef,
  type FilterChangedEvent,
  type GridApi,
  type IDoesFilterPassParams,
  type IFilter,
  type IFilterParams,
  type ICellRendererParams,
} from "ag-grid-community";
import type { DiscoveredField, ProfilePayload, Row } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { humanize } from "@/lib/format";
import { StateDetailDialog } from "./state-detail-dialog";
import { MapView } from "./map-view";

// AG Grid v33+ requires modules to be registered before any grid instance
// is constructed. AllCommunityModule pulls in every community module —
// fine for our bundle since we're not optimizing for size on an internal tool.
ModuleRegistry.registerModules([AllCommunityModule]);

// ---------- Cell renderer components ----------

const PILL_YES = "bg-emerald-100 text-emerald-900 hover:bg-emerald-100";
const PILL_NO = "bg-rose-100 text-rose-900 hover:bg-rose-100";

function YesNoCell({ value }: ICellRendererParams<Row, boolean | null>) {
  if (value === true)
    return <Badge variant="secondary" className={PILL_YES}>yes</Badge>;
  if (value === false)
    return <Badge variant="secondary" className={PILL_NO}>no</Badge>;
  return <span className="text-muted-foreground">—</span>;
}

function TextCellRenderer({ value }: ICellRendererParams<Row, string | number | null>) {
  if (value === null || value === undefined || value === "")
    return <span className="text-muted-foreground">—</span>;
  return <span>{value}</span>;
}

function VerifyCell({ data }: ICellRendererParams<Row>) {
  if (!data) return null;
  if (data.coverage_gap) return <span className="text-muted-foreground">—</span>;
  const v = data.evidence_verified || 0;
  const u = data.evidence_unverified || 0;
  if (v + u === 0) return <span className="text-muted-foreground">—</span>;
  return (
    <span
      className={
        "font-mono text-xs " +
        (u > 0 ? "text-amber-700" : "text-emerald-700")
      }
      title="Verbatim quotes regex-checked against the cleaned source"
    >
      {u > 0 ? "⚠ " : "✓ "}
      {v}/{v + u}
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

function RegulatoryModelCell({ data, value }: ICellRendererParams<Row, string | null>) {
  if (data?.coverage_gap) {
    return (
      <span
        className="text-xs italic text-muted-foreground"
        title={data.coverage_gap_reason || ""}
      >
        {data.coverage_gap_label || "—"}
      </span>
    );
  }
  if (!value) return <span className="text-muted-foreground">—</span>;
  const colors: Record<string, string> = {
    license: "bg-sky-100 text-sky-900",
    mandatory_certification: "bg-emerald-100 text-emerald-900",
    registration: "bg-amber-100 text-amber-900",
    exemption: "bg-zinc-100 text-zinc-700",
    voluntary_certification: "bg-violet-100 text-violet-900",
    market_forces: "bg-rose-100 text-rose-900",
  };
  const cls = colors[value] || "bg-muted text-muted-foreground";
  return (
    <Badge variant="secondary" className={cls + " hover:" + cls}>
      {humanize(value)}
    </Badge>
  );
}

function CredentialTypeCell({ data }: ICellRendererParams<Row>) {
  if (!data || data.coverage_gap) return <span className="text-muted-foreground">—</span>;
  const ct = data.credential_type;
  const mandatory = data.is_mandatory;
  if (!ct && mandatory === null) return <span className="text-muted-foreground">—</span>;
  const colors: Record<string, string> = {
    license: "bg-sky-100 text-sky-900",
    certification: "bg-emerald-100 text-emerald-900",
    registration: "bg-amber-100 text-amber-900",
    exemption: "bg-zinc-100 text-zinc-700",
    none: "bg-rose-100 text-rose-900",
  };
  const cls = ct ? colors[ct] || "bg-muted text-muted-foreground" : "";
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
  columns: Array<{ id: string; label: string }>;
  visible: Set<string>;
  onToggle: (id: string, v: boolean) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

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
          role="menu"
          className="absolute right-0 top-full mt-1 w-56 max-h-[60vh] overflow-y-auto rounded-md border bg-popover text-popover-foreground shadow-md z-50 p-1"
        >
          <div className="px-2 py-1.5 text-xs font-mono uppercase tracking-widest text-muted-foreground">
            Show / hide columns
          </div>
          <div className="my-1 h-px bg-border" />
          {columns.map((c) => (
            <label
              key={c.id}
              className="flex items-center gap-2 px-2 py-1.5 rounded text-sm hover:bg-accent hover:text-accent-foreground cursor-pointer"
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

type MulticheckModel = { values: string[] } | null;

const MulticheckFilter = forwardRef<IFilter, IFilterParams<Row>>(
  function MulticheckFilter(props, ref) {
    const [selected, setSelected] = useState<Set<string>>(new Set());
    const [query, setQuery] = useState("");

    // Unique non-null values across all loaded rows for this column.
    const uniqueValues = useMemo(() => {
      const set = new Set<string>();
      props.api.forEachNode((node) => {
        if (!node.data) return;
        const v = props.getValue(node);
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
    }, [props.api, props.getValue]);

    const filteredValues = useMemo(
      () =>
        query
          ? uniqueValues.filter((v) =>
              v.toLowerCase().includes(query.toLowerCase())
            )
          : uniqueValues,
      [uniqueValues, query]
    );

    useImperativeHandle(ref, () => ({
      isFilterActive() {
        return selected.size > 0;
      },
      doesFilterPass(params: IDoesFilterPassParams<Row>) {
        const v = props.getValue(params.node);
        if (Array.isArray(v))
          return v.some((x) => selected.has(String(x)));
        if (v == null) return false;
        return selected.has(String(v));
      },
      getModel(): MulticheckModel {
        return selected.size > 0 ? { values: Array.from(selected) } : null;
      },
      setModel(model: MulticheckModel) {
        setSelected(new Set(model?.values || []));
      },
    }));

    const toggle = (v: string) => {
      const next = new Set(selected);
      if (next.has(v)) next.delete(v);
      else next.add(v);
      setSelected(next);
      // AG Grid expects us to push the filter change to the grid manually
      // after state updates. filterChangedCallback re-runs doesFilterPass
      // across rows.
      setTimeout(() => props.filterChangedCallback(), 0);
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
            onClick={() => {
              setSelected(new Set(uniqueValues));
              setTimeout(() => props.filterChangedCallback(), 0);
            }}
            className="hover:text-foreground"
          >
            all
          </button>
          <span>{selected.size} selected</span>
          <button
            type="button"
            onClick={() => {
              setSelected(new Set());
              setTimeout(() => props.filterChangedCallback(), 0);
            }}
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
);


// ---------- Helpers for drilling into the structured record ----------

type EvidenceLike = { value: unknown; quote?: unknown; citation?: unknown };

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


// ---------- Column definitions ----------
// AG Grid's per-column filter gives us the popover-from-the-header pattern
// users are used to. Categorical columns get MulticheckFilter (Community
// workalike for the Enterprise Set Filter); text/number columns use the
// built-in text/number filters.
//
// `hide: true` means the column is registered but not shown by default —
// users opt in via the Columns ▾ dropdown. This lets us expose every
// modal field as a column without overwhelming the default view.

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

function buildColumnDefs(
  discoveredFields: DiscoveredField[],
  rows: Row[]
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
    autoHeight: true,
    // Hidden by default — for the common "license × mandatory" case it
    // duplicates the Regulation (UORF) column. Users opt in via the
    // Columns ▾ dropdown when they want the orthogonal decomposition.
    hide: true,
  },
  {
    field: "issuing_authority",
    headerName: "Licensing Authority",
    width: 230,
    cellRenderer: TextCellRenderer,
    filter: "agTextColumnFilter",
    wrapText: true,
    autoHeight: true,
    cellClass: "leading-snug",
  },
  {
    field: "education_degree",
    headerName: "Education (Min. Degree)",
    width: 260,
    cellRenderer: TextCellRenderer,
    filter: "agTextColumnFilter",
    wrapText: true,
    autoHeight: true,
    cellClass: "leading-snug",
  },
  {
    field: "post_degree_duration",
    headerName: "Professional Experience",
    width: 180,
    cellRenderer: TextCellRenderer,
    filter: "agTextColumnFilter",
    wrapText: true,
    autoHeight: true,
    cellClass: "leading-snug",
  },
  {
    field: "exams_count",
    headerName: "Exams",
    width: 95,
    cellRenderer: TextCellRenderer,
    filter: "agNumberColumnFilter",
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    field: "renewal_years",
    headerName: "Renewal (yrs)",
    width: 130,
    cellRenderer: TextCellRenderer,
    filter: MulticheckFilter,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "continuing_ed",
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
  },
  {
    field: "reciprocity_available",
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
    autoHeight: true,
  },
  {
    colId: "evidence",
    headerName: "Evidence",
    width: 100,
    valueGetter: (p) =>
      p.data
        ? `${p.data.evidence_verified}/${p.data.evidence_verified + p.data.evidence_unverified}`
        : null,
    cellRenderer: VerifyCell,
    filter: "agTextColumnFilter",
    cellClass: "text-center",
    headerClass: "text-center",
  },

  // ── Additional universal columns (default-hidden; opt in via Columns ▾)
  {
    colId: "license_required",
    headerName: "License required?",
    valueGetter: (p) => ev(p.data, "licensure", "license_required"),
    cellRenderer: YesNoCell,
    filter: MulticheckFilter,
    width: 130,
    hide: true,
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
    hide: true,
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
    hide: true,
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
    hide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "age_minimum",
    headerName: "Age minimum",
    valueGetter: (p) => ev(p.data, "licensure", "age_minimum"),
    cellRenderer: TextCellRenderer,
    filter: "agNumberColumnFilter",
    width: 130,
    hide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "moral_character_required",
    headerName: "Moral character required?",
    valueGetter: (p) => ev(p.data, "licensure", "moral_character_required"),
    cellRenderer: YesNoCell,
    filter: MulticheckFilter,
    width: 160,
    hide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "education_accrediting_body",
    headerName: "Accrediting body",
    valueGetter: (p) => ev(p.data, "licensure", "education", "accrediting_body"),
    cellRenderer: TextCellRenderer,
    filter: MulticheckFilter,
    width: 200,
    hide: true,
    wrapText: true,
    autoHeight: true,
  },
  {
    colId: "post_degree_required",
    headerName: "Post-degree required?",
    valueGetter: (p) => ev(p.data, "licensure", "post_degree_experience", "required"),
    cellRenderer: YesNoCell,
    filter: MulticheckFilter,
    width: 160,
    hide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "post_degree_kind",
    headerName: "Post-degree kind",
    valueGetter: (p) => ev(p.data, "licensure", "post_degree_experience", "kind"),
    cellRenderer: TextCellRenderer,
    filter: MulticheckFilter,
    width: 180,
    hide: true,
    wrapText: true,
    autoHeight: true,
  },
  {
    colId: "ce_required",
    headerName: "CE required?",
    valueGetter: (p) => ev(p.data, "licensure", "continuing_education", "required"),
    cellRenderer: YesNoCell,
    filter: MulticheckFilter,
    width: 130,
    hide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "ce_hours_per_period",
    headerName: "CE hours/period",
    valueGetter: (p) => ev(p.data, "licensure", "continuing_education", "hours_per_period"),
    cellRenderer: TextCellRenderer,
    filter: "agNumberColumnFilter",
    width: 130,
    hide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "ce_period_years",
    headerName: "CE period (yrs)",
    valueGetter: (p) => ev(p.data, "licensure", "continuing_education", "period_years"),
    cellRenderer: TextCellRenderer,
    filter: "agNumberColumnFilter",
    width: 130,
    hide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "ce_topical_requirements",
    headerName: "CE topical requirements",
    valueGetter: (p) => {
      const v = ev(p.data, "licensure", "continuing_education", "topical_requirements");
      return Array.isArray(v) ? v.join(", ") : v;
    },
    cellRenderer: TextCellRenderer,
    filter: "agTextColumnFilter",
    width: 220,
    hide: true,
    wrapText: true,
    autoHeight: true,
  },
  {
    colId: "reciprocity_requirements",
    headerName: "Reciprocity details",
    valueGetter: (p) => ev(p.data, "licensure", "reciprocity", "requirements"),
    cellRenderer: TextCellRenderer,
    filter: "agTextColumnFilter",
    width: 260,
    hide: true,
    wrapText: true,
    autoHeight: true,
  },
  {
    colId: "disciplinary_grounds_count",
    headerName: "Disciplinary grounds (#)",
    valueGetter: (p) => p.data?.disciplinary_grounds_count,
    cellRenderer: TextCellRenderer,
    filter: "agNumberColumnFilter",
    width: 130,
    hide: true,
    cellClass: "text-center",
    headerClass: "text-center",
  },
  {
    colId: "exam_names",
    headerName: "Exam names",
    valueGetter: (p) => {
      const exams = (p.data?._full?.licensure?.exams || []) as Array<{ name?: string }>;
      return exams.map((e) => e.name).filter(Boolean).join(", ");
    },
    cellRenderer: TextCellRenderer,
    filter: "agTextColumnFilter",
    width: 240,
    hide: true,
    wrapText: true,
    autoHeight: true,
  },
  {
    colId: "scope_definition",
    headerName: "Scope of practice (definition)",
    valueGetter: (p) => ev(p.data, "scope", "definition_quote"),
    cellRenderer: TextCellRenderer,
    filter: "agTextColumnFilter",
    width: 320,
    hide: true,
    wrapText: true,
    autoHeight: true,
  },
  {
    colId: "scope_methods",
    headerName: "Scope methods authorized",
    valueGetter: (p) => {
      const v = ev(p.data, "scope", "methods_authorized");
      return Array.isArray(v) ? v.join(", ") : v;
    },
    cellRenderer: TextCellRenderer,
    filter: "agTextColumnFilter",
    width: 220,
    hide: true,
    wrapText: true,
    autoHeight: true,
  },
  {
    colId: "scope_drug_authority",
    headerName: "Scope drug authority",
    valueGetter: (p) => ev(p.data, "scope", "drug_authority"),
    cellRenderer: TextCellRenderer,
    filter: "agTextColumnFilter",
    width: 220,
    hide: true,
    wrapText: true,
    autoHeight: true,
  },
  ];

  // ── Dynamic profession-specific columns (varies per profession) ──
  // discoveredFields lists every per-profession discovered field. We pull
  // .value out of each row's profession_specific[field.name] Evidence wrapper.
  // All default-hidden so they don't clutter the initial view.
  for (const f of discoveredFields) {
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
      hide: true,
      wrapText: f.type === "str" || f.type === "list[str]",
      autoHeight: true,
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
  fontFamily:
    "ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
  fontSize: 14,
  headerFontWeight: 600,
  headerBackgroundColor: "#f8fafc",
  oddRowBackgroundColor: "#ffffff",
  rowHoverColor: "#f1f5f9",
  borderColor: "#e2e8f0",
  wrapperBorderRadius: 8,
});

// Column id list + label map built dynamically per profession; see
// ProfileView for the live values (depends on payload.discovered_fields).

function colId(c: ColDef<Row>): string {
  return (c.field as string) || (c.colId as string);
}

// ============================================================================

export function ProfileView({ payload }: { payload: ProfilePayload }) {
  const { rows, evidence_summary, discovered_fields } = payload;
  const display = payload.display || payload.profession;
  const covered = rows.filter((r) => !r.coverage_gap).length;
  const gaps = rows.length - covered;
  const total = (evidence_summary?.verified || 0) + (evidence_summary?.unverified || 0);
  const pct = total
    ? ((100 * (evidence_summary?.verified || 0)) / total).toFixed(1)
    : "—";

  const gridRef = useRef<AgGridReact<Row>>(null);
  const [api, setApi] = useState<GridApi<Row> | null>(null);
  const [openState, setOpenState] = useState<string | null>(null);
  // Force re-render of the chip bar whenever AG Grid's filter model changes.
  // We track a tick rather than mirror the filter model into React state,
  // since the source of truth is the grid itself.
  const [filterTick, setFilterTick] = useState(0);

  // Build per-profession column defs from the static universal set + the
  // dynamic discovered fields, with each column's filter type auto-decided
  // from observed cardinality. Memoized so AG Grid sees stable refs.
  const columnDefs = useMemo(
    () => buildColumnDefs(discovered_fields, rows),
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
  // via lockVisible). Default: the columns marked hide:false in buildColumnDefs.
  const [visibleColumns, setVisibleColumns] = useState<Set<string>>(
    () =>
      new Set(
        columnDefs
          .filter((c) => !c.lockVisible && !c.hide)
          .map(colId)
      )
  );

  // URL-driven view + map field (unchanged from prior version)
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();
  const view: "table" | "map" =
    params.get("view") === "map" && payload.map_prep ? "map" : "table";
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
    updateParams({ view: v === "table" ? null : "map" });
  const setMapField = (f: string | null) => updateParams({ f });

  const onFilterChanged = (_e: FilterChangedEvent) => setFilterTick((t) => t + 1);

  const handleRowClick = useCallback(
    (event: { data: Row | undefined }) => {
      if (event.data) setOpenState(event.data.state);
    },
    []
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

  // ── Column visibility: drive AG Grid via API; UI is our own dropdown ──
  const toggleColumnVisible = (id: string, visible: boolean) => {
    setVisibleColumns((prev) => {
      const next = new Set(prev);
      if (visible) next.add(id);
      else next.delete(id);
      return next;
    });
    if (api) api.setColumnsVisible([id], visible);
  };

  // Sync visibility set to grid once the grid is ready.
  useEffect(() => {
    if (!api) return;
    for (const id of allToggleableIds) {
      api.setColumnsVisible([id], visibleColumns.has(id));
    }
    // Run only when api or the toggleable id list changes; visibility
    // changes are pushed synchronously in toggleColumnVisible.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [api, allToggleableIds]);

  return (
    <main className="mx-auto max-w-7xl px-6 py-10">
      <Link
        href="/"
        className="text-xs font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
      >
        ← all professions
      </Link>

      <p className="mt-6 text-xs font-mono tracking-widest uppercase text-muted-foreground">
        Profession profile
      </p>
      <h1 className="text-3xl font-semibold tracking-tight mt-1 mb-2">
        {display}
      </h1>
      <p className="text-muted-foreground max-w-3xl mb-6">
        Side-by-side licensure and scope of practice across 50 states,
        auto-extracted from state statutes. Every claim is backed by a
        verbatim quote validated against the source — click any row to see the
        quotes and citations. Click any column header for per-column filtering.
      </p>

      <div className="flex flex-wrap gap-x-8 gap-y-2 rounded-lg border bg-muted/30 px-4 py-3 mb-8 text-sm">
        <Stat label="states with extracted records" value={covered} />
        <Stat label="coverage gaps" value={gaps} />
        <Stat label="auto-discovered profession-specific fields" value={discovered_fields.length} />
        <Stat
          label={`evidence verified (${evidence_summary?.verified}/${total} quotes match source)`}
          value={`${pct}%`}
        />
      </div>

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
            <span className="text-xs font-mono text-muted-foreground">
              Filter per column by clicking its header (
              <span className="text-foreground">≡</span> icon). Toggle which
              columns are visible from the dropdown on the right.
            </span>

            <ColumnVisibilityPopover
              columns={toggleableColumns.map((c) => ({
                id: colId(c),
                label: (c.headerName as string) || colId(c),
              }))}
              visible={visibleColumns}
              onToggle={toggleColumnVisible}
            />
          </div>

          {/* Chip bar — every active filter shows as a removable chip */}
          {activeChips.length > 0 && (
            <div className="flex flex-wrap gap-2 items-center mb-3 px-1">
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
                // Tighten wrapped-text line spacing — AG Grid's default
                // leaves a paragraph-break-sized gap between wrapped lines.
                cellStyle: {
                  lineHeight: "1.35",
                  paddingTop: "8px",
                  paddingBottom: "8px",
                  display: "flex",
                  alignItems: "flex-start",
                },
              }}
              domLayout="autoHeight"
              onGridReady={(e) => setApi(e.api)}
              onRowClicked={handleRowClick}
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

      <StateDetailDialog
        rows={rows}
        fields={discovered_fields}
        openState={openState}
        onOpenChange={(o) => !o && setOpenState(null)}
      />
    </main>
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

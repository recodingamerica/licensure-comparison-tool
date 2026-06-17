"use client";

// Choropleth tab on the profile page. Reads the map_prep block off the
// per-profession payload (built by pipeline/map_prep/run.py → published
// via pipeline/publish/build_frontend.py) and renders one US map per
// selected field. Continuous fields use a linear ramp; categorical
// fields use an ordinal palette.
//
// Geography is the us-atlas states-10m TopoJSON, fetched from a CDN by
// react-simple-maps. State features are keyed by FIPS — we map those to
// USPS codes (which is what every other layer of the pipeline uses) via
// the table below.

import { useMemo } from "react";
import { scaleLinear } from "d3-scale";
import type { MapPrep, MapFieldSpec, MapRow } from "@/lib/types";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { humanize } from "@/lib/format";
import { UsMap, NO_DATA_FILL } from "@/components/us-map";

// The "priority" licensure concepts (mirrors PRIORITY_FIELDS in
// pipeline/publish/build_tag_sheet.py). Each maps to the dotted field name(s)
// it can be sourced from; a candidate resolves either from a Pass-3 text
// bucket (free-text fields normalized into bucket_set) or, failing that, from
// an already-normalized mappable field in mapPrep.spec (e.g. the
// regulatory_model enum). We surface whichever exists as a categorical
// "priority" choropleth grouped at the top of the field dropdown — these skip
// the "hide uniform" filter so headline concepts always appear, even when a
// profession is uniform (e.g. every state licenses optometrists). Discipline
// is intentionally omitted — it's per-item (a state has many grounds spanning
// several buckets), so it isn't a single-value choropleth; it lives on the tag
// sheet and the table's category column.
const PRIORITY_CONCEPTS: { concept: string; candidates: string[] }[] = [
  { concept: "Regulation (UORF)", candidates: ["licensure.regulatory_model"] },
  { concept: "Minimum Degree", candidates: ["licensure.education.degree_required"] },
  {
    concept: "Professional Experience",
    candidates: [
      "licensure.post_degree_experience.kind",
      "licensure.post_degree_experience.duration",
    ],
  },
  {
    concept: "Licensing Authority",
    candidates: [
      "licensure.issuing_authority",
      "licensure.regulatory_authority.name",
    ],
  },
  {
    concept: "Scope of Practice",
    candidates: [
      "scope.methods_authorized",
      "scope.drug_authority",
      "scope.definition_quote",
      "profession_specific.surgery_definition",
    ],
  },
];

// Synthetic field_name prefix for the "# of distinct tags" breadth maps, so
// they never collide with a real normalized field of the same dotted name.
const COUNT_PREFIX = "count::";

// Stable categorical palette — picked for distinguishability on a map at
// state-size. Up to ~12 categories before we wrap.
const CATEGORICAL_PALETTE = [
  "#0ea5e9", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
  "#ec4899", "#14b8a6", "#f97316", "#6366f1", "#84cc16",
  "#a855f7", "#06b6d4",
];

function continuousScale(values: number[]) {
  const nums = values.filter((v) => Number.isFinite(v));
  if (nums.length === 0) return null;
  const min = Math.min(...nums);
  const max = Math.max(...nums);
  // Light-to-dark blue ramp.
  return scaleLinear<string>()
    .domain([min, max])
    .range(["#dbeafe", "#1e3a8a"]);
}

// Per-field summary used to filter + rank the dropdown. "Uniform" fields
// (every state agrees, or only one distinct value across all non-null
// states) get hidden — a flat-colored map carries no information. Sparse
// fields are sorted to the bottom so the dropdown surfaces high-coverage
// maps first.
type FieldSummary = {
  spec: MapFieldSpec;
  coverage: number; // states with non-null normalized
  distinctValues: number; // distinct non-null normalized values
};

// A synthesized priority-field spec carries its plain-English concept label
// (e.g. "Minimum Degree") for the dropdown; otherwise it's a normal spec.
type PrioritySpec = MapFieldSpec & { concept: string };

function summarize(specs: MapFieldSpec[], rows: MapRow[]): FieldSummary[] {
  const byField = new Map<string, MapRow[]>();
  for (const r of rows) {
    const list = byField.get(r.field_name) ?? [];
    list.push(r);
    byField.set(r.field_name, list);
  }
  return specs.map((spec) => {
    const list = byField.get(spec.field_name) ?? [];
    const nonNull = list.filter((r) => r.normalized !== null);
    const distinct = new Set(nonNull.map((r) => r.normalized));
    return {
      spec,
      coverage: nonNull.length,
      distinctValues: distinct.size,
    };
  });
}

export function MapView({
  mapPrep,
  fieldName: fieldNameProp,
  onFieldChange,
}: {
  mapPrep: MapPrep;
  // Selected field comes from the URL via the parent so every choropleth
  // has a permanent link. Null means "no field in URL — fall back to the
  // first one in the dropdown".
  fieldName: string | null;
  onFieldChange: (f: string | null) => void;
}) {
  // Priority fields are the bucketed free-text fields (not_mappable, so absent
  // from mapPrep.spec). We synthesize categorical specs + per-state rows from
  // the Pass-3 text buckets so they can render as choropleths grouped at the
  // top of the dropdown.
  const { prioritySpecs, priorityRows } = useMemo(() => {
    const specs: PrioritySpec[] = [];
    const rows: MapRow[] = [];
    const tb = mapPrep.text_buckets ?? {};
    const specByName = new Map(mapPrep.spec.map((s) => [s.field_name, s]));
    for (const { concept, candidates } of PRIORITY_CONCEPTS) {
      // One map per concept — stop at the first candidate that exists.
      for (const fn of candidates) {
        // Case 1: a Pass-3 bucketed free-text field (not in mapPrep.spec).
        const entry = tb[fn];
        const byState = entry?.by_state ?? {};
        if (entry && Object.keys(byState).length > 0) {
          specs.push({
            field_name: fn,
            mappable: true,
            kind: "categorical",
            unit: null,
            categories: entry.bucket_set ?? [],
            reason: entry.rationale ?? "",
            concept,
          });
          for (const [state, bucket] of Object.entries(byState)) {
            rows.push({ field_name: fn, state, raw_value: bucket, normalized: bucket });
          }
          break;
        }
        // Case 2: an already-normalized mappable field (e.g. the
        // regulatory_model enum) — reuse its real spec + rows. priorityNames
        // then excludes it from "All mapped fields" so it isn't shown twice.
        const existing = specByName.get(fn);
        if (existing) {
          specs.push({ ...existing, concept });
          for (const r of mapPrep.rows) {
            if (r.field_name === fn) rows.push(r);
          }
          break;
        }
      }
    }
    return { prioritySpecs: specs, priorityRows: rows };
  }, [mapPrep]);

  const priorityNames = useMemo(
    () => new Set(prioritySpecs.map((s) => s.field_name)),
    [prioritySpecs]
  );

  // "Scope breadth" maps: # of distinct content categories each state falls
  // into for a per-item list field (laser procedures, injections, …). Rendered
  // as continuous choropleths — higher = broader authorized scope.
  const { breadthSpecs, breadthRows } = useMemo(() => {
    const specs: MapFieldSpec[] = [];
    const rows: MapRow[] = [];
    for (const cf of mapPrep.per_item_count_fields ?? []) {
      const entries = Object.entries(cf.by_state_count);
      if (entries.length < 2) continue;
      const id = COUNT_PREFIX + cf.field_name;
      specs.push({
        field_name: id,
        mappable: true,
        kind: "continuous",
        unit: "tags",
        categories: null,
        reason: `Number of distinct ${prettyFieldName(cf.field_name)} categories each state falls into.`,
      });
      for (const [state, n] of entries) {
        rows.push({ field_name: id, state, raw_value: String(n), normalized: n });
      }
    }
    return { breadthSpecs: specs, breadthRows: rows };
  }, [mapPrep]);

  // Hide uniform fields (≤1 distinct non-null value); sort remaining by
  // coverage descending so the most "interesting" maps are at the top.
  // Priority fields are pulled out and shown first, so exclude them here.
  const otherSummaries = useMemo(() => {
    const summaries = summarize(mapPrep.spec, mapPrep.rows);
    return summaries
      .filter((s) => s.distinctValues > 1 && !priorityNames.has(s.spec.field_name))
      .sort((a, b) => b.coverage - a.coverage);
  }, [mapPrep, priorityNames]);

  const otherSpecs = useMemo(
    () => otherSummaries.map((s) => s.spec),
    [otherSummaries]
  );

  // Priority maps first, then the rest, then the breadth maps. Drives both the
  // dropdown order and the default selection (an unparameterized URL lands on
  // the first priority map).
  const allSpecs = useMemo(
    () => [...prioritySpecs, ...otherSpecs, ...breadthSpecs],
    [prioritySpecs, otherSpecs, breadthSpecs]
  );

  const coverageByField = useMemo(() => {
    const m = new Map<string, number>();
    for (const r of priorityRows) {
      if (r.normalized == null) continue;
      m.set(r.field_name, (m.get(r.field_name) ?? 0) + 1);
    }
    for (const r of breadthRows) {
      if (r.normalized == null) continue;
      m.set(r.field_name, (m.get(r.field_name) ?? 0) + 1);
    }
    for (const s of otherSummaries) m.set(s.spec.field_name, s.coverage);
    return m;
  }, [priorityRows, breadthRows, otherSummaries]);

  // If the URL field exists in the visible list, use it; otherwise fall
  // back to the first one (which is what an unparameterized URL gets).
  const fieldName =
    fieldNameProp && allSpecs.some((s) => s.field_name === fieldNameProp)
      ? fieldNameProp
      : allSpecs[0]?.field_name ?? "";

  const spec = useMemo<MapFieldSpec | undefined>(
    () => allSpecs.find((s) => s.field_name === fieldName),
    [allSpecs, fieldName]
  );

  // state → MapRow for the currently selected field (priority rows are
  // synthesized above; the rest come straight from mapPrep.rows).
  const allRows = useMemo(
    () => [...priorityRows, ...breadthRows, ...mapPrep.rows],
    [priorityRows, breadthRows, mapPrep.rows]
  );
  const byState = useMemo(() => {
    const out = new Map<string, MapRow>();
    if (!spec) return out;
    for (const r of allRows) {
      if (r.field_name === spec.field_name) out.set(r.state, r);
    }
    return out;
  }, [allRows, spec]);

  // field_name → friendly label, so the closed dropdown shows "Minimum Degree"
  // rather than the raw dotted path.
  const labelByField = useMemo(() => {
    const m = new Map<string, string>();
    for (const s of prioritySpecs) m.set(s.field_name, s.concept);
    for (const s of otherSpecs) m.set(s.field_name, prettyFieldName(s.field_name));
    for (const s of breadthSpecs)
      m.set(s.field_name, breadthLabel(s.field_name));
    return m;
  }, [prioritySpecs, otherSpecs, breadthSpecs]);

  // Color mapping (depends on field kind)
  const colorFor = useMemo(() => {
    if (!spec) return () => NO_DATA_FILL;
    if (spec.kind === "continuous") {
      const nums = Array.from(byState.values())
        .map((r) => (typeof r.normalized === "number" ? r.normalized : NaN))
        .filter((v) => Number.isFinite(v));
      const scale = continuousScale(nums);
      return (state: string) => {
        const r = byState.get(state);
        const v = r?.normalized;
        if (!scale || typeof v !== "number") return NO_DATA_FILL;
        return scale(v);
      };
    }
    // categorical
    const cats = spec.categories ?? [];
    const palette: Record<string, string> = {};
    cats.forEach((c, i) => {
      palette[c] = CATEGORICAL_PALETTE[i % CATEGORICAL_PALETTE.length];
    });
    return (state: string) => {
      const r = byState.get(state);
      const v = r?.normalized;
      if (typeof v !== "string") return NO_DATA_FILL;
      return palette[v] ?? NO_DATA_FILL;
    };
  }, [spec, byState]);

  // Legend
  const legend = useMemo(() => {
    if (!spec) return null;
    if (spec.kind === "continuous") {
      const nums = Array.from(byState.values())
        .map((r) => (typeof r.normalized === "number" ? r.normalized : NaN))
        .filter((v) => Number.isFinite(v));
      if (nums.length === 0) return null;
      const min = Math.min(...nums);
      const max = Math.max(...nums);
      return (
        <div className="flex items-center gap-3 text-xs font-mono text-muted-foreground">
          <span>{min}</span>
          <div
            className="h-3 w-48 rounded"
            style={{
              background: "linear-gradient(to right, #dbeafe, #1e3a8a)",
            }}
          />
          <span>{max}</span>
          {spec.unit && <span className="ml-2">{spec.unit}</span>}
        </div>
      );
    }
    const cats = spec.categories ?? [];
    // Only show categories that actually appear in this profession's data,
    // to keep the legend short.
    const present = new Set(
      Array.from(byState.values())
        .map((r) => r.normalized)
        .filter((v): v is string => typeof v === "string")
    );
    return (
      <div className="flex flex-col gap-1.5 text-sm max-w-sm">
        {cats.filter((c) => present.has(c)).map((c) => (
          <span key={c} className="flex items-start gap-2 leading-snug">
            <span
              className="inline-block h-3 w-3 rounded-sm mt-1 shrink-0"
              style={{
                background:
                  CATEGORICAL_PALETTE[cats.indexOf(c) % CATEGORICAL_PALETTE.length],
              }}
            />
            <span>{humanize(c)}</span>
          </span>
        ))}
        <span className="flex items-start gap-2 leading-snug">
          <span
            className="inline-block h-3 w-3 rounded-sm mt-1 shrink-0"
            style={{ background: NO_DATA_FILL }}
          />
          <span className="text-muted-foreground">no data</span>
        </span>
      </div>
    );
  }, [spec, byState]);

  if (!allSpecs.length) {
    return (
      <div className="rounded border bg-muted/30 p-6 text-sm text-muted-foreground">
        No mappable fields yet for this profession. Run{" "}
        <code className="font-mono">python -m pipeline.map_prep.run &lt;profession&gt;</code>{" "}
        first.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <span className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
          Field
        </span>
        <Select value={fieldName} onValueChange={(v) => v && onFieldChange(v)}>
          <SelectTrigger className="w-[28rem]">
            <SelectValue>
              {(value) =>
                labelByField.get(value as string) ??
                prettyFieldName(String(value ?? ""))
              }
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            {prioritySpecs.length > 0 && (
              <SelectGroup>
                <SelectLabel>Priority fields</SelectLabel>
                {prioritySpecs.map((s) => {
                  const cov = coverageByField.get(s.field_name) ?? 0;
                  return (
                    <SelectItem key={s.field_name} value={s.field_name}>
                      {s.concept} ({cov} states)
                    </SelectItem>
                  );
                })}
              </SelectGroup>
            )}
            {otherSpecs.length > 0 && (
              <SelectGroup>
                <SelectLabel>All mapped fields</SelectLabel>
                {otherSpecs.map((s) => {
                  const cov = coverageByField.get(s.field_name) ?? 0;
                  return (
                    <SelectItem key={s.field_name} value={s.field_name}>
                      {prettyFieldName(s.field_name)} ({s.kind}, {cov} states)
                    </SelectItem>
                  );
                })}
              </SelectGroup>
            )}
            {breadthSpecs.length > 0 && (
              <SelectGroup>
                <SelectLabel>Scope breadth (distinct tags)</SelectLabel>
                {breadthSpecs.map((s) => {
                  const cov = coverageByField.get(s.field_name) ?? 0;
                  return (
                    <SelectItem key={s.field_name} value={s.field_name}>
                      {breadthLabel(s.field_name)} ({cov} states)
                    </SelectItem>
                  );
                })}
              </SelectGroup>
            )}
          </SelectContent>
        </Select>
      </div>

      {spec && (
        <p className="text-xs text-muted-foreground max-w-3xl">
          {spec.reason}
        </p>
      )}

      <UsMap
        fillFor={colorFor}
        renderTooltip={(state) => {
          const row = byState.get(state);
          const normalizedStr = row
            ? row.normalized === null
              ? "no data"
              : String(row.normalized)
            : "no data";
          const rawStr = row?.raw_value || "—";
          return (
            <>
              <div className="font-mono text-base font-semibold">{state}</div>
              <div className="mt-1">
                {normalizedStr}
                {rawStr && rawStr !== normalizedStr && (
                  <span className="ml-2 text-muted-foreground">
                    (raw: {rawStr})
                  </span>
                )}
              </div>
              {row?.quote && (
                <div className="mt-2 border-t pt-2 leading-relaxed">
                  <div className="text-foreground">“{row.quote}”</div>
                  {row.citation && (
                    <div className="mt-1 font-mono text-xs text-muted-foreground">
                      {row.citation}
                    </div>
                  )}
                </div>
              )}
            </>
          );
        }}
      />

      <div>{legend}</div>
    </div>
  );
}

// Label for a breadth (distinct-tag count) map: "# distinct <field> tags".
function breadthLabel(id: string): string {
  return `# distinct ${prettyFieldName(id.replace(COUNT_PREFIX, ""))} tags`;
}

// Trim "licensure." / "profession_specific." prefixes since they're noise
// in a per-profession dropdown.
function prettyFieldName(fn: string): string {
  const trimmed = fn
    .replace(/^licensure\./, "")
    .replace(/^profession_specific\./, "")
    .replace(/^scope\./, "scope · ");
  return humanize(trimmed.replaceAll(".", " · "));
}

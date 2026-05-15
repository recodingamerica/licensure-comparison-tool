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

import { useMemo, useState } from "react";
import { ComposableMap, Geographies, Geography } from "react-simple-maps";
import { scaleLinear } from "d3-scale";
import type { MapPrep, MapFieldSpec, MapRow } from "@/lib/types";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { humanize } from "@/lib/format";

const GEO_URL = "https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json";

// FIPS → USPS. us-atlas keys state features by FIPS id; the rest of the
// pipeline (and the normalized rows) uses USPS two-letter codes.
const FIPS_TO_USPS: Record<string, string> = {
  "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO",
  "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI",
  "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
  "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
  "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
  "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
  "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
  "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
  "54": "WV", "55": "WI", "56": "WY",
};

// Stable categorical palette — picked for distinguishability on a map at
// state-size. Up to ~12 categories before we wrap.
const CATEGORICAL_PALETTE = [
  "#0ea5e9", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
  "#ec4899", "#14b8a6", "#f97316", "#6366f1", "#84cc16",
  "#a855f7", "#06b6d4",
];
const NO_DATA_FILL = "#e5e7eb"; // tailwind zinc-200

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
  // Hide uniform fields (≤1 distinct non-null value); sort remaining by
  // coverage descending so the most "interesting" maps are at the top.
  const visibleSpecs = useMemo(() => {
    const summaries = summarize(mapPrep.spec, mapPrep.rows);
    return summaries
      .filter((s) => s.distinctValues > 1)
      .sort((a, b) => b.coverage - a.coverage);
  }, [mapPrep]);

  const specs = visibleSpecs.map((s) => s.spec);
  const coverageByField = useMemo(() => {
    const m = new Map<string, number>();
    for (const s of visibleSpecs) m.set(s.spec.field_name, s.coverage);
    return m;
  }, [visibleSpecs]);

  // If the URL field exists in the visible list, use it; otherwise fall
  // back to the first one (which is what an unparameterized URL gets).
  const fieldName =
    fieldNameProp && specs.some((s) => s.field_name === fieldNameProp)
      ? fieldNameProp
      : specs[0]?.field_name ?? "";

  const spec = useMemo<MapFieldSpec | undefined>(
    () => specs.find((s) => s.field_name === fieldName),
    [specs, fieldName]
  );

  // state → MapRow for the currently selected field
  const byState = useMemo(() => {
    const out = new Map<string, MapRow>();
    if (!spec) return out;
    for (const r of mapPrep.rows) {
      if (r.field_name === spec.field_name) out.set(r.state, r);
    }
    return out;
  }, [mapPrep.rows, spec]);

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

  const [hover, setHover] = useState<{
    state: string;
    normalized: string;
    raw: string;
    quote?: string;
    citation?: string;
    x: number;
    y: number;
  } | null>(null);

  if (!specs.length) {
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
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {specs.map((s) => {
              const cov = coverageByField.get(s.field_name) ?? 0;
              return (
                <SelectItem key={s.field_name} value={s.field_name}>
                  {prettyFieldName(s.field_name)} ({s.kind}, {cov} states)
                </SelectItem>
              );
            })}
          </SelectContent>
        </Select>
      </div>

      {spec && (
        <p className="text-xs text-muted-foreground max-w-3xl">
          {spec.reason}
        </p>
      )}

      <div className="rounded-lg border bg-white">
        <ComposableMap
          projection="geoAlbersUsa"
          projectionConfig={{ scale: 1000 }}
          width={975}
          height={610}
          style={{ width: "100%", height: "auto" }}
        >
          <Geographies geography={GEO_URL}>
            {({ geographies }) =>
              geographies.map((geo) => {
                const fips = String(geo.id).padStart(2, "0");
                const usps = FIPS_TO_USPS[fips];
                const row = usps ? byState.get(usps) : undefined;
                const fill = usps ? colorFor(usps) : NO_DATA_FILL;
                const normalizedStr = row
                  ? row.normalized === null
                    ? "no data"
                    : String(row.normalized)
                  : "no data";
                const rawStr = row?.raw_value || "—";
                return (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    fill={fill}
                    stroke="#ffffff"
                    strokeWidth={0.5}
                    onMouseEnter={(e) => {
                      if (usps)
                        setHover({
                          state: usps,
                          normalized: normalizedStr,
                          raw: rawStr,
                          quote: row?.quote,
                          citation: row?.citation,
                          x: e.clientX,
                          y: e.clientY,
                        });
                    }}
                    onMouseMove={(e) => {
                      if (usps)
                        setHover((h) =>
                          h && h.state === usps
                            ? { ...h, x: e.clientX, y: e.clientY }
                            : h
                        );
                    }}
                    onMouseLeave={() => setHover(null)}
                    style={{
                      default: { outline: "none" },
                      hover: { outline: "none", opacity: 0.85 },
                      pressed: { outline: "none" },
                    }}
                  />
                );
              })
            }
          </Geographies>
        </ComposableMap>
      </div>

      <div>{legend}</div>

      {hover && (
        <div
          className="pointer-events-none fixed z-50 max-w-lg rounded-md border bg-popover px-4 py-3 text-sm shadow-md"
          style={{
            left: hover.x + 12,
            top: hover.y + 12,
          }}
        >
          <div className="font-mono text-base font-semibold">{hover.state}</div>
          <div className="mt-1">
            {hover.normalized}
            {hover.raw && hover.raw !== hover.normalized && (
              <span className="ml-2 text-muted-foreground">
                (raw: {hover.raw})
              </span>
            )}
          </div>
          {hover.quote && (
            <div className="mt-2 border-t pt-2 leading-relaxed">
              <div className="text-foreground">“{hover.quote}”</div>
              {hover.citation && (
                <div className="mt-1 font-mono text-xs text-muted-foreground">
                  {hover.citation}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
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

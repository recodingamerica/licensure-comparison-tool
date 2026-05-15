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

export function MapView({ mapPrep }: { mapPrep: MapPrep }) {
  const specs = mapPrep.spec;
  const [fieldName, setFieldName] = useState<string>(
    specs[0]?.field_name ?? ""
  );

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
      <div className="flex flex-wrap gap-x-4 gap-y-2 text-xs">
        {cats.filter((c) => present.has(c)).map((c, i) => (
          <span key={c} className="inline-flex items-center gap-1.5">
            <span
              className="inline-block h-3 w-3 rounded-sm"
              style={{
                background:
                  CATEGORICAL_PALETTE[cats.indexOf(c) % CATEGORICAL_PALETTE.length],
              }}
            />
            <span className="font-mono">{humanize(c)}</span>
          </span>
        ))}
        <span className="inline-flex items-center gap-1.5">
          <span
            className="inline-block h-3 w-3 rounded-sm"
            style={{ background: NO_DATA_FILL }}
          />
          <span className="font-mono text-muted-foreground">no data</span>
        </span>
      </div>
    );
  }, [spec, byState]);

  const [hover, setHover] = useState<{ state: string; value: string } | null>(
    null
  );

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
        <Select value={fieldName} onValueChange={(v) => v && setFieldName(v)}>
          <SelectTrigger className="w-[28rem]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {specs.map((s) => (
              <SelectItem key={s.field_name} value={s.field_name}>
                {prettyFieldName(s.field_name)} ({s.kind})
              </SelectItem>
            ))}
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
                const hoverValue = row
                  ? row.normalized === null
                    ? "no data"
                    : String(row.normalized)
                  : "no data";
                return (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    fill={fill}
                    stroke="#ffffff"
                    strokeWidth={0.5}
                    onMouseEnter={() => {
                      if (usps) setHover({ state: usps, value: hoverValue });
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

      <div className="flex flex-wrap items-center justify-between gap-3">
        {legend}
        <div className="text-xs font-mono text-muted-foreground min-h-[1rem]">
          {hover ? `${hover.state}: ${hover.value}` : "hover a state"}
        </div>
      </div>
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

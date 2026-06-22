"use client";

// Compare tab — the regulatory landscape for one occupation.
//
// Method (kept transparent in the UI on purpose):
//   - Overlap is computed deterministically over a fixed CORE set of questions:
//     the important fields that MOST states answer. Every state is graded on the
//     same questions; states answering too few are shown gray, not given a score.
//   - No percentages: it's a weighted judgment, not a measurement, so magnitude is
//     shown as words (the calc assigns them) and as map color.
//
// Self-fetches /data/analysis/<prof>.json (pipeline.analyze.similarity).

import { useEffect, useMemo, useState } from "react";
import type { ProfileAnalysis } from "@/lib/types";
import { UsMap, NO_DATA_FILL } from "@/components/us-map";

// leaf words too generic to stand alone -> fold in the parent segment
const GENERIC = new Set([
  "required", "available", "exists", "offered", "permitted",
  "authorized", "prohibited", "allowed", "excluded", "type",
]);
function fieldLabel(f: string): string {
  const parts = f.split(".");
  let leaf = parts[parts.length - 1];
  if (GENERIC.has(leaf) && parts.length >= 2) leaf = `${parts[parts.length - 2]}_${leaf}`;
  const s = leaf.replace(/_/g, " ");
  return s.charAt(0).toUpperCase() + s.slice(1);
}
const val = (v: string) => (v === "true" ? "yes" : v === "false" ? "no" : v.replace(/_/g, " "));

function ramp(t: number): string {
  const a = [238, 236, 228];
  const b = [180, 83, 9];
  const c = a.map((x, i) => Math.round(x + (b[i] - x) * Math.max(0, Math.min(1, t))));
  return `rgb(${c[0]}, ${c[1]}, ${c[2]})`;
}

const SPREAD_VERB: Record<string, string> = {
  wide: "vary widely",
  moderate: "vary moderately",
  narrow: "are broadly similar",
};

export function SimilarityView({ professionId }: { professionId: string }) {
  const [data, setData] = useState<ProfileAnalysis | null>(null);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    setData(null);
    setMissing(false);
    fetch(`/data/analysis/${encodeURIComponent(professionId)}.json`)
      .then((r) => (r.status === 404 ? (setMissing(true), null) : r.ok ? r.json() : null))
      .then((d: ProfileAnalysis | null) => d && setData(d))
      .catch(() => setMissing(true));
  }, [professionId]);

  const distRange = useMemo(() => {
    if (!data) return [0, 1] as const;
    const vals = Object.values(data.distinctiveness);
    return vals.length ? ([Math.min(...vals), Math.max(...vals)] as const) : ([0, 1] as const);
  }, [data]);

  if (missing)
    return (
      <p className="text-sm text-muted-foreground">
        No comparison data for this profession yet — run{" "}
        <code className="text-xs">pipeline.analyze.similarity --json</code> +{" "}
        <code className="text-xs">publish_analysis</code>.
      </p>
    );
  if (!data) return <p className="text-sm text-muted-foreground">Loading…</p>;

  const ls = data.landscape;
  const [dmin, dmax] = distRange;
  const span = dmax - dmin || 1;
  const insufficient = new Set(data.insufficient_states);

  const fillFor = (st: string) => {
    const d = data.distinctiveness[st];
    return d === undefined ? NO_DATA_FILL : ramp((d - dmin) / span);
  };

  const renderTooltip = (st: string) => {
    if (!(st in data.notes)) return null;
    if (insufficient.has(st))
      return <div className="w-60 text-xs">{st} — not enough core data to compare.</div>;

    const nb = (data.neighbors[st] ?? []).slice(0, 3).map((n) => n.state);
    // unusual values: rare categories + much-stricter/looser, each with its label
    const seen = new Set<string>();
    const unusual: { label: string; value: string; tag: string }[] = [];
    for (const o of data.kind_outliers)
      if (o.state === st && !seen.has(o.field)) {
        seen.add(o.field);
        unusual.push({ label: fieldLabel(o.field), value: val(o.value), tag: o.rarity });
      }
    for (const o of data.stringency_outliers)
      if (o.state === st && !seen.has(o.field)) {
        seen.add(o.field);
        unusual.push({ label: fieldLabel(o.field), value: val(o.value), tag: o.magnitude });
      }
    const agree = (data.typical_on[st] ?? []).slice(0, 5);

    return (
      <div className="w-72 text-xs space-y-2">
        <div>
          <span className="font-semibold text-sm">{st}</span>
          <span className="ml-2 text-muted-foreground">{data.bands[st]}</span>
          {nb.length > 0 && <div className="text-muted-foreground">most like {nb.join(", ")}</div>}
        </div>
        <div>
          <div className="font-mono uppercase tracking-wide text-[10px] text-muted-foreground">Unusual values</div>
          {unusual.length === 0 ? (
            <div className="text-muted-foreground">none — typical across the board</div>
          ) : (
            unusual.slice(0, 6).map((u, i) => (
              <div key={i}>
                <span className="font-medium">{u.label}:</span> {u.value}{" "}
                <span className="text-muted-foreground">({u.tag})</span>
              </div>
            ))
          )}
        </div>
        {agree.length > 0 && (
          <div>
            <div className="font-mono uppercase tracking-wide text-[10px] text-muted-foreground">Same as most states</div>
            {agree.map((t, i) => (
              <div key={i}>
                <span className="font-medium">{fieldLabel(t.field)}:</span> {val(t.value)}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const coreLabels = data.core_fields.map(fieldLabel);
  const drivers = ls.drivers.slice(0, 3).map((d) => fieldLabel(d.field));
  const mostDistinct = Object.keys(data.distinctiveness).slice(0, 5);
  const spreadVerb = SPREAD_VERB[ls.spread_label] ?? "vary";
  const driverTail =
    ls.spread_label === "narrow"
      ? `, with the most variation on ${drivers.join(", ")}`
      : `, differing most on ${drivers.join(", ")}`;

  return (
    <div className="space-y-5">
      {/* Method — what the comparison is based on */}
      <div className="rounded-md border bg-muted/20 px-4 py-3 text-xs text-muted-foreground leading-relaxed">
        States are compared on the <strong className="text-foreground">{data.n_core} core questions</strong> most
        states answer: {coreLabels.join(", ")}. Details that only some states report don&apos;t enter the
        comparison — they appear as a state&apos;s unusual values instead.
        {data.insufficient_states.length > 0 && (
          <>
            {" "}Not enough core answers to compare (shown gray):{" "}
            <span className="font-mono">{data.insufficient_states.join(", ")}</span>.
          </>
        )}
      </div>

      {/* Macro — only describes the core set, no false "other fields are uniform" */}
      <div className="text-sm leading-relaxed">
        On these {data.n_core} questions, states <strong>{spreadVerb}</strong>
        {driverTail}.
      </div>

      {/* Utah summary (deterministic) */}
      {data.notes["UT"] && (
        <div className="rounded-md border bg-muted/30 px-4 py-3 text-sm leading-relaxed">{data.notes["UT"]}</div>
      )}

      {/* The landscape: map colored by distinctiveness, hover for agree vs unusual */}
      <div>
        <div className="text-[11px] font-mono uppercase tracking-widest text-muted-foreground mb-2">
          How distinctive each state is — hover for where it agrees &amp; what&apos;s unusual
        </div>
        <UsMap fillFor={fillFor} renderTooltip={renderTooltip} />
        <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
          <span>typical</span>
          <span
            className="inline-block h-2 w-32 rounded"
            style={{ background: `linear-gradient(to right, ${ramp(0)}, ${ramp(1)})` }}
          />
          <span>most distinctive</span>
          <span className="ml-2">→ {mostDistinct.join(", ")}</span>
          <span className="ml-2">
            <span className="inline-block h-2 w-3 rounded align-middle" style={{ background: NO_DATA_FILL }} /> not
            enough data
          </span>
        </div>
      </div>
    </div>
  );
}

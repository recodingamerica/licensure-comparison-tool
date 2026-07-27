"use client";

// Compare tab — the regulatory landscape for one occupation.
//
// Method (kept transparent on purpose): overlap is computed deterministically over
// a fixed CORE set of questions — the important fields most states answer — so every
// state is graded on the same questions. States answering too few are shown gray.
// No percentages: it's a weighted judgment, shown as words + map color.
//
// Novel policies (the rarity slider + click-to-map) used to live here too; they
// moved to the dedicated Novel Policies tab (#52), leaving this tab focused on the
// similarity landscape.
//
// Self-fetches /data/analysis/<prof>.json (pipeline.analyze.similarity).

import { useEffect, useMemo, useState } from "react";
import type { ProfileAnalysis } from "@/lib/types";
import { UsMap, NO_DATA_FILL } from "@/components/us-map";
import { useOpenStateDetail } from "@/components/state-focus";
import { fieldLabel, formatFieldValue as val } from "@/lib/format";
import { token } from "@/lib/web-colors";

const lc = (s: string) => (s ? s.charAt(0).toLowerCase() + s.slice(1) : s);
function joinAnd(items: string[]): string {
  if (items.length <= 1) return items[0] ?? "";
  if (items.length === 2) return `${items[0]} and ${items[1]}`;
  return `${items.slice(0, -1).join(", ")}, and ${items[items.length - 1]}`;
}

function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace("#", "");
  return [
    parseInt(h.slice(0, 2), 16),
    parseInt(h.slice(2, 4), 16),
    parseInt(h.slice(4, 6), 16),
  ];
}

function ramp(t: number): string {
  const a = hexToRgb(token("spread-lo"));
  const b = hexToRgb(token("spread-hi"));
  const c = a.map((x, i) => Math.round(x + (b[i] - x) * Math.max(0, Math.min(1, t))));
  return `rgb(${c[0]}, ${c[1]}, ${c[2]})`;
}

const SPREAD_VERB: Record<string, string> = {
  wide: "vary widely",
  moderate: "vary moderately",
  narrow: "are broadly similar",
};

export function SimilarityView({ professionId }: { professionId: string }) {
  const open = useOpenStateDetail();
  const [data, setData] = useState<ProfileAnalysis | null>(null);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    setData(null);
    setMissing(false);
    fetch(`/data/analysis/${encodeURIComponent(professionId)}.json`)
      .then((r) => (r.status === 404 ? (setMissing(true), null) : r.ok ? r.json() : null))
      .then((d: ProfileAnalysis | null) => {
        if (d) setData(d);
      })
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
  const lowConf = (st: string) => (data.core_coverage[st] ?? 1) < 0.7;

  const fillFor = (st: string) => {
    const d = data.distinctiveness[st];
    return d === undefined ? NO_DATA_FILL : ramp((d - dmin) / span);
  };

  // A state's "differs / same" lists — shared by the hover and the Utah panel.
  const Row = ({ label, tail }: { label: string; tail: string }) => (
    <div className="leading-snug">
      {label} <span className="text-muted-foreground">— {tail}</span>
    </div>
  );
  const heading = (t: string) => <div className="mb-1.5 text-xs text-muted-foreground">{t}</div>;
  const profileLists = (st: string, limitDiff: number, limitSame: number) => {
    const differs = data.differs_on[st] ?? [];
    const agree = data.typical_on[st] ?? [];
    return (
      <>
        <div>
          {heading("Differs from most states")}
          {differs.length === 0 ? (
            <div className="text-muted-foreground">matches the majority everywhere</div>
          ) : (
            differs.slice(0, limitDiff).map((u, i) => (
              <Row key={i} label={fieldLabel(u.field)} tail={`${val(u.value)} (${u.label})`} />
            ))
          )}
        </div>
        {agree.length > 0 && (
          <div>
            {heading("Same as most states")}
            {agree.slice(0, limitSame).map((t, i) => (
              <Row key={i} label={fieldLabel(t.field)} tail={val(t.value)} />
            ))}
          </div>
        )}
      </>
    );
  };

  const renderTooltip = (st: string) => {
    if (!(st in data.notes)) return null;
    if (insufficient.has(st))
      return <div className="w-60 text-xs">{st} — not enough core data to compare.</div>;
    const nb = (data.neighbors[st] ?? []).slice(0, 3).map((n) => n.state);
    return (
      <div className="w-72 space-y-2.5 text-xs">
        <div>
          <span className="font-medium text-sm">{st}</span>
          <span className="ml-2 text-muted-foreground">{data.bands[st]}</span>
          {nb.length > 0 && <div className="text-muted-foreground">most like {nb.join(", ")}</div>}
          {lowConf(st) && <div className="text-amber-700">limited data — a rough read</div>}
        </div>
        {profileLists(st, 6, 5)}
      </div>
    );
  };

  const coreLabels = data.core_fields.map(fieldLabel);
  const drivers = ls.drivers.slice(0, 3).map((d) => fieldLabel(d.field));
  const mostDistinct = Object.keys(data.distinctiveness).filter((s) => !lowConf(s)).slice(0, 5);
  const spreadVerb = SPREAD_VERB[ls.spread_label] ?? "vary";
  const driverList = joinAnd(drivers.map(lc));
  const driverTail =
    ls.spread_label === "narrow"
      ? `, with the most variation on ${driverList}`
      : `, differing most on ${driverList}`;

  return (
    <div className="max-w-7xl space-y-6">
      {/* Lead with the insight. */}
      <p className="text-base leading-relaxed">
        On the {data.n_core} questions most states answer, regimes{" "}
        <span className="font-medium">{spreadVerb}</span>
        {driverTail}.
      </p>

      {/* Method — quiet supporting line. */}
      <p className="text-xs leading-relaxed text-muted-foreground">
        Based on the questions most states answer ({joinAnd(coreLabels.map(lc))}); sparser details that only some
        states report show up as a state&apos;s unusual values instead.
        {data.insufficient_states.length > 0 && (
          <> Too few answers to compare: {data.insufficient_states.join(", ")}.</>
        )}
      </p>

      {/* Utah — the focus state, shown in full. */}
      {data.notes["UT"] && (
        <div className="border-t pt-5 space-y-3">
          <p className="text-[15px] leading-relaxed">{data.notes["UT"]}</p>
          <div className="grid gap-x-12 gap-y-4 text-[15px] sm:grid-cols-2">{profileLists("UT", 99, 99)}</div>
        </div>
      )}

      {/* The landscape map — how distinctive each state is. */}
      <div className="border-t pt-5">
        <p className="mb-3 text-xs text-muted-foreground">
          How distinctive each state is — hover any state for where it agrees and what&apos;s unusual.
        </p>
        <div className="mb-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
          <span>typical</span>
          <span
            className="inline-block h-2 w-28 rounded"
            style={{ background: `linear-gradient(to right, ${ramp(0)}, ${ramp(1)})` }}
          />
          <span>most distinctive</span>
          <span className="ml-1 text-foreground/70">{mostDistinct.join(", ")}</span>
          <span className="ml-2 flex items-center gap-1">
            <span className="inline-block h-2 w-3 rounded" style={{ background: NO_DATA_FILL }} /> not enough data
          </span>
        </div>
        {/* No single field applies here — Compare grades a state across the whole core
            set — so this opens the state's full Sheet, per the click contract. */}
        <UsMap
          fillFor={fillFor}
          renderTooltip={renderTooltip}
          onClick={open ?? undefined}
          bare
        />
      </div>
    </div>
  );
}

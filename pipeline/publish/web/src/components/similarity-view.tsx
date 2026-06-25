"use client";

// Compare tab — the regulatory landscape for one occupation.
//
// Method (kept transparent on purpose): overlap is computed deterministically over
// a fixed CORE set of questions — the important fields most states answer — so every
// state is graded on the same questions. States answering too few are shown gray.
// No percentages: it's a weighted judgment, shown as words + map color.
//
// Self-fetches /data/analysis/<prof>.json (pipeline.analyze.similarity).

import { useEffect, useMemo, useState } from "react";
import type { ProfileAnalysis, NovelPolicy } from "@/lib/types";
import { UsMap, NO_DATA_FILL } from "@/components/us-map";
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip";

const NOVEL_MAX_K = 10; // slider ceiling (the backend emits policies up to 15 states)

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
const clip = (s: string, n = 46) => (s.length > n ? s.slice(0, n - 1).trimEnd() + "…" : s);
const lc = (s: string) => (s ? s.charAt(0).toLowerCase() + s.slice(1) : s);
function joinAnd(items: string[]): string {
  if (items.length <= 1) return items[0] ?? "";
  if (items.length === 2) return `${items[0]} and ${items[1]}`;
  return `${items.slice(0, -1).join(", ")}, and ${items[items.length - 1]}`;
}

function ramp(t: number): string {
  const a = [238, 236, 228];
  const b = [180, 83, 9];
  const c = a.map((x, i) => Math.round(x + (b[i] - x) * Math.max(0, Math.min(1, t))));
  return `rgb(${c[0]}, ${c[1]}, ${c[2]})`;
}

// Novel-policy kinds get distinct colors so you can tell a "rare authority"
// (few states regulate it at all) from an "unusual value" (a rare answer to a
// common question) at a glance — at rest, when selected, and on the map.
const KIND_STYLE: Record<NovelPolicy["kind"], { chip: string; active: string; tail: string; dot: string; fill: string }> = {
  coverage: {
    chip: "border-amber-600/50 bg-amber-50/50 hover:bg-amber-100/70",
    active: "border-amber-700 bg-amber-700 text-white",
    tail: "text-amber-100",
    dot: "bg-amber-600",
    fill: "rgb(180, 83, 9)",
  },
  value: {
    chip: "border-sky-600/50 bg-sky-50/50 hover:bg-sky-100/70",
    active: "border-sky-700 bg-sky-700 text-white",
    tail: "text-sky-100",
    dot: "bg-sky-600",
    fill: "rgb(3, 105, 161)",
  },
};

const SPREAD_VERB: Record<string, string> = {
  wide: "vary widely",
  moderate: "vary moderately",
  narrow: "are broadly similar",
};

export function SimilarityView({ professionId }: { professionId: string }) {
  const [data, setData] = useState<ProfileAnalysis | null>(null);
  const [missing, setMissing] = useState(false);
  // Novel-policies rarity bar (#50): K = max # states a policy may be held by.
  const [novelK, setNovelK] = useState(1);
  const [selected, setSelected] = useState<NovelPolicy | null>(null);

  useEffect(() => {
    setData(null);
    setMissing(false);
    setSelected(null);
    fetch(`/data/analysis/${encodeURIComponent(professionId)}.json`)
      .then((r) => (r.status === 404 ? (setMissing(true), null) : r.ok ? r.json() : null))
      .then((d: ProfileAnalysis | null) => {
        if (!d) return;
        setData(d);
        // Default the rarity bar to the lowest K that surfaces at least one policy
        // (K=1 when a unique policy exists, else the next-lowest available).
        const ns = (d.novel_policies ?? []).map((p) => p.n_states);
        setNovelK(ns.length ? Math.min(...ns) : 1);
      })
      .catch(() => setMissing(true));
  }, [professionId]);

  const distRange = useMemo(() => {
    if (!data) return [0, 1] as const;
    const vals = Object.values(data.distinctiveness);
    return vals.length ? ([Math.min(...vals), Math.max(...vals)] as const) : ([0, 1] as const);
  }, [data]);

  // Novel policies at or below the current rarity threshold, rarest first.
  const novel = useMemo(
    () => (data?.novel_policies ?? []).filter((p) => p.n_states <= novelK),
    [data, novelK],
  );

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

  // When a novel policy is selected, the map switches to "which states have this":
  // the policy's states light up, everything else goes gray.
  const selectedStates = selected ? new Set(selected.states) : null;
  const fillFor = (st: string) => {
    if (selected && selectedStates)
      return selectedStates.has(st) ? KIND_STYLE[selected.kind].fill : NO_DATA_FILL;
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

  // Map tooltip: the per-policy view when one is selected, else the usual profile.
  const mapTooltip = selected
    ? (st: string) =>
        selectedStates!.has(st) ? (
          <div className="w-72 space-y-1 text-xs">
            <div>
              <span className="text-sm font-medium">{st}</span> — {selected.label}
            </div>
            {selected.quote && <div className="text-muted-foreground">“{selected.quote}”</div>}
          </div>
        ) : null
    : renderTooltip;

  const coreLabels = data.core_fields.map(fieldLabel);
  const drivers = ls.drivers.slice(0, 3).map((d) => fieldLabel(d.field));
  const mostDistinct = Object.keys(data.distinctiveness).filter((s) => !lowConf(s)).slice(0, 5);
  const spreadVerb = SPREAD_VERB[ls.spread_label] ?? "vary";
  const driverList = joinAnd(drivers.map(lc));
  const driverTail =
    ls.spread_label === "narrow"
      ? `, with the most variation on ${driverList}`
      : `, differing most on ${driverList}`;

  // Group novel policies by their state set, so policies shared by the same
  // states cluster under one set of state badges (#50). Rarest sets first, then
  // the biggest clusters.
  const novelGroups = (() => {
    const m = new Map<string, NovelPolicy[]>();
    for (const p of novel) {
      const key = p.states.join(",");
      const arr = m.get(key);
      if (arr) arr.push(p);
      else m.set(key, [p]);
    }
    return [...m.values()].sort(
      (a, b) =>
        a[0].n_states - b[0].n_states ||
        b.length - a.length ||
        a[0].states[0].localeCompare(b[0].states[0]),
    );
  })();

  return (
    <div className="max-w-4xl space-y-6">
      {/* Lead with the insight. */}
      <p className="text-[15px] leading-relaxed">
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
          <p className="text-sm leading-relaxed">{data.notes["UT"]}</p>
          <div className="grid gap-x-12 gap-y-4 text-sm sm:grid-cols-2">{profileLists("UT", 99, 99)}</div>
        </div>
      )}

      {/* Novel policies — rarity bar (#50). Pick a policy to map who has it. */}
      {data.novel_policies.length > 0 && (
        <div className="border-t pt-5">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <p className="text-sm font-medium">Novel policies</p>
            <label className="flex items-center gap-2 text-xs text-muted-foreground">
              held by at most
              <input
                type="range"
                min={1}
                max={NOVEL_MAX_K}
                value={novelK}
                onChange={(e) => {
                  setNovelK(Number(e.target.value));
                  setSelected(null);
                }}
                className="h-1 w-32 cursor-pointer accent-amber-700"
              />
              <span className="tabular-nums text-foreground">{novelK}</span> state{novelK > 1 ? "s" : ""}
            </label>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">
            Rules and authorities almost no state has. Click one to map the states that do.
          </p>
          <div className="mb-3 mt-1.5 flex items-center gap-3 text-xs text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <span className="inline-block h-2 w-2 rounded-full bg-amber-600" /> rare authority — few states regulate it
            </span>
            <span className="flex items-center gap-1.5">
              <span className="inline-block h-2 w-2 rounded-full bg-sky-600" /> unusual value — rare answer to a common one
            </span>
          </div>
          {novel.length === 0 ? (
            <p className="text-xs text-muted-foreground">Nothing this rare — widen the bar.</p>
          ) : (
            <TooltipProvider delay={150}>
              <div className="space-y-1.5">
                {novelGroups.map((pols) => (
                  <div key={pols[0].states.join(",")} className="flex items-start gap-2">
                    <div className="flex w-20 shrink-0 flex-wrap gap-1 pt-1.5">
                      {pols[0].states.map((s) => (
                        <span
                          key={s}
                          className="rounded bg-muted px-1.5 py-0.5 text-[11px] font-medium text-foreground/70"
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                    <div className="flex flex-1 flex-wrap gap-1.5">
                      {pols.map((p, i) => {
                        const active = selected === p;
                        const k = KIND_STYLE[p.kind];
                        const key = `${p.field}-${p.value ?? ""}-${i}`;
                        const button = (
                          <button
                            key={key}
                            onClick={() => setSelected(active ? null : p)}
                            className={`rounded-full border px-2.5 py-1 text-xs transition-colors ${active ? k.active : k.chip}`}
                          >
                            {clip(p.label)}
                          </button>
                        );
                        // Only clipped chips need a hover to reveal the full label.
                        if (p.label.length <= 46) return button;
                        return (
                          <Tooltip key={key}>
                            <TooltipTrigger render={button} />
                            <TooltipContent className="max-w-sm">{p.label}</TooltipContent>
                          </Tooltip>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </TooltipProvider>
          )}
          {selected && (
            <div className="mt-3 rounded-md border bg-muted/30 p-3 text-xs">
              <div className="font-medium">{selected.label}</div>
              <div className="mt-0.5 text-muted-foreground">
                {selected.kind === "coverage" ? "Regulated by " : "This value held by "}
                {selected.n_states === 1 ? "only " : ""}
                {selected.states.join(", ")}
              </div>
              {selected.quote && (
                <div
                  className="mt-1.5 border-l-2 pl-2 text-muted-foreground"
                  style={{ borderColor: KIND_STYLE[selected.kind].fill }}
                >
                  “{selected.quote}”{selected.citation ? ` — ${selected.citation}` : ""}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* The landscape map — recolors to the selected policy's states when one is picked. */}
      <div className="border-t pt-5">
        <p className="mb-3 text-xs text-muted-foreground">
          {selected ? (
            <>
              States with <span className="font-medium text-foreground">{selected.label}</span> —{" "}
              {selected.n_states} of 50.{" "}
              <button onClick={() => setSelected(null)} className="underline hover:text-foreground">
                back to distinctiveness
              </button>
            </>
          ) : (
            <>How distinctive each state is — hover any state for where it agrees and what&apos;s unusual.</>
          )}
        </p>
        <UsMap fillFor={fillFor} renderTooltip={mapTooltip} bare />
        {selected ? (
          <div className="mt-3 flex items-center gap-2 text-xs text-muted-foreground">
            <span className="inline-block h-2 w-3 rounded" style={{ background: KIND_STYLE[selected.kind].fill }} /> has this policy
            <span className="ml-2 flex items-center gap-1">
              <span className="inline-block h-2 w-3 rounded" style={{ background: NO_DATA_FILL }} /> does not
            </span>
          </div>
        ) : (
          <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
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
        )}
      </div>
    </div>
  );
}

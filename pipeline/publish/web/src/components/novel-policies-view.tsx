"use client";

// "What only a few states do" — the slide-8 view (POLICY INNOVATIONS & ODDITIES).
// A field-category filter bar + rarity slider over a list of rare policies sorted
// rarest-first; each card opens the slide-4 beat-by-beat walkthrough of how it was
// surfaced, led by a plain-English summary of what the finding actually is.
// Self-fetches /data/analysis/<prof>.json (same source as the Compare tab).

import { useEffect, useMemo, useState, type ReactNode } from "react";
import type { ProfileAnalysis, NovelPolicy } from "@/lib/types";

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
const val = (v: string) => {
  if (v === "true") return "yes";
  if (v === "false") return "no";
  // Whole-number values come through as "7.0" — show them as "7".
  const n = Number(v);
  if (v.trim() !== "" && Number.isInteger(n)) return String(n);
  return v.replace(/_/g, " ");
};

// Match KIND_STYLE.fill in similarity-view: amber = rare authority, sky = unusual value.
const KIND_FILL: Record<NovelPolicy["kind"], string> = {
  coverage: "rgb(180, 83, 9)",
  value: "rgb(3, 105, 161)",
};

// The 7 core scorecard categories (slide 8/9 filter pills). Every novel-policy
// field maps to one; profession_specific.* clinical fields are all Scope.
const NOVEL_CATEGORIES = [
  "Degree", "Experience", "Discipline", "Scope", "Regulation", "Authority", "License",
] as const;

function fieldCategory(field: string): string {
  const f = field.toLowerCase();
  if (f.includes("regulatory_model") || f.includes("uorf")) return "Regulation";
  if (f.includes("issuing_authority") || f.includes("regulatory_authority") || f.includes("advisory_board"))
    return "Authority";
  if (f.includes("disciplin")) return "Discipline";
  if (f.includes("education") || f.includes("degree")) return "Degree";
  if (f.includes("post_degree") || f.includes("experience") || f.includes("internship")) return "Experience";
  if (f.includes("license") || f.includes("tiered")) return "License";
  return "Scope";
}

const CAT_STYLE: Record<string, string> = {
  Degree: "border-slate-300 text-slate-600",
  Experience: "border-teal-300 text-teal-700",
  Discipline: "border-rose-300 text-rose-700",
  Scope: "border-sky-300 text-sky-700",
  Regulation: "border-violet-300 text-violet-700",
  Authority: "border-amber-300 text-amber-700",
  License: "border-indigo-300 text-indigo-700",
};

// Restrictive/permissive direction (#52c) — the second filter axis beyond Field.
const DIRECTIONS = ["more_restrictive", "more_permissive", "neutral"] as const;
type DirKey = (typeof DIRECTIONS)[number];
const DIR_LABEL: Record<DirKey, string> = {
  more_restrictive: "More restrictive",
  more_permissive: "More permissive",
  neutral: "Neutral",
};
const DIR_STYLE: Record<DirKey, string> = {
  more_restrictive: "border-rose-300 text-rose-700",
  more_permissive: "border-emerald-300 text-emerald-700",
  neutral: "border-slate-300 text-slate-600",
};
const DIR_ACTIVE: Record<DirKey, string> = {
  more_restrictive: "border-rose-600 bg-rose-600 text-white",
  more_permissive: "border-emerald-600 bg-emerald-600 text-white",
  neutral: "border-slate-500 bg-slate-500 text-white",
};

// The short teaser on the card face.
function novelDescription(p: NovelPolicy, total: number): string {
  const lbl = fieldLabel(p.field);
  if (p.kind === "coverage")
    return `${lbl}: regulated by only ${p.n_states} of ${total} states.`;
  return `${lbl}: a rare value — ${p.n_states} of ${total} ${p.n_states === 1 ? "state has" : "states have"} it.`;
}

// A fuller plain-English sentence of what the finding IS, drawn from the statute
// context (the sample state, the extracted value, the rarity). Shown atop the
// walkthrough, before "How the AI surfaced this" (issue #52).
function novelSummary(p: NovelPolicy, total: number): string {
  const lbl = fieldLabel(p.field).toLowerCase();
  const where = p.sample_state ?? p.states[0];
  if (p.kind === "coverage") {
    const tail =
      p.n_states === 1
        ? `the only one of ${total} states to regulate it at all`
        : `one of just ${p.n_states} of ${total} states to regulate it at all`;
    return `${where} regulates ${lbl}${p.value != null ? `, here as ${val(p.value)}` : ""} — ${tail}.`;
  }
  const v = p.value != null ? `“${val(p.value)}”` : "this value";
  const tail =
    p.n_states === 1
      ? `the only one of ${total} states with that answer`
      : `one of just ${p.n_states} of ${total} states sharing it`;
  return `${where} answers ${lbl} with ${v} — ${tail}.`;
}

// The counterpoint to the rare value (#52): what most states do on this field —
// the dominant answer, or "usually unspecified" when most states are silent.
function majorityLine(p: NovelPolicy): string | null {
  const m = p.majority;
  if (!m) return null;
  // A field most states simply don't have at all (coverage-novelty).
  if (m.value == null || m.reported === 0)
    return m.unstated > 0
      ? `Most states (${m.unstated} of ${m.total}) don't address this at all.`
      : null;
  // A common field where silence outweighs the leading answer.
  if (m.unstated > m.n)
    return `Most states (${m.unstated} of ${m.total}) don't specify; among those that do, ${val(m.value)} leads (${m.n}).`;
  // A common field with a clear majority answer.
  return `Most states answer ${val(m.value)} (${m.n} of ${m.total})${m.unstated > 0 ? `; ${m.unstated} don't specify` : ""}.`;
}

// One step in the slide-4 "how the AI surfaced this" walkthrough.
function Beat({ n, title, color, children }: {
  n: number; title: string; color: string; children: ReactNode;
}) {
  return (
    <li className="flex gap-3">
      <span
        className="mt-px flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[11px] font-semibold text-white"
        style={{ background: color }}
      >
        {n}
      </span>
      <div className="min-w-0">
        <div className="font-medium text-foreground">{title}</div>
        <div className="mt-0.5 leading-relaxed text-muted-foreground">{children}</div>
      </div>
    </li>
  );
}

function Walkthrough({ p, total }: { p: NovelPolicy; total: number }) {
  const c = KIND_FILL[p.kind];
  const chip = "inline-block rounded bg-foreground/[0.06] px-1.5 py-0.5 font-medium text-foreground";
  return (
    <div className="border-t bg-muted/20 p-4 text-sm">
      {/* Plain-English summary of the finding, before the mechanics (#52). */}
      <p className="mb-2 leading-relaxed text-foreground">{novelSummary(p, total)}</p>
      {/* What most states do — the counterpoint (#52). */}
      {majorityLine(p) && (
        <p className="mb-3 leading-relaxed text-muted-foreground">
          <span className="font-medium text-foreground">Across states: </span>
          {majorityLine(p)}
        </p>
      )}
      <div className="mb-3 text-[15px] font-medium text-foreground">
        How the AI surfaced this — beat by beat
      </div>
      <ol className="space-y-3">
        <Beat n={1} title="Read statute" color={c}>
          {p.quote ? (
            <span className="italic">“{p.quote}”</span>
          ) : (
            <span className="italic">no verbatim quote was captured for this value</span>
          )}
        </Beat>
        <Beat n={2} title="Decide the field" color={c}>
          The same question recurs across states, so it&apos;s tracked as its own field:{" "}
          <span className={chip}>{fieldLabel(p.field)}</span>
        </Beat>
        <Beat n={3} title="Extract value" color={c}>
          <span className="font-medium text-foreground">{p.sample_state ?? p.states[0]}</span> →{" "}
          <span className={chip}>{p.value != null ? val(p.value) : "regulated"}</span>
          {p.citation ? (
            <> — quote &amp; citation kept attached (<span className="tabular-nums">{p.citation}</span>)</>
          ) : null}
        </Beat>
        <Beat n={4} title="Normalize with tags" color={c}>
          Placed on the shared scale as{" "}
          <span
            className="inline-block rounded px-1.5 py-0.5 font-medium text-white"
            style={{ background: c }}
          >
            {p.label}
          </span>
        </Beat>
        <Beat n={5} title="Group" color={c}>
          <span className="text-[15px] font-semibold tabular-nums text-foreground">{p.n_states}</span>{" "}
          {p.n_states === 1 ? "state" : "states"}{" "}
          {p.kind === "coverage" ? "regulate this at all" : "share this value"} —{" "}
          <span className="text-foreground">{p.states.join(", ")}</span>{" "}
          {p.n_states === 1 ? "is the only one." : "among them."}
        </Beat>
      </ol>
    </div>
  );
}

export function NovelPoliciesView({ professionId }: { professionId: string }) {
  const [data, setData] = useState<ProfileAnalysis | null>(null);
  const [missing, setMissing] = useState(false);
  const [cat, setCat] = useState<string | null>(null);
  const [dir, setDir] = useState<DirKey | null>(null);
  const [selected, setSelected] = useState<NovelPolicy | null>(null);
  // Rarity bar (moved here from the Compare tab, #52): show policies held by at
  // most K states. Defaults to the max so the tab opens on the full list.
  const [maxK, setMaxK] = useState(1);
  const [novelK, setNovelK] = useState(1);

  useEffect(() => {
    setData(null);
    setMissing(false);
    setSelected(null);
    setCat(null);
    setDir(null);
    fetch(`/data/analysis/${encodeURIComponent(professionId)}.json`)
      .then((r) => (r.status === 404 ? (setMissing(true), null) : r.ok ? r.json() : null))
      .then((d: ProfileAnalysis | null) => {
        if (!d) return;
        setData(d);
        // Default the bar to the highest rarity present, so the tab opens showing
        // everything and the slider only ever narrows toward the rarest.
        const ns = (d.novel_policies ?? []).map((p) => p.n_states);
        const top = ns.length ? Math.max(...ns) : 1;
        setMaxK(top);
        setNovelK(top);
      })
      .catch(() => setMissing(true));
  }, [professionId]);

  const list = useMemo(() => {
    let all = (data?.novel_policies ?? []).filter((p) => p.n_states <= novelK);
    if (cat) all = all.filter((p) => fieldCategory(p.field) === cat);
    if (dir) all = all.filter((p) => p.direction === dir);
    return all.sort((a, b) => a.n_states - b.n_states || a.label.localeCompare(b.label));
  }, [data, cat, dir, novelK]);

  if (missing)
    return <p className="text-[15px] text-muted-foreground">No comparison data for this profession yet.</p>;
  if (!data) return <p className="text-[15px] text-muted-foreground">Loading…</p>;
  if (data.novel_policies.length === 0)
    return <p className="text-[15px] text-muted-foreground">No novel policies surfaced for this profession.</p>;

  const total = data.states.length;
  // Category counts respect the current rarity threshold so the pill numbers
  // always match what the slider is showing.
  const inK = data.novel_policies.filter((p) => p.n_states <= novelK);
  const catCounts = new Map<string, number>();
  for (const p of inK) {
    const k = fieldCategory(p.field);
    catCounts.set(k, (catCounts.get(k) ?? 0) + 1);
  }
  // Direction counts (#52c) — only render the axis if the data carries directions.
  const dirCounts = new Map<DirKey, number>();
  for (const p of inK) if (p.direction) dirCounts.set(p.direction, (dirCounts.get(p.direction) ?? 0) + 1);
  const nDirected = [...dirCounts.values()].reduce((a, b) => a + b, 0);

  return (
    <div className="max-w-3xl">
      <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
        Policy innovations &amp; oddities
      </p>
      <h2 className="mt-1 text-xl font-semibold">What only a few states do</h2>
      <p className="mt-1 text-[15px] leading-relaxed text-muted-foreground">
        Rare values across every tracked field — ideas to benchmark, and outliers to scrutinize.
        Sorted by how few states share each one. Click one for the step-by-step.
      </p>

      {/* Rarity slider — held by at most K states (moved from the Compare tab, #52). */}
      {maxK > 1 && (
        <label className="mt-4 flex items-center gap-2 text-sm text-muted-foreground">
          held by at most
          <input
            type="range"
            min={1}
            max={maxK}
            value={novelK}
            onChange={(e) => {
              setNovelK(Number(e.target.value));
              setSelected(null);
              setCat(null);
              setDir(null);
            }}
            className="h-1 w-40 cursor-pointer accent-foreground"
          />
          <span className="tabular-nums text-foreground">{novelK}</span> state{novelK > 1 ? "s" : ""}
        </label>
      )}

      {/* Field-category filter pills. */}
      <div className="mt-3 flex flex-wrap gap-1.5">
        {(["All fields", ...NOVEL_CATEGORIES] as const).map((c) => {
          const isAll = c === "All fields";
          const active = isAll ? cat === null : cat === c;
          const count = isAll ? inK.length : catCounts.get(c) ?? 0;
          if (!isAll && count === 0) return null;
          return (
            <button
              key={c}
              onClick={() => {
                setCat(isAll ? null : c);
                setSelected(null);
              }}
              className={`rounded-full border px-3 py-1 text-sm transition-colors ${
                active
                  ? "border-foreground bg-foreground text-background"
                  : "border-border bg-background text-muted-foreground hover:bg-muted"
              }`}
            >
              {c}
              <span className="ml-1.5 tabular-nums opacity-60">{count}</span>
            </button>
          );
        })}
      </div>

      {/* Direction filter — restrictive vs permissive (#52c). The "what kind"
          axis beyond Field. Hidden if the data carries no directions. */}
      {nDirected > 0 && (
        <div className="mt-2 flex flex-wrap items-center gap-1.5">
          <span className="mr-0.5 text-xs text-muted-foreground">Direction:</span>
          <button
            onClick={() => {
              setDir(null);
              setSelected(null);
            }}
            className={`rounded-full border px-3 py-1 text-sm transition-colors ${
              dir === null
                ? "border-foreground bg-foreground text-background"
                : "border-border bg-background text-muted-foreground hover:bg-muted"
            }`}
          >
            Any
            <span className="ml-1.5 tabular-nums opacity-60">{nDirected}</span>
          </button>
          {DIRECTIONS.map((d) => {
            const count = dirCounts.get(d) ?? 0;
            if (count === 0) return null;
            const active = dir === d;
            return (
              <button
                key={d}
                onClick={() => {
                  setDir(active ? null : d);
                  setSelected(null);
                }}
                className={`rounded-full border px-3 py-1 text-sm transition-colors ${
                  active ? DIR_ACTIVE[d] : `${DIR_STYLE[d]} bg-background hover:bg-muted`
                }`}
              >
                {DIR_LABEL[d]}
                <span className="ml-1.5 tabular-nums opacity-60">{count}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* Rare-policy cards, rarest first. */}
      <div className="mt-4 space-y-2">
        {list.length === 0 ? (
          <p className="text-sm text-muted-foreground">Nothing this rare — widen the bar.</p>
        ) : (
          list.map((p, i) => {
            const active = selected === p;
            const fc = fieldCategory(p.field);
            return (
              <div
                key={`${p.field}-${p.value ?? ""}-${i}`}
                className={`overflow-hidden rounded-lg border transition-colors ${
                  active ? "border-foreground/40 bg-muted/30" : "bg-background"
                }`}
              >
                <button
                  onClick={() => setSelected(active ? null : p)}
                  className="w-full p-3 text-left hover:bg-muted/20"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-2">
                      <span
                        className="mt-1 inline-block h-2 w-2 shrink-0 rounded-full"
                        style={{ background: KIND_FILL[p.kind] }}
                      />
                      <span className="text-[15px] font-medium leading-snug">{p.label}</span>
                    </div>
                    <span className="shrink-0 whitespace-nowrap text-sm tabular-nums text-muted-foreground">
                      {p.n_states}/{total} states
                    </span>
                  </div>
                  <p className="mt-1 pl-4 text-sm text-muted-foreground">{novelDescription(p, total)}</p>
                  <div className="mt-2 flex items-center justify-between gap-2 pl-4">
                    <div className="flex flex-wrap gap-1">
                      {p.states.map((s) => (
                        <span
                          key={s}
                          className="rounded bg-muted px-1.5 py-0.5 text-xs font-medium text-foreground/70"
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                    <div className="flex shrink-0 items-center gap-1">
                      {p.direction && p.direction !== "neutral" && (
                        <span className={`rounded-full border px-2 py-0.5 text-xs ${DIR_STYLE[p.direction]}`}>
                          {DIR_LABEL[p.direction]}
                        </span>
                      )}
                      <span className={`rounded-full border px-2 py-0.5 text-xs ${CAT_STYLE[fc]}`}>
                        {fc}
                      </span>
                    </div>
                  </div>
                </button>
                {active && <Walkthrough p={p} total={total} />}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

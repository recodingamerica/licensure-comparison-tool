"use client";

// "What only a few states do" — the slide-8 view (POLICY INNOVATIONS & ODDITIES).
// A field-category filter bar over a list of rare policies sorted rarest-first;
// each card opens the slide-4 beat-by-beat walkthrough of how it was surfaced.
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
const val = (v: string) => (v === "true" ? "yes" : v === "false" ? "no" : v.replace(/_/g, " "));

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

function novelDescription(p: NovelPolicy, total: number): string {
  const lbl = fieldLabel(p.field);
  if (p.kind === "coverage")
    return `${lbl}: regulated by only ${p.n_states} of ${total} states.`;
  return `${lbl}: a rare value — ${p.n_states} of ${total} ${p.n_states === 1 ? "state has" : "states have"} it.`;
}

// One step in the slide-4 "how the AI surfaced this" walkthrough.
function Beat({ n, title, color, children }: {
  n: number; title: string; color: string; children: ReactNode;
}) {
  return (
    <li className="flex gap-3">
      <span
        className="mt-px flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[10px] font-semibold text-white"
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

function Walkthrough({ p }: { p: NovelPolicy }) {
  const c = KIND_FILL[p.kind];
  const chip = "inline-block rounded bg-foreground/[0.06] px-1.5 py-0.5 font-medium text-foreground";
  return (
    <div className="border-t bg-muted/20 p-4 text-xs">
      <div className="mb-3 text-[13px] font-medium text-foreground">
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
          <span className="text-sm font-semibold tabular-nums text-foreground">{p.n_states}</span>{" "}
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
  const [selected, setSelected] = useState<NovelPolicy | null>(null);

  useEffect(() => {
    setData(null);
    setMissing(false);
    setSelected(null);
    setCat(null);
    fetch(`/data/analysis/${encodeURIComponent(professionId)}.json`)
      .then((r) => (r.status === 404 ? (setMissing(true), null) : r.ok ? r.json() : null))
      .then((d: ProfileAnalysis | null) => {
        if (d) setData(d);
      })
      .catch(() => setMissing(true));
  }, [professionId]);

  const list = useMemo(() => {
    const all = (data?.novel_policies ?? []).slice();
    const filtered = cat ? all.filter((p) => fieldCategory(p.field) === cat) : all;
    return filtered.sort((a, b) => a.n_states - b.n_states || a.label.localeCompare(b.label));
  }, [data, cat]);

  if (missing)
    return <p className="text-sm text-muted-foreground">No comparison data for this profession yet.</p>;
  if (!data) return <p className="text-sm text-muted-foreground">Loading…</p>;
  if (data.novel_policies.length === 0)
    return <p className="text-sm text-muted-foreground">No novel policies surfaced for this profession.</p>;

  const total = data.states.length;
  const catCounts = new Map<string, number>();
  for (const p of data.novel_policies) {
    const k = fieldCategory(p.field);
    catCounts.set(k, (catCounts.get(k) ?? 0) + 1);
  }

  return (
    <div className="max-w-3xl">
      <p className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
        Policy innovations &amp; oddities
      </p>
      <h2 className="mt-1 text-lg font-semibold">What only a few states do</h2>
      <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
        Rare values across every tracked field — ideas to benchmark, and outliers to scrutinize.
        Sorted by how few states share each one. Click one for the step-by-step.
      </p>

      {/* Field-category filter pills. */}
      <div className="mt-4 flex flex-wrap gap-1.5">
        {(["All fields", ...NOVEL_CATEGORIES] as const).map((c) => {
          const isAll = c === "All fields";
          const active = isAll ? cat === null : cat === c;
          const count = isAll ? data.novel_policies.length : catCounts.get(c) ?? 0;
          if (!isAll && count === 0) return null;
          return (
            <button
              key={c}
              onClick={() => {
                setCat(isAll ? null : c);
                setSelected(null);
              }}
              className={`rounded-full border px-3 py-1 text-xs transition-colors ${
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

      {/* Rare-policy cards, rarest first. */}
      <div className="mt-4 space-y-2">
        {list.map((p, i) => {
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
                    <span className="text-sm font-medium leading-snug">{p.label}</span>
                  </div>
                  <span className="shrink-0 whitespace-nowrap text-xs tabular-nums text-muted-foreground">
                    {p.n_states}/{total} states
                  </span>
                </div>
                <p className="mt-1 pl-4 text-xs text-muted-foreground">{novelDescription(p, total)}</p>
                <div className="mt-2 flex items-center justify-between gap-2 pl-4">
                  <div className="flex flex-wrap gap-1">
                    {p.states.map((s) => (
                      <span
                        key={s}
                        className="rounded bg-muted px-1.5 py-0.5 text-[11px] font-medium text-foreground/70"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                  <span className={`shrink-0 rounded-full border px-2 py-0.5 text-[11px] ${CAT_STYLE[fc]}`}>
                    {fc}
                  </span>
                </div>
              </button>
              {active && <Walkthrough p={p} />}
            </div>
          );
        })}
      </div>
    </div>
  );
}

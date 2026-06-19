"use client";

// Compare tab — "what is each state like, and where is it weird."
// Self-fetches /data/analysis/<prof>.json (produced by pipeline.analyze.similarity
// + utah_note). Focal state defaults to UT; the prose note is Utah-only by design.

import { useEffect, useMemo, useState } from "react";
import type { ProfileAnalysis } from "@/lib/types";

// Dotted field name -> short human label. "profession_specific.surgery_prohibited"
// -> "Surgery prohibited"; "licensure.education.degree_level" -> "Degree level".
function fieldLabel(f: string): string {
  const leaf = f.split(".").pop() ?? f;
  const s = leaf.replace(/_/g, " ");
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function val(v: string): string {
  if (v === "true") return "yes";
  if (v === "false") return "no";
  return v;
}

function Label({ children }: { children: React.ReactNode }) {
  return (
    <div className="text-[11px] font-mono uppercase tracking-widest text-muted-foreground mb-2">
      {children}
    </div>
  );
}

export function SimilarityView({ professionId }: { professionId: string }) {
  const [data, setData] = useState<ProfileAnalysis | null>(null);
  const [missing, setMissing] = useState(false);
  const [focus, setFocus] = useState("UT");

  useEffect(() => {
    setData(null);
    setMissing(false);
    fetch(`/data/analysis/${encodeURIComponent(professionId)}.json`)
      .then((r) => {
        if (r.status === 404) {
          setMissing(true);
          return null;
        }
        return r.ok ? r.json() : null;
      })
      .then((d: ProfileAnalysis | null) => d && setData(d))
      .catch(() => setMissing(true));
  }, [professionId]);

  // Keep focus valid for this profession; prefer UT.
  useEffect(() => {
    if (data && !data.states.includes(focus)) {
      setFocus(data.states.includes("UT") ? "UT" : data.states[0]);
    }
  }, [data, focus]);

  const distinctRank = useMemo(() => {
    if (!data) return null;
    const ordered = Object.keys(data.distinctiveness); // already sorted desc
    return { rank: ordered.indexOf(focus) + 1, total: ordered.length };
  }, [data, focus]);

  if (missing)
    return (
      <p className="text-sm text-muted-foreground">
        No comparison data for this profession yet — run{" "}
        <code className="text-xs">pipeline.analyze.similarity --json</code> +{" "}
        <code className="text-xs">publish_analysis</code>.
      </p>
    );
  if (!data) return <p className="text-sm text-muted-foreground">Loading…</p>;

  const neighbors = data.neighbors[focus] ?? [];
  const kind = data.kind_outliers.filter((o) => o.state === focus);
  const stringency = data.stringency_outliers.filter((o) => o.state === focus);
  const noteShown = focus === "UT" && data.utah_note;

  return (
    <div className="space-y-6">
      {/* Focal-state selector */}
      <div className="flex items-center gap-2 text-sm">
        <span className="text-muted-foreground">Compare</span>
        <select
          value={focus}
          onChange={(e) => setFocus(e.target.value)}
          className="rounded border bg-background px-2 py-1 text-sm font-mono"
        >
          {data.states.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <span className="text-muted-foreground">
          to the other {data.states.length - 1} states ({data.n_discriminating_fields} fields that vary)
        </span>
      </div>

      {/* Utah-only prose summary */}
      {noteShown && (
        <div className="rounded-md border bg-muted/30 px-4 py-3 text-sm leading-relaxed">
          {data.utah_note}
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        {/* Most similar */}
        <section>
          <Label>{focus} is most like</Label>
          {neighbors.length === 0 ? (
            <p className="text-sm text-muted-foreground">Not enough comparable fields.</p>
          ) : (
            <ul className="space-y-1">
              {neighbors.slice(0, 5).map((nb) => (
                <li key={nb.state} className="flex items-center gap-2 text-sm">
                  <span className="font-mono w-7">{nb.state}</span>
                  <span className="inline-block h-1.5 rounded bg-foreground/70" style={{ width: `${nb.sim * 120}px` }} />
                  <span className="text-muted-foreground tabular-nums">
                    {Math.round(nb.sim * 100)}%
                  </span>
                  <span className="text-[10px] text-muted-foreground">({nb.n} fields)</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Distinctiveness leaderboard */}
        <section>
          <Label>Most distinctive regimes overall</Label>
          <ul className="space-y-1">
            {Object.entries(data.distinctiveness)
              .slice(0, 6)
              .map(([st, score]) => (
                <li
                  key={st}
                  className={"flex items-center gap-2 text-sm " + (st === focus ? "font-semibold" : "")}
                >
                  <span className="font-mono w-7">{st}</span>
                  <span className="inline-block h-1.5 rounded bg-amber-500/70" style={{ width: `${score * 220}px` }} />
                  <span className="text-muted-foreground tabular-nums">{score.toFixed(2)}</span>
                </li>
              ))}
          </ul>
          {distinctRank && (
            <p className="mt-2 text-xs text-muted-foreground">
              {focus} ranks #{distinctRank.rank} of {distinctRank.total} on overall distinctiveness.
            </p>
          )}
        </section>
      </div>

      {/* Where this state is weird */}
      <section>
        <Label>Where {focus} is unusual</Label>
        {kind.length === 0 && stringency.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Nothing categorically rare or far from the norm — {focus} is typical here.
          </p>
        ) : (
          <div className="space-y-2">
            {kind.slice(0, 8).map((o, i) => (
              <div key={"k" + i} className="flex flex-wrap items-baseline gap-x-2 text-sm">
                <span className="font-medium">{fieldLabel(o.field)}</span>
                <span className="font-mono text-foreground">= {val(o.value)}</span>
                <span className="text-muted-foreground">
                  — categorically rare: only {o.n_states} of {o.total} states
                </span>
              </div>
            ))}
            {stringency
              .filter((s) => !kind.some((k) => k.field === s.field)) // avoid dupe lines
              .slice(0, 8)
              .map((o, i) => (
                <div key={"s" + i} className="flex flex-wrap items-baseline gap-x-2 text-sm">
                  <span className="font-medium">{fieldLabel(o.field)}</span>
                  <span className="font-mono text-foreground">= {val(o.value)}</span>
                  <span className="text-muted-foreground">
                    — {o.direction.includes("strict") ? "much stricter" : "much looser"} than peers
                  </span>
                </div>
              ))}
          </div>
        )}
      </section>
    </div>
  );
}

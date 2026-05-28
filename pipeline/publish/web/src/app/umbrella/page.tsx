"use client";

// /umbrella  —  cross-state overview of umbrella-scoping coverage.
//
// "Umbrella" = cross-cutting statutes (board composition, definitions,
// discipline) that apply to many regulated professions rather than one
// practice act. For every state we have data for, this view shows how many
// umbrella sections we've scoped and which professions they cover, so it's
// easy to see at a glance what we have for each (state, profession) pair.
// Click a state to drill into its umbrella sections.

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";

type Coverage = { universal: number; enumerated: number; undetermined: number };
type IndexState = {
  state: string;
  section_count: number;
  coverage: Coverage;
  profession_count: number;
  state_regulates: string[];
};
type IndexPayload = {
  states: IndexState[];
  professions: string[];
  matrix: Record<string, Record<string, number>>;
};

function fmtProf(p: string) {
  return p.replace(/_/g, " ");
}

export default function UmbrellaIndexPage() {
  const [data, setData] = useState<IndexPayload | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [profFilter, setProfFilter] = useState<string>("");

  useEffect(() => {
    fetch("/data/umbrella/_index.json")
      .then((r) => {
        if (!r.ok) throw new Error("missing /data/umbrella/_index.json — run build_umbrella_browse");
        return r.json();
      })
      .then(setData)
      .catch((e) => setErr(String(e)));
  }, []);

  const rows = useMemo(() => {
    if (!data) return [];
    return [...data.states].sort((a, b) => {
      if (profFilter) {
        return (data.matrix[b.state]?.[profFilter] ?? 0) - (data.matrix[a.state]?.[profFilter] ?? 0);
      }
      return b.section_count - a.section_count;
    });
  }, [data, profFilter]);

  if (err) {
    return (
      <main className="mx-auto max-w-3xl px-6 py-10">
        <p className="text-sm text-destructive">{err}</p>
      </main>
    );
  }
  if (!data) {
    return <main className="mx-auto max-w-3xl px-6 py-10 text-sm text-muted-foreground">Loading…</main>;
  }

  const totals = data.states.reduce(
    (acc, s) => {
      acc.total += s.section_count;
      acc.uni += s.coverage.universal;
      acc.enu += s.coverage.enumerated;
      acc.und += s.coverage.undetermined;
      return acc;
    },
    { total: 0, uni: 0, enu: 0, und: 0 },
  );

  return (
    <main className="mx-auto max-w-6xl px-6 py-10 space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">Umbrella scope — coverage by state</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Cross-cutting statutes (definitions, board composition, discipline) that govern many professions
          rather than one practice act. For each state we&apos;ve auto-classified each umbrella section by which
          professions it applies to. Click a state for the full list of sections.
        </p>
        <p className="mt-2 text-sm">
          {data.states.length} states · {totals.total.toLocaleString()} sections ·{" "}
          <span className="text-foreground">{(totals.uni + totals.enu).toLocaleString()} classified</span>{" "}
          ({totals.uni.toLocaleString()} universal, {totals.enu.toLocaleString()} enumerated) ·{" "}
          <span className="text-muted-foreground">{totals.und.toLocaleString()} unclassified</span>
        </p>
      </header>

      <div className="flex items-center gap-3 text-sm">
        <label htmlFor="prof" className="text-muted-foreground">
          Sort by coverage for profession:
        </label>
        <select
          id="prof"
          value={profFilter}
          onChange={(e) => setProfFilter(e.target.value)}
          className="rounded border bg-background px-2 py-1"
        >
          <option value="">(total sections)</option>
          {data.professions.map((p) => (
            <option key={p} value={p}>{fmtProf(p)}</option>
          ))}
        </select>
      </div>

      <table className="w-full text-sm">
        <thead className="text-left text-muted-foreground">
          <tr className="border-b">
            <th className="py-2 pr-4">State</th>
            <th className="py-2 pr-4 text-right">Sections</th>
            <th className="py-2 pr-4 text-right">Universal</th>
            <th className="py-2 pr-4 text-right">Enumerated</th>
            <th className="py-2 pr-4 text-right">Unclassified</th>
            <th className="py-2 pr-4 text-right">
              {profFilter ? `${fmtProf(profFilter)} sections` : "Top professions covered"}
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((s) => {
            const m = data.matrix[s.state] ?? {};
            const top = Object.entries(m).sort((a, b) => b[1] - a[1]).slice(0, 5);
            return (
              <tr key={s.state} className="border-b hover:bg-muted/40">
                <td className="py-2 pr-4 font-medium">
                  <Link className="underline-offset-2 hover:underline" href={`/umbrella/${s.state}`}>
                    {s.state}
                  </Link>
                </td>
                <td className="py-2 pr-4 text-right tabular-nums">{s.section_count}</td>
                <td className="py-2 pr-4 text-right tabular-nums">{s.coverage.universal}</td>
                <td className="py-2 pr-4 text-right tabular-nums">{s.coverage.enumerated}</td>
                <td className="py-2 pr-4 text-right tabular-nums text-muted-foreground">
                  {s.coverage.undetermined}
                </td>
                <td className="py-2 pr-4 text-right">
                  {profFilter ? (
                    <span className="tabular-nums">{m[profFilter] ?? 0}</span>
                  ) : (
                    <span className="inline-flex flex-wrap justify-end gap-1">
                      {top.length === 0 && (
                        <span className="text-xs text-muted-foreground">none yet</span>
                      )}
                      {top.map(([p, n]) => (
                        <Badge key={p} variant="secondary" className="font-normal">
                          {fmtProf(p)} {n}
                        </Badge>
                      ))}
                    </span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </main>
  );
}

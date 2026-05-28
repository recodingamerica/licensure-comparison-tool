"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import type { ProfessionsListEntry } from "@/lib/types";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { professionStyle, useProfessionMeta } from "@/lib/profession-colors";

type StatesListEntry = {
  state: string;
  sections: number;
  professions: string[];
};

// Count of universal (cross-profession) columns in the /profile table.
// Tracks the non-discovered ColDefs defined in profile-view.tsx::
// buildColumnDefs. Update if columns are added/removed there. The home-card
// breakdown reads "{discovered} profession-specific + {universal} universal
// fields" — Atharv flagged the dropdown's 70+ vs home's ~29 as confusing
// (issue #13); the breakdown makes it intuitive.
const UNIVERSAL_FIELDS_COUNT = 44;

export default function HomePage() {
  const [mode, setMode] = useState<"profession" | "state">("profession");
  const [professions, setProfessions] = useState<ProfessionsListEntry[] | null>(null);
  const [states, setStates] = useState<StatesListEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Triggers a re-render once /professions.json loads so the colored dots
  // appear instead of the neutral fallback.
  useProfessionMeta();

  useEffect(() => {
    Promise.all([
      fetch("/professions.json").then((r) => (r.ok ? r.json() : [])),
      fetch("/states.json").then((r) => (r.ok ? r.json() : [])),
    ])
      .then(([p, s]) => {
        const pp = (p as ProfessionsListEntry[]).sort(
          (a, b) => (b.covered || 0) - (a.covered || 0),
        );
        const ss = (s as StatesListEntry[]).sort((a, b) =>
          a.state.localeCompare(b.state),
        );
        setProfessions(pp);
        setStates(ss);
      })
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <p className="text-xs font-mono tracking-widest uppercase text-muted-foreground mb-3">
        State licensing data
      </p>
      <h1 className="text-3xl font-semibold tracking-tight mb-2">
        {mode === "profession" ? "Pick a profession" : "Pick a state"}
      </h1>
      <p className="text-muted-foreground mb-6 max-w-2xl">
        Side-by-side licensure and scope of practice across U.S. states,
        auto-extracted from state statutes. Every claim is backed by a
        verbatim quote regex-validated against the source.
      </p>

      {/* Mode toggle — same visual pattern as the profile-view's table/map */}
      <div className="mb-6 inline-flex rounded-md border bg-muted/30 p-1 text-xs font-mono">
        <button
          onClick={() => setMode("profession")}
          className={
            "px-3 py-1 rounded " +
            (mode === "profession"
              ? "bg-background shadow-sm text-foreground"
              : "text-muted-foreground hover:text-foreground")
          }
        >
          by profession
        </button>
        <button
          onClick={() => setMode("state")}
          className={
            "px-3 py-1 rounded " +
            (mode === "state"
              ? "bg-background shadow-sm text-foreground"
              : "text-muted-foreground hover:text-foreground")
          }
        >
          by state
        </button>
      </div>

      {error && (
        <div className="rounded border border-destructive bg-destructive/5 px-4 py-3 text-sm text-destructive">
          Failed to load list data: {error}
        </div>
      )}

      {mode === "profession" && (
        <>
          {!professions && !error && (
            <p className="text-sm text-muted-foreground">Loading…</p>
          )}
          {professions && (
            <div className="grid gap-3">
              {professions.map((p) => (
                <Link
                  key={p.profession}
                  href={`/professions/${encodeURIComponent(p.profession)}`}
                  className="block group"
                >
                  <Card className="py-3 transition-colors hover:border-foreground/30">
                    <CardHeader className="flex flex-row items-baseline justify-between gap-4 space-y-0">
                      <CardTitle className="text-base font-medium group-hover:underline flex items-center gap-2">
                        <span
                          className={`w-2 h-2 rounded-full shrink-0 ${
                            professionStyle(p.profession).dot
                          }`}
                        />
                        {p.display}
                      </CardTitle>
                      <span className="text-xs font-mono text-muted-foreground whitespace-nowrap">
                        {p.covered}/{(p.covered || 0) + (p.gaps || 0)} states ·{" "}
                        {p.fields} profession-specific + {UNIVERSAL_FIELDS_COUNT} universal fields ·{" "}
                        {p.verified_pct ?? "—"}% verified
                      </span>
                    </CardHeader>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </>
      )}

      {mode === "state" && (
        <>
          {!states && !error && (
            <p className="text-sm text-muted-foreground">Loading…</p>
          )}
          {states && states.length === 0 && (
            <p className="text-sm text-muted-foreground italic">
              No state-level data published yet — run pipeline.publish.
              build_state_browse to generate it.
            </p>
          )}
          {states && states.length > 0 && (
            <div className="grid gap-3">
              {states.map((s) => (
                <Link
                  key={s.state}
                  href={`/states/${s.state}`}
                  className="block group"
                >
                  <Card className="py-3 transition-colors hover:border-foreground/30">
                    <CardHeader className="flex flex-row items-baseline justify-between gap-4 space-y-0">
                      <CardTitle className="text-base font-mono font-medium group-hover:underline">
                        {s.state}
                      </CardTitle>
                      <span className="text-xs font-mono text-muted-foreground whitespace-nowrap">
                        {s.sections.toLocaleString()} sections ·{" "}
                        {s.professions.length} profession
                        {s.professions.length === 1 ? "" : "s"}
                      </span>
                    </CardHeader>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </>
      )}

      {/* Cross-cutting umbrella content is now embedded as a tab on each
          per-profession and per-state page (since 2026-05-28). The standalone
          /umbrella overview still exists as a coverage report — surfaced
          below in the Reports section. */}

      <section className="mt-10">
        <p className="text-xs font-mono tracking-widest uppercase text-muted-foreground mb-3">
          Reports
        </p>
        <div className="grid gap-3">
          <Link href="/reports" className="block group">
            <Card className="py-3 transition-colors hover:border-foreground/30">
              <CardHeader className="flex flex-row items-baseline justify-between gap-4 space-y-0">
                <CardTitle className="text-base font-medium group-hover:underline">
                  Generated artifacts
                </CardTitle>
                <span className="text-xs font-mono text-muted-foreground whitespace-nowrap">
                  scorecards &amp; summaries
                </span>
              </CardHeader>
            </Card>
          </Link>
          <Link href="/umbrella" className="block group">
            <Card className="py-3 transition-colors hover:border-foreground/30">
              <CardHeader className="flex flex-row items-baseline justify-between gap-4 space-y-0">
                <CardTitle className="text-base font-medium group-hover:underline">
                  Cross-cutting statute coverage
                </CardTitle>
                <span className="text-xs font-mono text-muted-foreground whitespace-nowrap">
                  data quality matrix across 45 states
                </span>
              </CardHeader>
            </Card>
          </Link>
        </div>
      </section>
    </main>
  );
}

"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import type { ProfessionsListEntry } from "@/lib/types";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";

export default function HomePage() {
  const [items, setItems] = useState<ProfessionsListEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/professions.json")
      .then((r) => r.json())
      .then((d: ProfessionsListEntry[]) => {
        d.sort((a, b) => (b.covered || 0) - (a.covered || 0));
        setItems(d);
      })
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <p className="text-xs font-mono tracking-widest uppercase text-muted-foreground mb-3">
        State licensing data
      </p>
      <h1 className="text-3xl font-semibold tracking-tight mb-2">
        Pick a profession
      </h1>
      <p className="text-muted-foreground mb-8 max-w-2xl">
        Side-by-side licensure and scope of practice across U.S. states,
        auto-extracted from state statutes. Every claim is backed by a
        verbatim quote regex-validated against the source.
      </p>

      {error && (
        <div className="rounded border border-destructive bg-destructive/5 px-4 py-3 text-sm text-destructive">
          Failed to load professions.json: {error}
        </div>
      )}

      {!items && !error && (
        <p className="text-sm text-muted-foreground">Loading…</p>
      )}

      {items && (
        <div className="grid gap-3">
          {items.map((p) => (
            <Link
              key={p.profession}
              href={`/profile?p=${encodeURIComponent(p.profession)}`}
              className="block group"
            >
              <Card className="py-3 transition-colors hover:border-foreground/30">
                <CardHeader className="flex flex-row items-baseline justify-between gap-4 space-y-0">
                  <CardTitle className="text-base font-medium group-hover:underline">
                    {p.display}
                  </CardTitle>
                  <span className="text-xs font-mono text-muted-foreground whitespace-nowrap">
                    {p.covered}/{(p.covered || 0) + (p.gaps || 0)} states ·{" "}
                    {p.fields} fields · {p.verified_pct ?? "—"}% verified
                  </span>
                </CardHeader>
              </Card>
            </Link>
          ))}
        </div>
      )}

      <section className="mt-10 grid gap-3">
        <p className="text-xs font-mono tracking-widest uppercase text-muted-foreground">
          Tools
        </p>
        <Link href="/search" className="block group">
          <Card className="py-3 transition-colors hover:border-foreground/30">
            <CardHeader className="flex flex-row items-baseline justify-between gap-4 space-y-0">
              <CardTitle className="text-base font-medium group-hover:underline">
                Search across all extractions
              </CardTitle>
              <span className="text-xs font-mono text-muted-foreground whitespace-nowrap">
                phrase + statute search
              </span>
            </CardHeader>
          </Card>
        </Link>
        <Link href="/reports" className="block group">
          <Card className="py-3 transition-colors hover:border-foreground/30">
            <CardHeader className="flex flex-row items-baseline justify-between gap-4 space-y-0">
              <CardTitle className="text-base font-medium group-hover:underline">
                Reports & artifacts
              </CardTitle>
              <span className="text-xs font-mono text-muted-foreground whitespace-nowrap">
                scorecards & summaries
              </span>
            </CardHeader>
          </Card>
        </Link>
      </section>
    </main>
  );
}

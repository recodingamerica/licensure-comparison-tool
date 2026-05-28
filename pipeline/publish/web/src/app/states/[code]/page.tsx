"use client";

// /states/[code] — unified per-state page.
//
// One merged view: each profession this state regulates is a card showing
// its practice-act sections + cross-cutting umbrella sections. Mirror of
// /professions/[id]?view=statutes which does the same merge on the
// profession-first axis.

import { Suspense, use, useEffect, useState } from "react";
import Link from "next/link";
import { StateStatutesView } from "@/components/state-statutes-view";
import type { StateBrowsePayload } from "@/lib/state-browse-types";

function StateInner({ params }: { params: Promise<{ code: string }> }) {
  const { code: raw } = use(params);
  const code = raw.toUpperCase();

  const [payload, setPayload] = useState<StateBrowsePayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setPayload(null);
    setError(null);
    fetch(`/data/state/${encodeURIComponent(code)}.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`No state data for ${code}`);
        return r.json();
      })
      .then((d: StateBrowsePayload) => setPayload(d))
      .catch((e) => setError(String(e)));
  }, [code]);

  return (
    <main className="mx-auto max-w-7xl px-6 py-10 space-y-6">
      <div className="flex items-baseline gap-3">
        <Link
          href="/"
          className="text-xs font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
        >
          ← all states
        </Link>
      </div>
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold">{code}</h1>
      </header>

      {error && (
        <div className="rounded border border-destructive bg-destructive/5 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {!payload && !error && <p className="text-sm text-muted-foreground">Loading…</p>}
      {payload && <StateStatutesView payload={payload} />}
    </main>
  );
}

export default function Page({ params }: { params: Promise<{ code: string }> }) {
  return (
    <Suspense
      fallback={
        <main className="mx-auto max-w-7xl px-6 py-10">
          <p className="text-sm text-muted-foreground">Loading…</p>
        </main>
      }
    >
      <StateInner params={params} />
    </Suspense>
  );
}

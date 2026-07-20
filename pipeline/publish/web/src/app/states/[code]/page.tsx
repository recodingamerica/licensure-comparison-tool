"use client";

// /states/[code] — unified per-state page.
//
// One merged view: each profession this state regulates is a card showing
// its practice-act sections + cross-cutting umbrella sections. Mirror of
// /professions/[id]?view=statutes which does the same merge on the
// profession-first axis.

import { Suspense, use } from "react";
import { BackLink } from "@/components/ui/back-link";
import { StateStatutesView } from "@/components/state-statutes-view";
import type { StateBrowsePayload } from "@/lib/state-browse-types";
import { useJsonData } from "@/lib/use-json-data";

function StateInner({ params }: { params: Promise<{ code: string }> }) {
  const { code: raw } = use(params);
  const code = raw.toUpperCase();

  const { data: payload, error } = useJsonData<StateBrowsePayload>(
    `/data/state/${encodeURIComponent(code)}.json`,
    `No state data for ${code}`,
  );

  return (
    <main className="mx-auto max-w-7xl px-6 py-10 space-y-6">
      <div className="flex items-baseline gap-3">
        <BackLink href="/">all states</BackLink>
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

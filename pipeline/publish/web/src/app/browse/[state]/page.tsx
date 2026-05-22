"use client";

// /browse/[state]
//
// State-level view: every regulation that touches a licensed profession
// in this state, grouped by audience (universal / multi-profession /
// single-profession). Filter chips let you narrow to one or more
// professions and the tree narrows to match — universal always shows,
// multi-prof shows if the selected set intersects applies_to,
// single-prof shows if its profession is selected.

import { Suspense, use, useEffect, useState } from "react";
import Link from "next/link";
import { StateBrowseClient } from "@/components/browse/state-browse-client";
import type { StateBrowsePayload } from "@/lib/state-browse-types";

type Params = Promise<{ state: string }>;

function StateBrowseInner({ params }: { params: Params }) {
  const { state: rawState } = use(params);
  const state = rawState.toUpperCase();
  const [payload, setPayload] = useState<StateBrowsePayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setPayload(null);
    setError(null);
    fetch(`/data/state/${encodeURIComponent(state)}.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`No state data for ${state}`);
        return r.json();
      })
      .then((d: StateBrowsePayload) => setPayload(d))
      .catch((e) => setError(String(e)));
  }, [state]);

  if (error) {
    return (
      <main className="mx-auto max-w-2xl px-6 py-12">
        <p className="text-sm text-destructive">{error}</p>
        <Link href="/" className="text-xs underline mt-4 block">← home</Link>
      </main>
    );
  }
  if (!payload) {
    return (
      <main className="mx-auto max-w-2xl px-6 py-12">
        <p className="text-xs text-muted-foreground">Loading…</p>
      </main>
    );
  }

  return <StateBrowseClient payload={payload} />;
}

export default function Page({ params }: { params: Params }) {
  return (
    <Suspense
      fallback={
        <main className="mx-auto max-w-2xl px-6 py-12">
          <p className="text-xs text-muted-foreground">Loading…</p>
        </main>
      }
    >
      <StateBrowseInner params={params} />
    </Suspense>
  );
}

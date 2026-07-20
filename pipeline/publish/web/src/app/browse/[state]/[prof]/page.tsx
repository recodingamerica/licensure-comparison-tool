"use client";

// /browse/[state]/[prof]
//
// Two-pane document-browse view for one (state, profession) pair: hierarchy
// tree on the left (sections grouped by scope_layer — practice act, health-
// professions umbrella, universal umbrella), detail panel on the right
// (full section text with quote_spans highlighted in amber, search hits
// in yellow).
//
// Data source: the existing per-profession blob already shipped to
// /data/<prof>.json — same blob the table view uses. We pluck `row.
// browse_sections` for the matching state. Identical client-side fetch
// pattern as /profile.

import { Suspense, use } from "react";
import Link from "next/link";
import type { BrowsePayload } from "@/lib/types";
import type { TreeNode } from "@/components/browse/tree-node";
import { BrowseClient } from "@/components/browse/browse-client";
import { useJsonData } from "@/lib/use-json-data";

type Params = Promise<{ state: string; prof: string }>;

function BrowseInner({ params }: { params: Params }) {
  const { state: rawState, prof } = use(params);
  const state = rawState.toUpperCase();
  // Per-(profession, state) browse file — much smaller than the main profile
  // blob (only THIS state's sections), so the page loads fast even for
  // big-statute states like nursing.
  const { data: payload, error } = useJsonData<BrowsePayload<TreeNode>>(
    `/data/${encodeURIComponent(prof)}/browse/${encodeURIComponent(state)}.json`,
    `No browse data for ${prof}/${state}`,
  );

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

  return (
    <BrowseClient
      state={state}
      profession={prof}
      sections={payload.sections}
      groups={payload.groups ?? []}
    />
  );
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
      <BrowseInner params={params} />
    </Suspense>
  );
}

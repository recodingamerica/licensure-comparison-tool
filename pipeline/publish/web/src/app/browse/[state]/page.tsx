"use client";

// /browse/[state]
//
// State-level view: every regulation that touches a licensed profession
// in this state, grouped by audience (universal / multi-profession /
// single-profession). Filter chips let you narrow to one or more
// professions and the tree narrows to match — universal always shows,
// multi-prof shows if the selected set intersects applies_to,
// single-prof shows if its profession is selected.

import { Suspense, use } from "react";
import { StateBrowseClient } from "@/components/browse/state-browse-client";
import {
  BrowseErrorMain,
  BrowseLoadingMain,
} from "@/components/browse/browse-page-shell";
import type { StateBrowsePayload } from "@/lib/state-browse-types";
import { useJsonData } from "@/lib/use-json-data";

type Params = Promise<{ state: string }>;

function StateBrowseInner({ params }: { params: Params }) {
  const { state: rawState } = use(params);
  const state = rawState.toUpperCase();
  const { data: payload, error } = useJsonData<StateBrowsePayload>(
    `/data/state/${encodeURIComponent(state)}.json`,
    `No state data for ${state}`,
  );

  if (error) return <BrowseErrorMain error={error} />;
  if (!payload) return <BrowseLoadingMain />;

  return <StateBrowseClient payload={payload} />;
}

export default function Page({ params }: { params: Params }) {
  return (
    <Suspense fallback={<BrowseLoadingMain />}>
      <StateBrowseInner params={params} />
    </Suspense>
  );
}

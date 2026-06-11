"use client";

// /professions/[id] — unified per-profession page.
//
// Three tabs at top — different lenses on this profession's data:
//   Table     — structured AG Grid comparison (only the 6 mapped profs)
//   Map       — choropleth of one field across states (only when map_prep)
//   Statutes  — merged per-state view: practice act + cross-cutting umbrella
//
// Active tab in ?view=. Defaults to table for mapped professions, statutes
// for umbrella-only ones.

import { Suspense, use, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import type { ProfilePayload } from "@/lib/types";
import { ProfileView } from "@/components/profile-view";
import { ProfessionStatutesView } from "@/components/profession-statutes-view";
import { ProfileTags } from "@/components/profile-tags";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { professionStyle, useProfessionMeta } from "@/lib/profession-colors";

type View = "table" | "map" | "statutes" | "tags";

function ProfessionInner({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  // Trigger /professions.json load so the family-color dot resolves.
  useProfessionMeta();
  const router = useRouter();
  const pathname = usePathname();
  const sp = useSearchParams();

  const [payload, setPayload] = useState<ProfilePayload | null>(null);
  const [dataExists, setDataExists] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setPayload(null);
    setError(null);
    setDataExists(null);
    fetch(`/data/${encodeURIComponent(id)}.json`)
      .then((r) => {
        if (r.status === 404) {
          setDataExists(false);
          return null;
        }
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d: ProfilePayload | null) => {
        if (d) {
          setPayload(d);
          setDataExists(true);
        }
      })
      .catch((e) => setError(String(e)));
  }, [id]);

  const viewParam = sp.get("view");
  // Legacy bookmark compatibility: the standalone umbrella page redirect
  // landed users at ?tab=umbrella for a while before the merge — read that
  // too so old links work without a second redirect hop.
  const legacyTab = sp.get("tab");
  const view: View = useMemo(() => {
    if (viewParam === "map" && payload?.map_prep) return "map";
    if (viewParam === "tags") return "tags";
    if (
      viewParam === "statutes" ||
      viewParam === "hierarchy" ||
      viewParam === "umbrella" ||
      legacyTab === "umbrella"
    )
      return "statutes";
    if (viewParam === "table" && dataExists !== false) return "table";
    return dataExists === false ? "statutes" : "table";
  }, [viewParam, legacyTab, payload, dataExists]);

  const setView = (next: View) => {
    const params = new URLSearchParams(sp.toString());
    if (next === "table") params.delete("view");
    else params.set("view", next);
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  };

  const profDisplay = payload?.display ?? id.replace(/_/g, " ");
  const hasMap = !!payload?.map_prep;
  const hasData = dataExists !== false;

  return (
    <main className="mx-auto max-w-7xl px-6 py-10 space-y-6">
      <div className="flex items-baseline gap-3">
        <Link
          href="/"
          className="text-xs font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
        >
          ← all professions
        </Link>
      </div>
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold flex items-center gap-3">
          <span className={`w-3 h-3 rounded-full shrink-0 ${professionStyle(id).dot}`} />
          {profDisplay}
        </h1>
      </header>

      {error && (
        <div className="rounded border border-destructive bg-destructive/5 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}

      <Tabs value={view} onValueChange={(v) => setView(v as View)}>
        <TabsList>
          <TabsTrigger value="table" disabled={!hasData}>
            Table
            {!hasData && (
              <span className="ml-2 text-[10px] text-muted-foreground">(no data)</span>
            )}
          </TabsTrigger>
          <TabsTrigger value="map" disabled={!hasMap}>
            Map
            {!hasMap && (
              <span className="ml-2 text-[10px] text-muted-foreground">(no map)</span>
            )}
          </TabsTrigger>
          <TabsTrigger value="statutes">Statutes</TabsTrigger>
          <TabsTrigger value="tags" disabled={!hasMap}>
            Tags
            {!hasMap && (
              <span className="ml-2 text-[10px] text-muted-foreground">(no tags)</span>
            )}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="table" className="mt-4">
          {dataExists === null && <p className="text-sm text-muted-foreground">Loading…</p>}
          {dataExists && payload && <ProfileView payload={payload} embedded view="table" />}
        </TabsContent>
        <TabsContent value="map" className="mt-4">
          {dataExists && payload && <ProfileView payload={payload} embedded view="map" />}
        </TabsContent>
        <TabsContent value="statutes" className="mt-4">
          <ProfessionStatutesView profPayload={payload} id={id} />
        </TabsContent>
        <TabsContent value="tags" className="mt-4">
          <ProfileTags professionId={id} />
        </TabsContent>
      </Tabs>
    </main>
  );
}

export default function Page({ params }: { params: Promise<{ id: string }> }) {
  return (
    <Suspense
      fallback={
        <main className="mx-auto max-w-7xl px-6 py-10">
          <p className="text-sm text-muted-foreground">Loading…</p>
        </main>
      }
    >
      <ProfessionInner params={params} />
    </Suspense>
  );
}

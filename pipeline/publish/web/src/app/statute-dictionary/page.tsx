"use client";

// /statute-dictionary — pick an occupation + a state from dropdowns and get that
// pair's full statute tree inline (Atharv #77). Reuses the existing /browse tree
// (BrowseClient) in `embedded` mode; the state dropdown is gated to the states
// that actually have a tree for the chosen occupation, so coverage gaps are
// visible rather than dead-ends.

import { Suspense, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Combobox, type ComboboxOption } from "@/components/ui/combobox";
import { BrowseClient } from "@/components/browse/browse-client";
import type { BrowsePayload } from "@/lib/types";
import type { TreeNode } from "@/components/browse/tree-node";
import { STATE_NAMES } from "@/lib/states";

type ProfEntry = { profession: string; display?: string };
type StateEntry = { state: string; sections: number; professions: string[] };

function StatuteDictionaryInner() {
  const [profs, setProfs] = useState<ProfEntry[] | null>(null);
  const [states, setStates] = useState<StateEntry[] | null>(null);
  const [loadErr, setLoadErr] = useState<string | null>(null);

  const [prof, setProf] = useState("");
  const [state, setState] = useState("");

  const [payload, setPayload] = useState<BrowsePayload<TreeNode> | null>(null);
  const [treeErr, setTreeErr] = useState<string | null>(null);

  // Load the two manifests once.
  useEffect(() => {
    Promise.all([
      fetch("/professions.json").then((r) => (r.ok ? r.json() : [])),
      fetch("/states.json").then((r) => (r.ok ? r.json() : [])),
    ])
      .then(([p, s]) => {
        setProfs(p);
        setStates(s);
      })
      .catch((e) => setLoadErr(String(e)));
  }, []);

  // profession → sorted list of states that have a tree (invert states.json).
  const profToStates = useMemo(() => {
    const m = new Map<string, string[]>();
    for (const s of states ?? []) {
      for (const p of s.professions ?? []) {
        if (!m.has(p)) m.set(p, []);
        m.get(p)!.push(s.state);
      }
    }
    for (const arr of m.values()) arr.sort();
    return m;
  }, [states]);

  const profOptions = useMemo<ComboboxOption[]>(
    () =>
      (profs ?? [])
        .filter((p) => profToStates.has(p.profession))
        .map((p) => ({
          value: p.profession,
          label: p.display || p.profession.replace(/_/g, " "),
          keywords: p.profession,
        }))
        .sort((a, b) => a.label.localeCompare(b.label)),
    [profs, profToStates],
  );

  const coveredStates = prof ? profToStates.get(prof) ?? [] : [];
  const stateOptions = useMemo<ComboboxOption[]>(
    () =>
      coveredStates.map((st) => ({
        value: st,
        label: STATE_NAMES[st] ? `${STATE_NAMES[st]} (${st})` : st,
        keywords: st,
      })),
    [coveredStates],
  );

  // Fetch the selected pair's tree.
  useEffect(() => {
    if (!prof || !state) {
      setPayload(null);
      setTreeErr(null);
      return;
    }
    setPayload(null);
    setTreeErr(null);
    fetch(`/data/${encodeURIComponent(prof)}/browse/${encodeURIComponent(state)}.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`No statute tree for ${prof}/${state}`);
        return r.json();
      })
      .then((d: BrowsePayload<TreeNode>) => setPayload(d))
      .catch((e) => setTreeErr(String(e)));
  }, [prof, state]);

  const onProf = (v: string) => {
    setProf(v);
    // If the chosen occupation doesn't cover the current state, clear it.
    if (v && state && !(profToStates.get(v) ?? []).includes(state)) setState("");
  };

  return (
    <div className="flex flex-col h-screen">
      <header className="border-b px-6 py-3 bg-background">
        <div className="flex items-baseline gap-3 flex-wrap">
          <Link
            href="/"
            className="text-xs font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
          >
            ← home
          </Link>
          <h1 className="text-lg font-semibold">Statute Dictionary</h1>
          <span className="text-xs text-muted-foreground">
            pick an occupation and a state to see its full statute tree
          </span>
        </div>
        <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-3xl">
          <label className="flex flex-col gap-1 text-xs">
            <span className="text-muted-foreground">Occupation</span>
            <Combobox
              value={prof}
              onValueChange={onProf}
              options={profOptions}
              placeholder={profs ? "Select an occupation…" : "Loading…"}
              searchPlaceholder="Search occupations…"
              emptyText="No occupations."
            />
          </label>
          <label className="flex flex-col gap-1 text-xs">
            <span className="text-muted-foreground">
              State{prof ? ` — ${coveredStates.length} with a tree` : ""}
            </span>
            <Combobox
              value={state}
              onValueChange={(v) => setState(v)}
              options={stateOptions}
              placeholder={prof ? "Select a state…" : "Pick an occupation first"}
              searchPlaceholder="Search states…"
              emptyText="No states with a tree."
            />
          </label>
        </div>
      </header>

      <div className="flex-1 min-h-0">
        {loadErr ? (
          <p className="p-6 text-sm text-destructive">{loadErr}</p>
        ) : !prof || !state ? (
          <p className="p-6 text-sm text-muted-foreground">
            Choose an occupation and a state above. The state list shows only the
            states we have a statute tree for that occupation.
          </p>
        ) : treeErr ? (
          <p className="p-6 text-sm text-destructive">{treeErr}</p>
        ) : !payload ? (
          <p className="p-6 text-xs text-muted-foreground">Loading tree…</p>
        ) : (
          <BrowseClient
            key={`${prof}-${state}`}
            state={state}
            profession={prof}
            sections={payload.sections}
            groups={payload.groups ?? []}
            embedded
          />
        )}
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <Suspense
      fallback={
        <main className="mx-auto max-w-2xl px-6 py-12">
          <p className="text-xs text-muted-foreground">Loading…</p>
        </main>
      }
    >
      <StatuteDictionaryInner />
    </Suspense>
  );
}

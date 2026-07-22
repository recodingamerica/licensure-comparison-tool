"use client";

// /downloads — get the data as an Excel workbook: by occupation (all states) or by state
// (all occupations). Each option links a pre-generated file on Blob (build_downloads.py);
// the index (occupation/state → url) is baked in as /data/downloads_index.json.

import { useEffect, useMemo, useState } from "react";
import { BackLink } from "@/components/ui/back-link";
import { Combobox, type ComboboxOption } from "@/components/ui/combobox";
import { STATE_NAMES } from "@/lib/states";

type Occ = { id: string; display: string; url: string };
type St = { code: string; url: string };
type Index = { occupations: Occ[]; states: St[] };

const DL_BTN =
  "mt-4 inline-flex items-center gap-2 rounded-md bg-foreground px-4 py-2 text-sm " +
  "font-medium text-background hover:opacity-90";

export default function DownloadsPage() {
  const [idx, setIdx] = useState<Index | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [prof, setProf] = useState("");
  const [state, setState] = useState("");

  useEffect(() => {
    fetch("/data/downloads_index.json")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((d: Index) => setIdx(d))
      .catch((e) => setErr(String(e)));
  }, []);

  const occOptions = useMemo<ComboboxOption[]>(
    () =>
      (idx?.occupations ?? [])
        .map((o) => ({ value: o.id, label: o.display, keywords: o.id }))
        .sort((a, b) => a.label.localeCompare(b.label)),
    [idx],
  );
  const stateOptions = useMemo<ComboboxOption[]>(
    () =>
      (idx?.states ?? []).map((s) => ({
        value: s.code,
        label: `${s.code} — ${STATE_NAMES[s.code] ?? s.code}`,
        keywords: s.code,
      })),
    [idx],
  );

  const occUrl = idx?.occupations.find((o) => o.id === prof)?.url;
  const stateUrl = idx?.states.find((s) => s.code === state)?.url;

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <BackLink href="/">home</BackLink>
      <h1 className="mt-2 text-2xl font-semibold">Download data</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Get the full data as an Excel workbook — one occupation across all states, or one state
        across all occupations. Each file has three tabs: <b>Processed</b> (the extracted
        fields), <b>Evidence</b> (each value with the verbatim statute quote &amp; citation it
        came from), and <b>Raw statute text</b>.
      </p>

      {err && (
        <p className="mt-6 text-sm text-destructive">
          Couldn&apos;t load the download list: {err}
        </p>
      )}

      <div className="mt-8 grid gap-6 sm:grid-cols-2">
        <section className="rounded-lg border p-5">
          <h2 className="text-base font-medium">By occupation</h2>
          <p className="mt-1 mb-3 text-xs text-muted-foreground">
            One occupation, all 50 states.
          </p>
          <Combobox
            value={prof}
            onValueChange={setProf}
            options={occOptions}
            placeholder={idx ? "Pick an occupation…" : "Loading…"}
            searchPlaceholder="Search occupations…"
            emptyText="No occupations."
          />
          {occUrl && (
            <a href={occUrl} download className={DL_BTN}>
              Download Excel ↓
            </a>
          )}
        </section>

        <section className="rounded-lg border p-5">
          <h2 className="text-base font-medium">By state</h2>
          <p className="mt-1 mb-3 text-xs text-muted-foreground">
            One state, all occupations.
          </p>
          <Combobox
            value={state}
            onValueChange={setState}
            options={stateOptions}
            placeholder={idx ? "Pick a state…" : "Loading…"}
            searchPlaceholder="Search states…"
            emptyText="No states."
          />
          {stateUrl && (
            <a href={stateUrl} download className={DL_BTN}>
              Download Excel ↓
            </a>
          )}
        </section>
      </div>
    </main>
  );
}

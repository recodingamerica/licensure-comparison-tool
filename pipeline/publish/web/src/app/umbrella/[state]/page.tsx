"use client";

// /umbrella/[state]  —  per-state umbrella sections with applies_to.
//
// For one state, list every umbrella section grouped by chapter, with the
// set of professions it applies to. Universal sections are tagged "All
// licensees"; unclassified sections are listed in a collapsed bucket at the
// bottom (honest residual — pipeline couldn't auto-scope them).

import { Suspense, use, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";

type Audience = "universal" | "enumerated" | "undetermined";
type Section = {
  url: string;
  label: string;
  audience: Audience;
  applies_to: string[] | null;
  text: string;
};
type Chapter = { slug: string; label: string; sections: Section[] };
type Payload = {
  state: string;
  section_count: number;
  coverage: { universal: number; enumerated: number; undetermined: number };
  all_professions: string[];
  chapters: Chapter[];
};

function fmtProf(p: string) {
  return p.replace(/_/g, " ");
}

function audienceBadge(s: Section) {
  if (s.audience === "universal") {
    return <Badge className="font-normal">All licensees</Badge>;
  }
  if (s.audience === "undetermined") {
    return (
      <Badge variant="outline" className="font-normal text-muted-foreground">
        unclassified
      </Badge>
    );
  }
  const applies = s.applies_to ?? [];
  return (
    <span className="inline-flex flex-wrap gap-1">
      {applies.map((p) => (
        <Badge key={p} variant="secondary" className="font-normal">
          {fmtProf(p)}
        </Badge>
      ))}
    </span>
  );
}

function StateUmbrellaInner({ params }: { params: Promise<{ state: string }> }) {
  const { state: raw } = use(params);
  const state = raw.toUpperCase();
  const [data, setData] = useState<Payload | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [profFilter, setProfFilter] = useState<string>("");
  const [showUnclassified, setShowUnclassified] = useState(false);

  useEffect(() => {
    setData(null);
    setErr(null);
    fetch(`/data/umbrella/${state}.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`No umbrella data for ${state}`);
        return r.json();
      })
      .then(setData)
      .catch((e) => setErr(String(e)));
  }, [state]);

  const filteredChapters = useMemo(() => {
    if (!data) return [];
    return data.chapters
      .map((ch) => ({
        ...ch,
        sections: ch.sections.filter((s) => {
          if (!showUnclassified && s.audience === "undetermined") return false;
          if (profFilter) {
            if (s.audience === "universal") return true; // universal applies to all
            if (s.audience === "enumerated") return (s.applies_to ?? []).includes(profFilter);
            return false;
          }
          return true;
        }),
      }))
      .filter((ch) => ch.sections.length > 0);
  }, [data, profFilter, showUnclassified]);

  if (err) {
    return (
      <main className="mx-auto max-w-3xl px-6 py-10">
        <p className="text-sm text-destructive">{err}</p>
        <Link href="/umbrella" className="mt-3 inline-block text-sm underline">
          ← back to all states
        </Link>
      </main>
    );
  }
  if (!data) {
    return <main className="mx-auto max-w-3xl px-6 py-10 text-sm text-muted-foreground">Loading…</main>;
  }

  return (
    <main className="mx-auto max-w-5xl px-6 py-10 space-y-6">
      <div>
        <Link href="/umbrella" className="text-sm text-muted-foreground underline-offset-2 hover:underline">
          ← all states
        </Link>
      </div>
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold">{state} — umbrella scope</h1>
        <p className="text-sm text-muted-foreground">
          {data.section_count} umbrella sections across {data.chapters.length} chapter(s) ·{" "}
          {data.coverage.universal} apply to all licensees ·{" "}
          {data.coverage.enumerated} list specific professions ·{" "}
          {data.coverage.undetermined} unclassified
        </p>
      </header>

      <div className="flex flex-wrap items-center gap-4 text-sm">
        <label className="flex items-center gap-2">
          <span className="text-muted-foreground">Filter by profession:</span>
          <select
            value={profFilter}
            onChange={(e) => setProfFilter(e.target.value)}
            className="rounded border bg-background px-2 py-1"
          >
            <option value="">(any)</option>
            {data.all_professions.map((p) => (
              <option key={p} value={p}>{fmtProf(p)}</option>
            ))}
          </select>
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={showUnclassified}
            onChange={(e) => setShowUnclassified(e.target.checked)}
          />
          <span className="text-muted-foreground">show unclassified</span>
        </label>
      </div>

      {filteredChapters.length === 0 ? (
        <p className="text-sm text-muted-foreground">No sections match the filter.</p>
      ) : (
        <div className="space-y-8">
          {filteredChapters.map((ch) => (
            <section key={ch.slug}>
              <h2 className="text-lg font-medium">{ch.label}</h2>
              <p className="text-xs text-muted-foreground mb-3">
                {ch.slug} · {ch.sections.length} section{ch.sections.length === 1 ? "" : "s"}
              </p>
              <ul className="space-y-3">
                {ch.sections.map((s) => (
                  <li key={s.url} className="rounded border p-3">
                    <div className="flex items-start justify-between gap-4">
                      <a
                        href={s.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium underline-offset-2 hover:underline"
                      >
                        {s.label}
                      </a>
                      <div className="shrink-0">{audienceBadge(s)}</div>
                    </div>
                    {s.text && (
                      <p className="mt-2 text-sm text-muted-foreground line-clamp-3">{s.text}</p>
                    )}
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      )}
    </main>
  );
}

export default function Page({ params }: { params: Promise<{ state: string }> }) {
  return (
    <Suspense fallback={<main className="mx-auto max-w-3xl px-6 py-10 text-sm text-muted-foreground">Loading…</main>}>
      <StateUmbrellaInner params={params} />
    </Suspense>
  );
}

"use client";

// /search — UI for cross-extraction phrase search.
//
// Hits /api/search with a debounced query, surfaces two tabs:
//   - "In extracted quotes (N)" — the LLM-grounded excerpts
//   - "In statute text (M)"     — full section bodies, with the matched
//                                 phrase highlighted via Postgres ts_headline
// Quote hits drill into /profile?p=<prof>&state=<state> (the existing
// profile page; future polish: scroll to the relevant row).
// Statute hits link to the source URL on Justia.

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

type QuoteHit = {
  kind: "quote";
  state: string;
  profession: string;
  field_path: string;
  value_text: string | null;
  quote: string;
  citation: string;
  unverified: boolean;
  rank: number;
};
type StatuteHit = {
  kind: "statute";
  state: string;
  profession: string | null;
  citation: string | null;
  label: string;
  hierarchy_level: string;
  is_umbrella: boolean;
  snippet: string; // HTML — contains <b>…</b> highlight markers from ts_headline
  rank: number;
};
type Payload = { q: string; quotes: QuoteHit[]; statutes: StatuteHit[] };

function useDebounced<T>(value: T, ms = 250): T {
  const [v, setV] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setV(value), ms);
    return () => clearTimeout(t);
  }, [value, ms]);
  return v;
}

function SearchInner() {
  const router = useRouter();
  const params = useSearchParams();
  const urlQ = params.get("q") ?? "";

  const [q, setQ] = useState(urlQ);
  const [tab, setTab] = useState<"quotes" | "statutes">("quotes");
  const [data, setData] = useState<Payload | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reflect the typed query back into the URL so links are shareable.
  // Debounce so we're not pushing a new history entry on every keystroke.
  const debouncedQ = useDebounced(q, 250);

  useEffect(() => {
    const trimmed = debouncedQ.trim();
    if (trimmed) {
      router.replace(`/search?q=${encodeURIComponent(trimmed)}`, { scroll: false });
    } else {
      router.replace(`/search`, { scroll: false });
      setData(null);
      return;
    }
    setLoading(true);
    setError(null);
    fetch(`/api/search?q=${encodeURIComponent(trimmed)}`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d: Payload) => setData(d))
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, [debouncedQ, router]);

  const counts = useMemo(
    () => ({
      quotes: data?.quotes.length ?? 0,
      statutes: data?.statutes.length ?? 0,
    }),
    [data],
  );

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <Link
        href="/"
        className="text-xs font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
      >
        ← home
      </Link>
      <h1 className="text-3xl font-semibold tracking-tight mt-6 mb-2">Search</h1>
      <p className="text-muted-foreground mb-6 max-w-3xl">
        Phrase search across every extraction. <span className="font-mono">In extracted quotes</span>{" "}
        hits the LLM-grounded excerpts (high signal but narrow); <span className="font-mono">In statute text</span>{" "}
        hits the full statutory language (broader, finds things we didn&apos;t extract).
      </p>

      <input
        type="search"
        autoFocus
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="e.g. telehealth, podiatric medicine, NLC..."
        className="w-full rounded-md border bg-background px-4 py-3 text-base placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
      />

      {loading && (
        <p className="text-sm text-muted-foreground mt-4">Searching…</p>
      )}
      {error && (
        <p className="rounded border border-destructive bg-destructive/5 px-4 py-3 text-sm text-destructive mt-4">
          {error}
        </p>
      )}

      {data && (
        <>
          <div className="mt-6 inline-flex rounded-md border bg-muted/30 p-1 text-xs font-mono">
            {(["quotes", "statutes"] as const).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={
                  "px-3 py-1 rounded " +
                  (tab === t
                    ? "bg-background shadow-sm text-foreground"
                    : "text-muted-foreground hover:text-foreground")
                }
              >
                {t === "quotes"
                  ? `Extracted quotes (${counts.quotes})`
                  : `Statute text (${counts.statutes})`}
              </button>
            ))}
          </div>

          {tab === "quotes" ? (
            <QuoteList hits={data.quotes} />
          ) : (
            <StatuteList hits={data.statutes} />
          )}
        </>
      )}
    </main>
  );
}

function QuoteList({ hits }: { hits: QuoteHit[] }) {
  if (hits.length === 0) {
    return (
      <p className="text-sm text-muted-foreground mt-6">No matches in extracted quotes.</p>
    );
  }
  return (
    <ul className="mt-4 divide-y rounded border">
      {hits.map((h, i) => (
        <li key={i} className="px-4 py-3 hover:bg-muted/30">
          <div className="flex items-baseline justify-between gap-4">
            <Link
              href={`/profile?p=${encodeURIComponent(h.profession)}`}
              className="text-sm font-medium hover:underline"
            >
              {h.state} · {h.profession.replace("_", " ")}{" "}
              <span className="text-xs font-mono text-muted-foreground">
                {h.field_path}
              </span>
            </Link>
            <span className="text-xs font-mono text-muted-foreground whitespace-nowrap">
              {h.citation}
            </span>
          </div>
          <p className="mt-1 text-sm text-foreground leading-snug">
            “{h.quote}”
          </p>
          {h.unverified && (
            <p className="mt-1 text-xs font-mono text-amber-700">⚠ unverified</p>
          )}
        </li>
      ))}
    </ul>
  );
}

function StatuteList({ hits }: { hits: StatuteHit[] }) {
  if (hits.length === 0) {
    return (
      <p className="text-sm text-muted-foreground mt-6">No matches in statute text.</p>
    );
  }
  return (
    <ul className="mt-4 divide-y rounded border">
      {hits.map((h, i) => (
        <li key={i} className="px-4 py-3 hover:bg-muted/30">
          <div className="flex items-baseline justify-between gap-4">
            <p className="text-sm font-medium">
              {h.state}{" "}
              <span className="text-xs font-mono text-muted-foreground">
                {h.label}
              </span>
              {h.is_umbrella && (
                <span className="ml-2 inline-block rounded-sm bg-muted px-1.5 py-0.5 text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
                  umbrella
                </span>
              )}
            </p>
            {h.citation && (
              <span className="text-xs font-mono text-muted-foreground whitespace-nowrap">
                {h.citation}
              </span>
            )}
          </div>
          <p
            className="mt-1 text-sm text-foreground leading-snug [&_b]:bg-amber-100 [&_b]:px-0.5"
            // ts_headline emits <b>…</b> around matched terms. We render it as
            // HTML, but the only attacker is Postgres — input is parameterized
            // via plainto_tsquery, so this is safe.
            dangerouslySetInnerHTML={{ __html: h.snippet }}
          />
        </li>
      ))}
    </ul>
  );
}

export default function SearchPage() {
  return (
    <Suspense
      fallback={
        <main className="mx-auto max-w-5xl px-6 py-12">
          <p className="text-sm text-muted-foreground">Loading…</p>
        </main>
      }
    >
      <SearchInner />
    </Suspense>
  );
}

"use client";

// /umbrella/profession/[id]  —  cross-state view of umbrella sections that
// apply to one profession.
//
// Each state card splits sections by `audience` (shared taxonomy with
// /browse/[state] — see lib/audience.ts): Applies to everyone / Shared with
// multiple professions / Profession-specific. Plus an "Unclassified in this
// state" residual (sections the pipeline couldn't confidently scope).
//
// State cards collapsed by default, sorted by section count. Three filters
// (Profession / State / Audience) as dropdowns at the top.

import { Suspense, use, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Combobox, type ComboboxOption } from "@/components/ui/combobox";
import {
  AUDIENCE_LABEL,
  AUDIENCE_DOT,
  AUDIENCE_KINDS,
  type AudienceKind,
} from "@/lib/audience";

// Audience dropdown is single-select. "all" = show every audience kind;
// "unclassified" = show only the residual; otherwise one specific kind.
type AudienceFilter = "all" | AudienceKind | "unclassified";

type Section = {
  url: string;
  label: string;
  audience: "universal" | "enumerated" | "undetermined";
  applies_to: string[] | null;
  text: string;
  audience_kind?: AudienceKind;
};
type Chapter = { slug: string; label: string; sections: Section[] };
type Coverage = Record<AudienceKind, number> & { unclassified_in_state: number };
type StateBlock = {
  state: string;
  section_count: number;
  coverage: Coverage;
  chapters: Chapter[];
  unclassified_chapters: Chapter[];
};
type Payload = {
  profession: string;
  state_count: number;
  directly_enumerated_state_count: number;
  section_count: number;
  coverage: Coverage;
  states: StateBlock[];
};
type ProfIndex = {
  professions: { profession: string; state_count: number }[];
};

function fmtProf(p: string) {
  return p.replace(/_/g, " ");
}

function AudienceBadge({ kind }: { kind: AudienceKind }) {
  return (
    <Badge variant="outline" className="font-mono text-[10px] gap-1.5">
      <span className={`w-1.5 h-1.5 rounded-full ${AUDIENCE_DOT[kind]}`} />
      {AUDIENCE_LABEL[kind]}
    </Badge>
  );
}

function SectionList({
  chapters,
  audienceFilter,
  unclassified,
}: {
  chapters: Chapter[];
  audienceFilter: Set<AudienceKind>;
  unclassified?: boolean;
}) {
  const visible = useMemo(() => {
    if (unclassified) return chapters;
    return chapters
      .map((ch) => ({
        ...ch,
        sections: ch.sections.filter(
          (s) => s.audience_kind != null && audienceFilter.has(s.audience_kind),
        ),
      }))
      .filter((ch) => ch.sections.length > 0);
  }, [chapters, audienceFilter, unclassified]);

  if (visible.length === 0) {
    return <p className="text-xs text-muted-foreground italic">No matching sections.</p>;
  }
  return (
    <>
      {visible.map((ch) => (
        <section key={ch.slug}>
          <h4 className="text-sm font-medium">{ch.label}</h4>
          <p className="text-xs text-muted-foreground mb-2">
            {ch.slug} · {ch.sections.length} section{ch.sections.length === 1 ? "" : "s"}
          </p>
          <ul className="space-y-2">
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
                  <div className="shrink-0">
                    {unclassified ? (
                      <Badge variant="outline" className="font-mono text-[10px] text-muted-foreground">
                        unclassified
                      </Badge>
                    ) : s.audience_kind ? (
                      <AudienceBadge kind={s.audience_kind} />
                    ) : null}
                  </div>
                </div>
                {s.text && (
                  <p className="mt-2 text-sm text-muted-foreground line-clamp-3">{s.text}</p>
                )}
              </li>
            ))}
          </ul>
        </section>
      ))}
    </>
  );
}

function StateCard({
  block,
  audienceFilter,
  showUnclassified,
}: {
  block: StateBlock;
  audienceFilter: Set<AudienceKind>;
  showUnclassified: boolean;
}) {
  const c = block.coverage;
  const visibleTotal = AUDIENCE_KINDS.reduce(
    (sum, k) => sum + (audienceFilter.has(k) ? c[k] : 0),
    0,
  );
  return (
    <details className="rounded border bg-card">
      <summary className="cursor-pointer list-none px-4 py-3 flex items-center justify-between gap-4">
        <div className="flex items-baseline gap-3 flex-wrap">
          <Link
            href={`/umbrella/${block.state}`}
            className="text-lg font-semibold underline-offset-2 hover:underline"
            onClick={(e) => e.stopPropagation()}
          >
            {block.state}
          </Link>
          <span className="text-xs text-muted-foreground flex flex-wrap items-center gap-2">
            <span>
              {visibleTotal} section{visibleTotal === 1 ? "" : "s"} matching
            </span>
            {AUDIENCE_KINDS.map((k) =>
              c[k] > 0 ? (
                <span key={k} className="inline-flex items-center gap-1">
                  <span className={`w-1.5 h-1.5 rounded-full ${AUDIENCE_DOT[k]}`} />
                  {c[k]}
                </span>
              ) : null,
            )}
            {c.unclassified_in_state > 0 && (
              <span className="text-amber-700 dark:text-amber-400">
                · {c.unclassified_in_state} unclassified
              </span>
            )}
          </span>
        </div>
        <span className="text-xs text-muted-foreground">expand</span>
      </summary>
      <div className="border-t px-4 py-3 space-y-3">
        {AUDIENCE_KINDS.map((k) =>
          audienceFilter.has(k) && c[k] > 0 ? (
            <details key={k} className="rounded border bg-muted/30">
              <summary className="cursor-pointer list-none px-3 py-2 flex items-center justify-between gap-2 text-sm">
                <span className="font-medium flex items-center gap-1.5">
                  <span className={`w-1.5 h-1.5 rounded-full ${AUDIENCE_DOT[k]}`} />
                  {AUDIENCE_LABEL[k]} <span className="text-muted-foreground">({c[k]})</span>
                </span>
                <span className="text-xs text-muted-foreground">expand</span>
              </summary>
              <div className="border-t px-3 py-3 space-y-4">
                <SectionList
                  chapters={block.chapters}
                  audienceFilter={new Set([k])}
                />
              </div>
            </details>
          ) : null,
        )}
        {showUnclassified && c.unclassified_in_state > 0 && (
          <details className="rounded border bg-amber-50/40 dark:bg-amber-950/20">
            <summary className="cursor-pointer list-none px-3 py-2 flex items-center justify-between gap-2 text-sm">
              <span className="font-medium">
                Unclassified in {block.state}{" "}
                <span className="text-muted-foreground">({c.unclassified_in_state})</span>
              </span>
              <span className="text-xs text-muted-foreground">
                may or may not apply — pipeline couldn&apos;t confidently scope
              </span>
            </summary>
            <div className="border-t px-3 py-3 space-y-4">
              <SectionList
                chapters={block.unclassified_chapters}
                audienceFilter={new Set()}
                unclassified
              />
            </div>
          </details>
        )}
      </div>
    </details>
  );
}

function ProfessionInner({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [data, setData] = useState<Payload | null>(null);
  const [index, setIndex] = useState<ProfIndex | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [audienceFilter, setAudienceFilter] = useState<AudienceFilter>("all");
  const [stateFilter, setStateFilter] = useState<string>("all");

  useEffect(() => {
    setData(null);
    setErr(null);
    setStateFilter("all");
    setAudienceFilter("all");
    fetch(`/data/umbrella/by_profession/${id}.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`No umbrella data for profession "${id}"`);
        return r.json();
      })
      .then(setData)
      .catch((e) => setErr(String(e)));
  }, [id]);

  useEffect(() => {
    fetch("/data/umbrella/by_profession/_index.json")
      .then((r) => (r.ok ? r.json() : null))
      .then(setIndex)
      .catch(() => {});
  }, []);

  // Derived: which audience kinds are visible, and whether to show
  // the unclassified residual on each card.
  const activeKinds = useMemo<Set<AudienceKind>>(() => {
    if (audienceFilter === "all") return new Set(AUDIENCE_KINDS);
    if (audienceFilter === "unclassified") return new Set();
    return new Set([audienceFilter]);
  }, [audienceFilter]);
  const showUnclassified = audienceFilter === "all" || audienceFilter === "unclassified";

  const visibleStates = useMemo(() => {
    if (!data) return [];
    let s = data.states;
    if (stateFilter !== "all") s = s.filter((b) => b.state === stateFilter);
    return s.filter((b) => {
      const tierTotal = AUDIENCE_KINDS.reduce(
        (sum, k) => sum + (activeKinds.has(k) ? b.coverage[k] : 0),
        0,
      );
      if (tierTotal > 0) return true;
      if (showUnclassified && b.coverage.unclassified_in_state > 0) return true;
      return false;
    });
  }, [data, stateFilter, activeKinds, showUnclassified]);

  if (err) {
    return (
      <main className="mx-auto max-w-3xl px-6 py-10">
        <p className="text-sm text-destructive">{err}</p>
        <Link href="/umbrella" className="mt-3 inline-block text-sm underline">
          ← back to umbrella overview
        </Link>
      </main>
    );
  }
  if (!data) {
    return <main className="mx-auto max-w-3xl px-6 py-10 text-sm text-muted-foreground">Loading…</main>;
  }

  const c = data.coverage;
  return (
    <main className="mx-auto max-w-5xl px-6 py-10 space-y-6">
      <div>
        <Link href="/umbrella" className="text-sm text-muted-foreground underline-offset-2 hover:underline">
          ← umbrella overview
        </Link>
      </div>
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold">{fmtProf(data.profession)} — umbrella scope</h1>
        <p className="text-sm text-muted-foreground">
          Applies in {data.state_count} state{data.state_count === 1 ? "" : "s"} · {data.section_count} sections ·{" "}
          {c.unclassified_in_state} unclassified
        </p>
      </header>

      <div className="border rounded bg-muted/30 px-4 py-3 grid grid-cols-1 sm:grid-cols-3 gap-3">
        {index && (
          <label className="flex flex-col gap-1 text-xs">
            <span className="text-muted-foreground">Profession</span>
            <Combobox
              value={data.profession}
              onValueChange={(v) => {
                if (v && v !== data.profession) {
                  window.location.href = `/umbrella/profession/${v}`;
                }
              }}
              options={index.professions.map<ComboboxOption>((p) => ({
                value: p.profession,
                label: `${fmtProf(p.profession)} (${p.state_count})`,
                keywords: p.profession,
              }))}
              searchPlaceholder="Search professions…"
              emptyText="No matching professions."
            />
          </label>
        )}
        <label className="flex flex-col gap-1 text-xs">
          <span className="text-muted-foreground">State</span>
          <Combobox
            value={stateFilter}
            onValueChange={(v) => v && setStateFilter(v)}
            options={[
              { value: "all", label: `All states (${data.states.length})` },
              ...data.states.map<ComboboxOption>((b) => ({
                value: b.state,
                label: `${b.state} (${b.section_count}${
                  b.coverage.unclassified_in_state > 0
                    ? ` + ${b.coverage.unclassified_in_state} unclassified`
                    : ""
                })`,
              })),
            ]}
            searchPlaceholder="Search states…"
            emptyText="No matching states."
          />
        </label>
        <label className="flex flex-col gap-1 text-xs">
          <span className="text-muted-foreground">Audience</span>
          <Select
            value={audienceFilter}
            onValueChange={(v) => v && setAudienceFilter(v as AudienceFilter)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All audiences</SelectItem>
              {AUDIENCE_KINDS.map((k) => (
                <SelectItem key={k} value={k}>
                  {AUDIENCE_LABEL[k]} ({c[k]})
                </SelectItem>
              ))}
              <SelectItem value="unclassified">
                Unclassified residual ({c.unclassified_in_state})
              </SelectItem>
            </SelectContent>
          </Select>
        </label>
      </div>

      {visibleStates.length === 0 ? (
        <p className="text-sm text-muted-foreground">No states match the filter.</p>
      ) : (
        <div className="space-y-3">
          {visibleStates.map((block) => (
            <StateCard
              key={block.state}
              block={block}
              audienceFilter={activeKinds}
              showUnclassified={showUnclassified}
            />
          ))}
        </div>
      )}
    </main>
  );
}

export default function Page({ params }: { params: Promise<{ id: string }> }) {
  return (
    <Suspense fallback={<main className="mx-auto max-w-3xl px-6 py-10 text-sm text-muted-foreground">Loading…</main>}>
      <ProfessionInner params={params} />
    </Suspense>
  );
}

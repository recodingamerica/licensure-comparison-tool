"use client";

// ProfessionStatutesView — merged per-state statute view for one profession.
//
// For each state where we have anything, one card containing BOTH:
//   1. Practice act    — the licensing chapter for this profession (statute
//                        text aggregated per row.sections)
//   2. Cross-cutting   — umbrella chapters that ALSO apply (the audience-
//      umbrella         tiered accordion lifted from ProfessionUmbrellaView)
//
// Replaces the previous two tabs ("Statute hierarchy" + "Cross-cutting
// statutes") which made the two halves of one answer feel like alternatives.

import { useEffect, useMemo, useState } from "react";
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
import type { ProfilePayload, Row, SectionRef } from "@/lib/types";
import {
  AUDIENCE_LABEL,
  AUDIENCE_DOT,
  AUDIENCE_KINDS,
  type AudienceKind,
} from "@/lib/audience";

type AudienceFilter = "all" | AudienceKind | "unclassified";

// Plain-English gloss for each umbrella tier — Atharv #76 was confused by the
// bare color dots/counts. Shown in the legend at the top of the view.
const TIER_HINT: Record<AudienceKind, string> = {
  universal: "binds every licensee in the state",
  multi: "shared by several named professions, including this one",
  single: "applies only to this profession",
};

type UmbrellaSection = {
  url: string;
  label: string;
  audience: "universal" | "enumerated" | "undetermined";
  applies_to: string[] | null;
  text: string;
  audience_kind?: AudienceKind;
};
type UmbrellaChapter = { slug: string; label: string; sections: UmbrellaSection[] };
type UmbrellaCoverage = Record<AudienceKind, number> & { unclassified_in_state: number };
type UmbrellaStateBlock = {
  state: string;
  section_count: number;
  coverage: UmbrellaCoverage;
  chapters: UmbrellaChapter[];
  unclassified_chapters: UmbrellaChapter[];
};
type UmbrellaPayload = {
  profession: string;
  state_count: number;
  directly_enumerated_state_count: number;
  section_count: number;
  coverage: UmbrellaCoverage;
  states: UmbrellaStateBlock[];
};

function AudienceBadge({ kind }: { kind: AudienceKind }) {
  return (
    <Badge variant="outline" className="font-mono text-[10px] gap-1.5">
      <span className={`w-1.5 h-1.5 rounded-full ${AUDIENCE_DOT[kind]}`} />
      {AUDIENCE_LABEL[kind]}
    </Badge>
  );
}

function UmbrellaSectionList({
  chapters,
  audienceFilter,
  unclassified,
}: {
  chapters: UmbrellaChapter[];
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
          <ul className="space-y-1.5">
            {ch.sections.map((s, i) => (
              <li key={`${s.url}-${i}`} className="flex items-baseline gap-2 text-sm">
                <a
                  href={s.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline-offset-2 hover:underline"
                >
                  {s.label}
                </a>
                {unclassified ? (
                  <Badge variant="outline" className="font-mono text-[10px] text-muted-foreground shrink-0">
                    unclassified
                  </Badge>
                ) : s.audience_kind ? (
                  <AudienceBadge kind={s.audience_kind} />
                ) : null}
              </li>
            ))}
          </ul>
        </section>
      ))}
    </>
  );
}

function PracticeActSection({
  sections,
}: {
  sections: SectionRef[];
}) {
  if (!sections.length) {
    return (
      <p className="text-xs text-muted-foreground italic">
        No practice-act sections shipped for this state.
      </p>
    );
  }
  // Compact "where the statute is" list — citation + linked label, no full
  // text (Atharv #76: this page is a guide to where the statutes are, not a
  // reader; the full text lives one click away in the statute tree).
  return (
    <ul className="space-y-1.5">
      {sections.map((s, i) => (
        <li key={`${s.url}-${i}`} className="flex items-baseline gap-2 text-sm">
          {s.citation && (
            <span className="font-mono text-xs text-muted-foreground shrink-0">
              {s.citation}
            </span>
          )}
          <a
            href={s.url}
            target="_blank"
            rel="noopener noreferrer"
            className="underline-offset-2 hover:underline"
          >
            {s.label || s.citation || s.url}
          </a>
        </li>
      ))}
    </ul>
  );
}

function CombinedStateCard({
  state,
  row,
  umbrella,
  audienceFilter,
  showUnclassified,
  profSlug,
}: {
  state: string;
  row: Row | null;
  umbrella: UmbrellaStateBlock | null;
  audienceFilter: Set<AudienceKind>;
  showUnclassified: boolean;
  profSlug: string;
}) {
  const practiceCount = row?.sections?.length ?? 0;
  const c = umbrella?.coverage;
  const umbrellaVisible = c
    ? AUDIENCE_KINDS.reduce((sum, k) => sum + (audienceFilter.has(k) ? c[k] : 0), 0)
    : 0;
  return (
    <details className="rounded border bg-card">
      <summary className="cursor-pointer list-none px-4 py-3 flex items-center justify-between gap-4">
        <div className="flex items-baseline gap-3 flex-wrap">
          <Link
            href={`/states/${state}/`}
            className="text-lg font-semibold underline-offset-2 hover:underline"
            onClick={(e) => e.stopPropagation()}
          >
            {state}
          </Link>
          <span className="text-xs text-muted-foreground flex flex-wrap items-center gap-2">
            {practiceCount > 0 && (
              <span>
                <strong className="text-foreground">{practiceCount}</strong> practice-act section
                {practiceCount === 1 ? "" : "s"}
              </span>
            )}
            {c && (
              <>
                <span>·</span>
                <span>
                  <strong className="text-foreground">{umbrellaVisible}</strong> umbrella section
                  {umbrellaVisible === 1 ? "" : "s"} matching
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
              </>
            )}
          </span>
        </div>
        <span className="text-xs text-muted-foreground">expand</span>
      </summary>
      <div className="border-t px-4 py-3 space-y-5">
        {/* Practice act */}
        {row && row.sections && row.sections.length > 0 && (
          <section>
            <div className="flex items-center justify-between gap-3 mb-2">
              <h3 className="text-sm font-semibold">Practice act</h3>
              <Link
                href={`/browse/${state}/${profSlug}`}
                className="inline-flex items-center gap-1 rounded-md border px-2.5 py-1 text-xs font-medium hover:bg-muted/50 shrink-0"
              >
                Full statute tree →
              </Link>
            </div>
            <PracticeActSection sections={row.sections} />
          </section>
        )}

        {/* Umbrella */}
        {umbrella && c && (
          <section>
            <h3 className="text-sm font-semibold mb-2">Cross-cutting umbrella</h3>
            <div className="space-y-3">
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
                      <UmbrellaSectionList
                        chapters={umbrella.chapters}
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
                      Unclassified in {state}{" "}
                      <span className="text-muted-foreground">({c.unclassified_in_state})</span>
                    </span>
                    <span className="text-xs text-muted-foreground">
                      may or may not apply
                    </span>
                  </summary>
                  <div className="border-t px-3 py-3 space-y-4">
                    <UmbrellaSectionList
                      chapters={umbrella.unclassified_chapters}
                      audienceFilter={new Set()}
                      unclassified
                    />
                  </div>
                </details>
              )}
            </div>
          </section>
        )}
      </div>
    </details>
  );
}

export function ProfessionStatutesView({
  profPayload,
  id,
}: {
  profPayload: ProfilePayload | null;
  id: string;
}) {
  const [umbrella, setUmbrella] = useState<UmbrellaPayload | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [audienceFilter, setAudienceFilter] = useState<AudienceFilter>("all");
  const [stateFilter, setStateFilter] = useState<string>("all");

  useEffect(() => {
    setUmbrella(null);
    setErr(null);
    setStateFilter("all");
    setAudienceFilter("all");
    fetch(`/data/umbrella/by_profession/${id}.json`)
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => setUmbrella(d))
      .catch((e) => setErr(String(e)));
  }, [id]);

  // Build the merged per-state list: any state that has a practice-act row
  // OR an umbrella block. Sort by total section count descending so the
  // meatiest states surface first.
  const merged = useMemo(() => {
    const byState = new Map<string, { row: Row | null; umbrella: UmbrellaStateBlock | null }>();
    for (const r of profPayload?.rows ?? []) {
      if (r.coverage_gap) continue;
      byState.set(r.state, { row: r, umbrella: null });
    }
    for (const u of umbrella?.states ?? []) {
      const existing = byState.get(u.state);
      if (existing) existing.umbrella = u;
      else byState.set(u.state, { row: null, umbrella: u });
    }
    const list = Array.from(byState.entries()).map(([state, v]) => {
      const practice = v.row?.sections?.length ?? 0;
      const umb = v.umbrella?.section_count ?? 0;
      return { state, ...v, sortKey: practice + umb };
    });
    list.sort((a, b) => b.sortKey - a.sortKey || a.state.localeCompare(b.state));
    return list;
  }, [profPayload, umbrella]);

  const activeKinds = useMemo<Set<AudienceKind>>(() => {
    if (audienceFilter === "all") return new Set(AUDIENCE_KINDS);
    if (audienceFilter === "unclassified") return new Set();
    return new Set([audienceFilter]);
  }, [audienceFilter]);
  const showUnclassified = audienceFilter === "all" || audienceFilter === "unclassified";

  const visible = useMemo(() => {
    if (stateFilter !== "all") return merged.filter((m) => m.state === stateFilter);
    return merged;
  }, [merged, stateFilter]);

  if (err) return <p className="text-sm text-destructive">{err}</p>;

  const u = umbrella?.coverage;
  const profSlug = profPayload?.profession ?? id;

  return (
    <div className="space-y-6">
      <p className="text-sm text-muted-foreground">
        A guide to where this profession&apos;s statutes live across{" "}
        {merged.length} state{merged.length === 1 ? "" : "s"} — each card lists the
        practice-act sections and the cross-cutting umbrella statutes that also apply, with a
        link straight into the full statute tree. Each section links to its full text.
        {u && u.unclassified_in_state > 0 && (
          <> {u.unclassified_in_state} umbrella sections are unclassified across all states.</>
        )}
      </p>

      {/* Legend — spell out the color tiers Atharv #76 found opaque. */}
      <div className="border rounded bg-muted/20 px-4 py-3 text-xs">
        <p className="font-medium text-foreground mb-2">What the tiers mean</p>
        <ul className="grid gap-1.5 sm:grid-cols-2">
          <li className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-slate-400 shrink-0" />
            <span className="font-medium">Practice act</span>
            <span className="text-muted-foreground">— this profession&apos;s own licensing chapter</span>
          </li>
          {AUDIENCE_KINDS.map((k) => (
            <li key={k} className="flex items-center gap-2">
              <span className={`inline-block w-2 h-2 rounded-full shrink-0 ${AUDIENCE_DOT[k]}`} />
              <span className="font-medium">{AUDIENCE_LABEL[k]}</span>
              <span className="text-muted-foreground">— {TIER_HINT[k]}</span>
            </li>
          ))}
          <li className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-amber-500 shrink-0" />
            <span className="font-medium">Unclassified</span>
            <span className="text-muted-foreground">— not yet determined who it applies to</span>
          </li>
        </ul>
      </div>

      <div className="border rounded bg-muted/30 px-4 py-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
        <label className="flex flex-col gap-1 text-xs">
          <span className="text-muted-foreground">State</span>
          <Combobox
            value={stateFilter}
            onValueChange={(v) => v && setStateFilter(v)}
            options={[
              { value: "all", label: `All states (${merged.length})` },
              ...merged.map<ComboboxOption>((m) => ({
                value: m.state,
                label: m.state,
              })),
            ]}
            searchPlaceholder="Search states…"
            emptyText="No matching states."
          />
        </label>
        <label className="flex flex-col gap-1 text-xs">
          <span className="text-muted-foreground">Cross-cutting umbrella tier</span>
          <Select
            value={audienceFilter}
            onValueChange={(v) => v && setAudienceFilter(v as AudienceFilter)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All tiers</SelectItem>
              {AUDIENCE_KINDS.map((k) => (
                <SelectItem key={k} value={k}>
                  {AUDIENCE_LABEL[k]} {u ? `(${u[k]})` : ""}
                </SelectItem>
              ))}
              <SelectItem value="unclassified">
                Unclassified residual {u ? `(${u.unclassified_in_state})` : ""}
              </SelectItem>
            </SelectContent>
          </Select>
        </label>
      </div>

      {visible.length === 0 ? (
        <p className="text-sm text-muted-foreground">No states match the filter.</p>
      ) : (
        <div className="space-y-3">
          {visible.map((m) => (
            <CombinedStateCard
              key={m.state}
              state={m.state}
              row={m.row}
              umbrella={m.umbrella}
              audienceFilter={activeKinds}
              showUnclassified={showUnclassified}
              profSlug={profSlug}
            />
          ))}
        </div>
      )}
    </div>
  );
}

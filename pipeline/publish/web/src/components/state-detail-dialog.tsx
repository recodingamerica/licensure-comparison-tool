"use client";

import { useMemo, useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import type {
  DiscoveredField,
  DisciplinaryGround,
  EducationTier,
  Row,
  SectionRef,
} from "@/lib/types";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { Eyebrow } from "@/components/ui/eyebrow";
import { SEMANTIC_CLASSES as SC } from "@/lib/web-colors";
import {
  EvidenceRow,
  SearchQueryContext,
  FocusFieldContext,
  BucketContext,
} from "./evidence-row";
import { searchSnippets, humanize } from "@/lib/format";

// Map a clicked grid colId (#34) to the EvidenceRow `label` it corresponds to
// inside the Sheet. Most universal columns share the same string as their row
// label (regulatory_model, issuing_authority, credential_type, …) so identity
// is the default; only the columns whose label uses a different notation are
// listed here. Profession-specific columns are "ps_<name>" and resolve to
// "<name>". Keep aligned with UNVERIFIED_PATHS in profile-view.tsx.
const FOCUS_LABEL_OVERRIDES: Record<string, string> = {
  education_degree: "education.degree_required",
  education_accrediting_body: "education.accrediting_body",
  post_degree_required: "post_degree.required",
  post_degree_duration: "post_degree.duration",
  post_degree_kind: "post_degree.kind",
  renewal_years: "renewal.interval_years",
  ce_required: "CE.required",
  continuing_ed: "CE.required",
  ce_hours_per_period: "CE.hours_per_period",
  ce_period_years: "CE.period_years",
  ce_topical_requirements: "CE.topical_requirements",
  reciprocity_available: "reciprocity.available",
  reciprocity_requirements: "reciprocity.requirements",
  scope_definition: "definition_quote",
  scope_methods: "methods_authorized",
  scope_drug_authority: "drug_authority",
};

function focusColIdToLabel(colId: string | null | undefined): string | null {
  if (!colId) return null;
  if (FOCUS_LABEL_OVERRIDES[colId]) return FOCUS_LABEL_OVERRIDES[colId];
  if (colId.startsWith("ps_")) return colId.slice(3);
  return colId; // identity for the same-named universal columns
}

// The three universal text-bucketed fields, mapped from their map_prep dotted
// path to the Sheet's EvidenceRow label, so the same chip the grid shows above
// a bucketed cell also appears on the matching row inside the Sheet.
const BUCKET_PATH_TO_LABEL: Record<string, string> = {
  "licensure.issuing_authority": "issuing_authority",
  "licensure.education.degree_required": "education.degree_required",
  "licensure.post_degree_experience.duration": "post_degree.duration",
};

// Group a state's disciplinary grounds by their content category (from the
// per-item bucketing pass), largest group first. When no ground carries a
// category (pass not run for this profession), returns a single unlabeled
// group so the flat list renders exactly as before.
function groupGroundsByCategory(
  grounds: DisciplinaryGround[],
): [string, DisciplinaryGround[]][] {
  if (!grounds.some((g) => g.category)) return [["", grounds]];
  const byCat = new Map<string, DisciplinaryGround[]>();
  for (const g of grounds) {
    const cat = g.category || "Uncategorized";
    const arr = byCat.get(cat);
    if (arr) arr.push(g);
    else byCat.set(cat, [g]);
  }
  return Array.from(byCat.entries()).sort((a, b) => b[1].length - a[1].length);
}

const COMPACT_FULL: Record<string, string> = {
  NLC: "Nurse Licensure Compact",
  IMLC: "Interstate Medical Licensure Compact",
  PTC: "Physical Therapy Compact",
  "ASLP-IC": "Audiology and Speech-Language Pathology Interstate Compact",
  "PSY-PACT": "Psychology Interjurisdictional Compact",
  "EMS-C": "EMS Personnel Licensure Interstate Compact",
  "OT-C": "Occupational Therapy Licensure Compact",
  CC: "Counseling Compact",
  "DDH-C": "Dentist and Dental Hygienist Compact",
  "OD-C": "Optometry Licensure Compact",
  "APRN-C": "Advanced Practice Registered Nurse Compact",
};

type Props = {
  rows: Row[];
  fields: DiscoveredField[];
  openState: string | null;
  onOpenChange: (open: boolean) => void;
  // Active query for the "Statute text" column filter, passed down so the
  // Sheet's in-context panels can highlight the user's search instead of
  // the LLM-quote highlights. When empty, the existing quote highlights
  // render unchanged.
  searchQuery?: string;
  // The grid colId the user clicked through (#34). The matching EvidenceRow
  // scrolls into view, highlights, and auto-expands its statute text. Null
  // when the Sheet was opened without a specific field focus.
  focusColId?: string | null;
  // map_prep.text_buckets, used to surface the same per-state bucket chip the
  // grid shows above bucketed cells on the matching Sheet rows (#34).
  textBuckets?: Record<string, { by_state?: Record<string, string> }>;
};

// Renamed visually from "Dialog" → "Sheet" (slide-in side panel) because the
// table now carries the full value set per state — the panel's job is the
// per-claim evidence drilldown (verbatim quote + citation + source link),
// not "all the data for this row" duplication. Keeping the export name
// StateDetailDialog so callers don't need to change.
export function StateDetailDialog({ rows, fields, openState, onOpenChange, searchQuery, focusColId, textBuckets }: Props) {
  const row = useMemo(
    () => rows.find((r) => r.state === openState) || null,
    [rows, openState]
  );

  const focusLabel = useMemo(() => focusColIdToLabel(focusColId), [focusColId]);

  // Per-state bucket chips keyed by EvidenceRow label. Covers the three
  // universal text-bucketed fields plus any profession-specific bucketed list
  // field (path "profession_specific.<name>" → row label "<name>").
  const bucketByLabel = useMemo(() => {
    const out: Record<string, string> = {};
    if (!row || !textBuckets) return out;
    for (const [path, entry] of Object.entries(textBuckets)) {
      const b = entry?.by_state?.[row.state];
      if (!b) continue;
      const label =
        BUCKET_PATH_TO_LABEL[path] ??
        (path.startsWith("profession_specific.")
          ? path.slice("profession_specific.".length)
          : null);
      if (label) out[label] = b;
    }
    return out;
  }, [row, textBuckets]);

  if (!row) {
    return (
      <Sheet open={!!openState} onOpenChange={onOpenChange}>
        <SheetContent side="right" />
      </Sheet>
    );
  }

  // Coverage-gap rows carry no extracted `_full` payload — render the gap
  // summary before touching `_full` below.
  if (row.coverage_gap) {
    return (
      <Sheet open onOpenChange={onOpenChange}>
        <SheetContent side="right" className="w-full sm:max-w-md lg:max-w-xl">
          <SheetHeader>
            <SheetTitle>{row.state} — coverage gap</SheetTitle>
            <SheetDescription>
              {row.coverage_gap_label || "no data"}{" "}
              <code className="ml-2 text-xs">{row.coverage_gap_reason || ""}</code>
            </SheetDescription>
          </SheetHeader>
          {row.coverage_gap_detail && (
            <p className="px-4 text-sm text-muted-foreground">{row.coverage_gap_detail}</p>
          )}
        </SheetContent>
      </Sheet>
    );
  }

  // `_full` is typed as required (src/lib/types.ts), but partial / absence
  // rows can arrive without it. Guard rather than crash the Sheet on click,
  // matching how profile-view.tsx guards `_full` before dereferencing.
  const full = row._full;
  if (!full) {
    return (
      <Sheet open onOpenChange={onOpenChange}>
        <SheetContent side="right" className="w-full sm:max-w-md lg:max-w-xl">
          <SheetHeader>
            <SheetTitle>{row.state}</SheetTitle>
            <SheetDescription>
              No detail available for this row.
            </SheetDescription>
          </SheetHeader>
        </SheetContent>
      </Sheet>
    );
  }

  const lic = full.licensure;
  const scope = full.scope;
  const spec = full.profession_specific;

  const sections: Record<string, SectionRef> = {};
  (row.sections || []).forEach((s) => {
    if (s.citation) {
      sections[s.citation] = s;
      sections[`[${s.citation}]`] = s;
    }
  });

  // Group profession-specific fields by category
  // Keep fields this state DIDN'T address. `fields` is the profession's own discovered
  // schema, so every entry applies to the profession — a missing node means this state's
  // statute is silent, which is a finding. Dropping them made silence look identical to
  // an explicit "no" (issue #103).
  const byCat: Record<string, Array<{ def: DiscoveredField; ev: Evidence | null }>> = {};
  fields.forEach((f) => {
    const ev = spec?.[f.name];
    (byCat[f.category] ||= []).push({ def: f, ev: (ev as Evidence) ?? null });
  });

  return (
    <SearchQueryContext.Provider value={searchQuery ?? ""}>
    <FocusFieldContext.Provider value={focusLabel}>
    <BucketContext.Provider value={bucketByLabel}>
    <Sheet open onOpenChange={onOpenChange}>
      <SheetContent
        side="right"
        // The base SheetContent has `data-[side=right]:sm:max-w-sm` (~384px)
        // which is too narrow for the per-state evidence + statute view —
        // Atharv's issue #12. The `!` modifier wins over the base default.
        className="w-full sm:!max-w-2xl lg:!max-w-[65vw] xl:!max-w-[60vw] p-0 gap-0 flex flex-col"
      >
        <SheetHeader className="border-b px-6 py-4 flex-shrink-0 bg-background">
          <SheetTitle className="text-xl flex items-center gap-3 flex-wrap">
            <span>
              {row.state} — {row._full.profession.replace(/_/g, " ")}
            </span>
            {row.compacts && row.compacts.length > 0 && (
              <span className="flex gap-1 flex-wrap">
                {row.compacts.map((c) => (
                  <Badge
                    key={c}
                    variant="secondary"
                    className="bg-indigo-100 text-indigo-900 hover:bg-indigo-100 font-mono text-xs"
                    title={COMPACT_FULL[c] || c}
                  >
                    {c}
                  </Badge>
                ))}
              </span>
            )}
            {row.data_basis === "verified_absence" && (
              <Badge
                variant="secondary"
                className={`${SC.attention.bg} ${SC.attention.text} ${SC.attention.hoverBg} text-xs`}
                title="This state has no state-level license for this profession. Determined from hand-verified research, not extracted from a statute — see config/verified_absences.yaml."
              >
                Not state-regulated · research-verified
              </Badge>
            )}
          </SheetTitle>
          {row.data_basis === "verified_absence" && (
            <div className={`mt-2 rounded border ${SC.attention.border} ${SC.attention.bg} px-3 py-2 text-xs ${SC.attention.text}`}>
              <b>No state license.</b> Regulated locally / not at the state level
              {row.absence_basis ? ` (${row.absence_basis.replace(/_/g, " ")})` : ""}.
              This row is <b>hand-verified research</b>, not a statute extraction — there is
              no state statute to quote. {row.absence_note}
            </div>
          )}
          <SheetDescription className="text-xs text-muted-foreground">
            Verbatim statute quote and citation for every claim. Click{" "}
            <em>in context</em> on any row to see the surrounding section text
            with the quote highlighted.{" "}
            {(row.browse_section_count ?? 0) > 0 && (
              <a
                href={`/browse/${row.state}/${encodeURIComponent(row._full.profession)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block ml-1 font-mono text-foreground underline hover:no-underline"
              >
                Browse the full statute ↗
              </a>
            )}
          </SheetDescription>
          {row.source_chapter_urls && row.source_chapter_urls.length > 0 && (
            <div className="text-xs font-mono break-all space-y-0.5 mt-1">
              {row.source_chapter_urls.map((u) => (
                <a
                  key={u}
                  href={u}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-foreground block"
                >
                  {u}
                </a>
              ))}
            </div>
          )}
        </SheetHeader>

        <SheetBody
          searchQuery={searchQuery ?? ""}
          sectionText={row.section_text_full ?? ""}
        >
          <Section title="Base licensure">
            <EvidenceRow label="regulatory_model" ev={lic.regulatory_model} sections={sections} />
            <EvidenceRow label="credential_type" ev={lic.credential_type} sections={sections} />
            <EvidenceRow label="is_mandatory" ev={lic.is_mandatory} sections={sections} />
            <EvidenceRow label="title_protection" ev={lic.title_protection} sections={sections} />
            <EvidenceRow label="scope_protection" ev={lic.scope_protection} sections={sections} />
            <EvidenceRow label="license_required" ev={lic.license_required} sections={sections} />
            <EvidenceRow label="issuing_authority" ev={lic.issuing_authority} sections={sections} />
            <EvidenceRow label="age_minimum" ev={lic.age_minimum} sections={sections} />
            <EvidenceRow label="moral_character_required" ev={lic.moral_character_required} sections={sections} />
            {lic.education && (
              <>
                <EvidenceRow label="education.degree_level" ev={lic.education.degree_level} sections={sections} />
                <EvidenceRow label="education.degree_required" ev={lic.education.degree_required} sections={sections} />
                <EvidenceRow label="education.school_approval_basis" ev={lic.education.school_approval_basis} sections={sections} />
                <EvidenceRow label="education.accrediting_body" ev={lic.education.accrediting_body} sections={sections} />
                <EvidenceRow label="education.credential_pegged" ev={lic.education.credential_pegged} sections={sections} />
                <EducationTiers tiers={lic.education.tiers} />
              </>
            )}
            {lic.post_degree_experience && (
              <>
                <EvidenceRow label="post_degree.experience_source" ev={lic.post_degree_experience.experience_source} sections={sections} />
                <EvidenceRow label="post_degree.required" ev={lic.post_degree_experience.required} sections={sections} />
                <EvidenceRow label="post_degree.duration" ev={lic.post_degree_experience.duration} sections={sections} />
                <EvidenceRow label="post_degree.kind" ev={lic.post_degree_experience.kind} sections={sections} />
              </>
            )}
            {lic.renewal && <EvidenceRow label="renewal.interval_years" ev={lic.renewal.interval_years} sections={sections} />}
            {lic.continuing_education && (
              <>
                <EvidenceRow label="CE.required" ev={lic.continuing_education.required} sections={sections} />
                <EvidenceRow label="CE.hours_per_period" ev={lic.continuing_education.hours_per_period} sections={sections} />
                <EvidenceRow label="CE.period_years" ev={lic.continuing_education.period_years} sections={sections} />
                <EvidenceRow label="CE.topical_requirements" ev={lic.continuing_education.topical_requirements} sections={sections} />
              </>
            )}
            {lic.reciprocity && (
              <>
                <EvidenceRow label="reciprocity.available" ev={lic.reciprocity.available} sections={sections} />
                <EvidenceRow label="reciprocity.requirements" ev={lic.reciprocity.requirements} sections={sections} />
              </>
            )}
          </Section>

          {lic.exams && lic.exams.length > 0 && (
            <Section title="Exams">
              {lic.exams.map((e, i) => (
                <EvidenceRow
                  key={i}
                  label={e.name || "exam"}
                  ev={{ value: e.name || "", quote: e.quote || "", citation: e.citation || "" }}
                  sections={sections}
                />
              ))}
            </Section>
          )}

          {lic.disciplinary_grounds && lic.disciplinary_grounds.length > 0 && (
            <Section title="Disciplinary grounds">
              {groupGroundsByCategory(lic.disciplinary_grounds).map(
                ([cat, grounds]) => (
                  <div key={cat} className="mb-2">
                    {cat && (
                      <p className="text-xs font-mono uppercase tracking-wider text-muted-foreground mb-1">
                        {cat} · {grounds.length}
                      </p>
                    )}
                    {grounds.map((g, i) => (
                      <EvidenceRow
                        key={`${cat}-${i}`}
                        label={g.short_label || "ground"}
                        ev={{ value: g.description || "", quote: g.quote || "", citation: g.citation || "" }}
                        sections={sections}
                      />
                    ))}
                  </div>
                ),
              )}
            </Section>
          )}

          {scope && (scope.definition_quote || scope.methods_authorized || scope.drug_authority) && (
            <Section title="Scope of practice">
              <EvidenceRow label="definition_quote" ev={scope.definition_quote} sections={sections} />
              <EvidenceRow label="methods_authorized" ev={scope.methods_authorized} sections={sections} />
              <EvidenceRow label="drug_authority" ev={scope.drug_authority} sections={sections} />
            </Section>
          )}

          {Object.keys(byCat)
            .sort()
            .map((cat) => (
              <Section key={cat} title={cat}>
                {byCat[cat].map(({ def, ev }) => (
                  <EvidenceRow
                    key={def.name}
                    label={def.name}
                    ev={ev}
                    sections={sections}
                    showAbsent
                  />
                ))}
              </Section>
            ))}
        </SheetBody>
      </SheetContent>
    </Sheet>
    </BucketContext.Provider>
    </FocusFieldContext.Provider>
    </SearchQueryContext.Provider>
  );
}

type Evidence = NonNullable<Parameters<typeof EvidenceRow>[0]["ev"]>;

// When the user is searching, the Sheet's primary job becomes "show where
// the match is." We collapse the existing extracted-fields view behind a
// disclosure toggle so it doesn't compete with the snippet panel for
// attention. When not searching, the toggle is hidden and everything
// renders flat — the original behavior.
function SheetBody({
  searchQuery,
  sectionText,
  children,
}: {
  searchQuery: string;
  sectionText: string;
  children: React.ReactNode;
}) {
  const searching = searchQuery.trim().length > 0;
  const [showFields, setShowFields] = useState(false);

  if (!searching) {
    // Plain view: just the extracted-fields rendering, no snippets or
    // toggle — identical to the pre-search experience.
    return (
      <div className="px-6 py-4 space-y-6 overflow-y-auto flex-1">
        {children}
      </div>
    );
  }

  return (
    <div className="px-6 py-4 space-y-4 overflow-y-auto flex-1">
      <StatuteTextMatches query={searchQuery} sectionText={sectionText} />
      <button
        type="button"
        onClick={() => setShowFields((v) => !v)}
        className="flex items-center gap-1 text-xs font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
      >
        {showFields ? (
          <ChevronDown className="size-3" />
        ) : (
          <ChevronRight className="size-3" />
        )}
        {showFields ? "hide extracted fields" : "show extracted fields"}
      </button>
      {showFields && <div className="space-y-6">{children}</div>}
    </div>
  );
}

// Per-class / date-phased education floors (#35). Only renders when the state
// actually has tiers (different floors across classes or a date phase-in);
// `education.degree_level` already carries the single overall floor otherwise.
function EducationTiers({ tiers }: { tiers?: EducationTier[] | null }) {
  if (!tiers || tiers.length === 0) return null;
  return (
    <div className="grid grid-cols-[160px_1fr] md:grid-cols-[180px_1fr] gap-x-3 py-2 border-b border-border/60">
      <code className="text-xs text-muted-foreground font-mono pt-1 break-all">
        education.tiers
      </code>
      <div className="space-y-1.5">
        {tiers.map((t, i) => (
          <div key={i} className="text-sm flex flex-wrap items-baseline gap-x-2">
            <span className="font-medium">{humanize(t.degree_level)}</span>
            <span className="text-muted-foreground">— {t.license_class}</span>
            {t.effective_date && (
              <span className="font-mono text-[11px] text-muted-foreground">
                (from {t.effective_date})
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <Eyebrow as="h3" className="mb-2">
        {title}
      </Eyebrow>
      <div>{children}</div>
    </section>
  );
}

// When the "Statute text" filter has a query, surface every matching snippet
// from this state's combined statute text at the TOP of the Sheet. Each
// snippet shows ~70 chars of context before/after the match with the term
// highlighted yellow. Without this, users had to expand "in context" on
// each Evidence row hoping to stumble onto the match — bad UX.
function StatuteTextMatches({ query, sectionText }: { query: string; sectionText: string }) {
  const q = query.trim();
  const snippets = useMemo(
    () => (q && sectionText ? searchSnippets(q, sectionText) : []),
    [q, sectionText],
  );
  if (!q) return null;
  return (
    <section>
      <Eyebrow as="h3" className="mb-2">
        Statute text matches for{" "}
        <span className="text-foreground">&ldquo;{q}&rdquo;</span>{" "}
        <span className="text-muted-foreground">({snippets.length})</span>
      </Eyebrow>
      {snippets.length === 0 ? (
        <p className="text-xs text-muted-foreground italic">
          No matches in the combined statute text. The row matched on a
          different field — or the filter has caught it via partial match
          that&apos;s already been narrowed away.
        </p>
      ) : (
        <ol className="space-y-2 text-[12px] leading-relaxed">
          {snippets.map((s, i) => (
            <li
              key={i}
              className="bg-yellow-50 border-l-2 border-yellow-300 px-3 py-1.5 rounded"
            >
              <span className="text-muted-foreground">…{s.before}</span>
              <mark className="bg-yellow-300 px-0.5 rounded-sm">{s.match}</mark>
              <span className="text-muted-foreground">{s.after}…</span>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}

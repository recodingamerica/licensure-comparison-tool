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
import { Badge } from "@/components/ui/badge";
import { Eyebrow } from "@/components/ui/eyebrow";
import { SEMANTIC_CLASSES as SC } from "@/lib/web-colors";
import {
  EvidenceRow,
  SearchQueryContext,
  FocusFieldContext,
  AutoExpandContext,
  BucketContext,
} from "./evidence-row";
import { ABSENCE } from "./absence";
import { SHEET_SECTION } from "./sheet-sections";
import { DetailSheet, SheetScrollBody } from "@/components/ui/detail-sheet";
import { FilterBar } from "@/components/ui/filter-bar";
import { searchSnippets, humanize } from "@/lib/format";

// A grid colId that is not itself a record path. Columns carry their own dotted path
// (see cellDef `context.fieldPath` in profile-view), so the only cases left are rules
// rather than a lookup table: profession-specific columns are "ps_<name>", and the
// universal ones share their name with the Sheet row. The 16-entry override table this
// replaced had to be kept in sync by hand with UNVERIFIED_PATHS — a comment in the file
// said so, which is the tell that it shouldn't have existed.
function focusColIdToLabel(colId: string | null | undefined): string | null {
  if (!colId) return null;
  if (colId.startsWith("ps_")) return colId.slice(3);
  return colId;
}

// A record's dotted field path ("licensure.education.degree_level") → the Sheet's row
// label ("education.degree_level"). One translation, used by the bucket chips, by map
// clicks, and by anything else that knows a field by its path. Previously this existed
// only as a 3-entry lookup table, so every new caller either extended the table or
// hand-rolled its own slicing.
const NESTED_LABEL_PREFIX: Record<string, string> = {
  post_degree_experience: "post_degree",
  continuing_education: "CE",
};

/** What the Sheet is filtered to. One value, so no combination can contradict itself. */
type SheetFilter =
  | { kind: "none" }
  | { kind: "field"; label: string }
  | { kind: "category"; label: string }
  | { kind: "section"; label: string };

type EvidenceNode = NonNullable<Parameters<typeof EvidenceRow>[0]["ev"]>;

/**
 * Index every Evidence node in a record by its Sheet row label.
 *
 * The entry points know a field by different names — the grid by colId, a map by dotted
 * record path, the bucket chips by dotted path — but they all have to land on the same
 * row. Rather than each maintaining its own lookup table, they resolve to a label and
 * look it up here. Walks the record once, so it also covers profession-specific fields
 * without anyone enumerating them.
 */
function indexEvidenceByLabel(record: unknown): Record<string, EvidenceNode> {
  const out: Record<string, EvidenceNode> = {};
  const walk = (node: unknown, path: string) => {
    if (!node || typeof node !== "object") return;
    if ("value" in (node as Record<string, unknown>)) {
      const label = fieldPathToLabel(path);
      if (label && !(label in out)) out[label] = node as EvidenceNode;
      return;
    }
    if (Array.isArray(node)) return; // lists (exams, grounds) render as their own sections
    for (const [k, v] of Object.entries(node as Record<string, unknown>)) {
      walk(v, path ? `${path}.${k}` : k);
    }
  };
  walk(record, "");
  return out;
}

export function fieldPathToLabel(path: string): string | null {
  if (!path) return null;
  if (path.startsWith("profession_specific.")) {
    return path.slice("profession_specific.".length);
  }
  if (path.startsWith("scope.")) return path.slice("scope.".length);
  // A bare identifier is already a label — the novel-policies data mixes dotted paths
  // ("profession_specific.x") with unprefixed profession-specific field names. The
  // caller still validates the result against the record and the profession's schema,
  // so an unrecognized name simply won't filter.
  if (!path.includes(".")) return path;
  if (!path.startsWith("licensure.")) return null;
  const rest = path.slice("licensure.".length);
  const dot = rest.indexOf(".");
  if (dot === -1) return rest; // licensure.regulatory_model -> regulatory_model
  const group = rest.slice(0, dot);
  const leaf = rest.slice(dot + 1);
  return `${NESTED_LABEL_PREFIX[group] ?? group}.${leaf}`;
}

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
  // The specific category chip clicked in the grid ("Fraud"). The matching
  // Disciplinary-grounds group scrolls into view and highlights, so the Sheet lands on
  // the items you clicked rather than just the column they live in.
  //
  // Only meaningful together with focusColId: category labels are NOT unique across
  // fields (7 collide today — "Registered Nurse" is a bucket of both license_tiers and
  // lpn_supervision_requirements), so matching on the label alone could highlight a
  // different field's group than the one clicked.
  focusCategory?: string | null;
  // Dotted record path of the field the click was about (the choropleth field a map was
  // showing). The Sheet filters to that one field.
  focusFieldPath?: string | null;
  // A Sheet section the click points at, for columns that summarize a LIST rather than a
  // single field ("Exams" counts a list — no one node to filter to, but there is a
  // section).
  focusSection?: string | null;
  // map_prep.text_buckets, used to surface the same per-state bucket chip the
  // grid shows above bucketed cells on the matching Sheet rows (#34).
  textBuckets?: Record<string, { by_state?: Record<string, string> }>;
};

// Renamed visually from "Dialog" → "Sheet" (slide-in side panel) because the
// table now carries the full value set per state — the panel's job is the
// per-claim evidence drilldown (verbatim quote + citation + source link),
// not "all the data for this row" duplication. Keeping the export name
// StateDetailDialog so callers don't need to change.
export function StateDetailDialog({ rows, fields, openState, onOpenChange, searchQuery, focusColId, focusCategory, focusFieldPath, focusSection, textBuckets }: Props) {
  const row = useMemo(
    () => rows.find((r) => r.state === openState) || null,
    [rows, openState]
  );



  // Scroll the clicked category group into view once the Sheet has painted. Same rAF
  // deferral as EvidenceRow's focused row — the Sheet slides in via a transform, so
  // scrolling before that settles lands in the wrong place.
  // Clicking a category chip FILTERS the Sheet to what you clicked rather than merely
  // highlighting it — with the filter shown and removable, so it can never become an
  // invisible reason you're not seeing everything. Held as local state (seeded from the
  // click) so clearing it restores the full Sheet without reopening.
  //
  // Derived, not mirrored into state: we track only which request the user DISMISSED.
  // Mirroring the prop into state needs a sync effect, and a setState inside an effect
  // cascades renders. Keying the dismissal by state+category means clearing one filter
  // doesn't suppress the next chip you click.
  //
  // Scoped to the disciplinary-categories column, the only place these groups render.
  // Category labels are not unique across fields, so matching on the label alone could
  // filter to a different field's group than the one clicked.
  const requestedCategory =
    focusColId === "disciplinary_categories" ? focusCategory ?? null : null;
  // A field filter (from a map click) and a category filter are the same idea applied to
  // different things, so they share one dismissal key — clearing is one gesture either way.
  // One resolution path for every entry point: map click (dotted path) and grid cell
  // click (colId) both become a label, and we only filter when that label actually
  // resolves to a node in this record — so a computed/non-field column (coverage_gap,
  // statute text) falls back to the full Sheet instead of filtering to nothing.
  const evidenceByLabel = useMemo(
    () => (row?._full ? indexEvidenceByLabel(row._full) : {}),
    [row],
  );
  const candidateLabel = focusFieldPath
    ? fieldPathToLabel(focusFieldPath)
    : focusColIdToLabel(focusColId);
  // Filter when the label names a field we KNOW about — either this record has a value
  // for it, or it's in the profession's discovered schema. Asking only "does this record
  // have a node?" wrongly refused to filter on a field the state doesn't address, which
  // is precisely the case where the user most needs to be told it isn't addressed.
  // Still refuses computed columns (exams_count, statute_text), which are neither.
  const knownFieldLabels = useMemo(
    () => new Set(fields.map((f) => f.name)),
    [fields],
  );
  // An explicit fieldPath is an ASSERTION from a column def or a map spec that the field
  // exists, so it's trusted as-is. A colId is only a guess at a label and still has to
  // prove itself. Without this split, clicking a column whose value happens to be null
  // (post_degree.duration on a state that doesn't set one) refused to filter — the
  // field is real, the state just has nothing for it, which is what we should say.
  const requestedFieldLabel = !candidateLabel
    ? null
    : focusFieldPath ||
        candidateLabel in evidenceByLabel ||
        knownFieldLabels.has(candidateLabel)
      ? candidateLabel
      : null;
  // ── The filter, as ONE value ────────────────────────────────────────────────────
  // Previously this was four loose booleans (filterActive / filterCategory /
  // filterFieldLabel / filterSection) and five hand-written gates that each spelled the
  // visibility rule slightly differently. That is where today's bugs came from: one gate
  // hid the Disciplinary-grounds section during a CATEGORY filter (empty Sheet), and
  // another didn't use the shared helper at all. A discriminated union plus one
  // exhaustive predicate makes those states unrepresentable — add a filter kind and
  // TypeScript forces every case to be answered here, once.
  const requestKey = requestedCategory
    ? `${openState}:cat:${requestedCategory}`
    : requestedFieldLabel
      ? `${openState}:field:${requestedFieldLabel}`
      : focusSection
        ? `${openState}:section:${focusSection}`
        : null;
  const [dismissedKey, setDismissedKey] = useState<string | null>(null);
  const dismissed = !!requestKey && dismissedKey === requestKey;

  const filter: SheetFilter =
    !requestKey || dismissed
      ? { kind: "none" }
      : requestedCategory
        ? { kind: "category", label: requestedCategory }
        : requestedFieldLabel
          ? { kind: "field", label: requestedFieldLabel }
          : { kind: "section", label: focusSection as string };

  const filterActive = filter.kind !== "none";

  // The ONE visibility rule. Every section gate calls this and nothing else.
  const showsSection = (name: string): boolean => {
    switch (filter.kind) {
      case "none":
        return true;
      // A field filter renders its own one-row section instead of any of these.
      case "field":
        return false;
      // A category lives INSIDE Disciplinary grounds — that section has to stay.
      case "category":
        return name === SHEET_SECTION.disciplinaryGrounds;
      case "section":
        return name === filter.label;
    }
  };

  // The row that auto-expands is the row you filtered TO, not whatever the colId spelled.
  // Expansion used to depend on how the click arrived: an identity column expanded
  // because colId == row label, a declared-path column did not ("education_degree" vs
  // "education.degree_required"), and map / matrix / policy clicks never did, having no
  // colId at all.
  const focusLabel =
    filter.kind === "field" ? filter.label : focusColIdToLabel(focusColId);

  // Per-state bucket chips keyed by EvidenceRow label. Covers the three
  // universal text-bucketed fields plus any profession-specific bucketed list
  // field (path "profession_specific.<name>" → row label "<name>").
  const bucketByLabel = useMemo(() => {
    const out: Record<string, string> = {};
    if (!row || !textBuckets) return out;
    for (const [path, entry] of Object.entries(textBuckets)) {
      const b = entry?.by_state?.[row.state];
      if (!b) continue;
      const label = fieldPathToLabel(path);
      if (label) out[label] = b;
    }
    return out;
  }, [row, textBuckets]);

  if (!row) {
    return (
      <DetailSheet open={!!openState} onOpenChange={onOpenChange} title="" />
    );
  }

  // Coverage-gap rows carry no extracted `_full` payload — render the gap
  // summary before touching `_full` below.
  if (row.coverage_gap) {
    return (
      <DetailSheet
        open
        onOpenChange={onOpenChange}
        title={`${row.state} — coverage gap`}
        description={
          <>
            {row.coverage_gap_label || ABSENCE["no-statute"].label}{" "}
            <code className="ml-2 text-xs">{row.coverage_gap_reason || ""}</code>
          </>
        }
      >
        {row.coverage_gap_detail && (
          <SheetScrollBody>
            <p className="text-sm text-muted-foreground">{row.coverage_gap_detail}</p>
          </SheetScrollBody>
        )}
      </DetailSheet>
    );
  }

  // `_full` is typed as required (src/lib/types.ts), but partial / absence
  // rows can arrive without it. Guard rather than crash the Sheet on click,
  // matching how profile-view.tsx guards `_full` before dereferencing.
  const full = row._full;
  if (!full) {
    return (
      <DetailSheet
        open
        onOpenChange={onOpenChange}
        title={row.state}
        description="No detail available for this row."
      />
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
    <AutoExpandContext.Provider value={filterActive}>
    <BucketContext.Provider value={bucketByLabel}>
    <DetailSheet
      open
      onOpenChange={onOpenChange}
      width="wide"
      title={
          <span className="flex items-center gap-3 flex-wrap">
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
          </span>
      }
      headerExtra={
        <>
          {row.data_basis === "verified_absence" && (
            <div className={`mt-2 rounded border ${SC.attention.border} ${SC.attention.bg} px-3 py-2 text-xs ${SC.attention.text}`}>
              <b>No state license.</b> Regulated locally / not at the state level
              {row.absence_basis ? ` (${row.absence_basis.replace(/_/g, " ")})` : ""}.
              This row is <b>hand-verified research</b>, not a statute extraction — there is
              no state statute to quote. {row.absence_note}
            </div>
          )}
          <div className="text-xs text-muted-foreground">
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
          </div>
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
        </>
      }
    >
        <SheetBody
          searchQuery={searchQuery ?? ""}
          sectionText={row.section_text_full ?? ""}
        >
          {filterActive && (
            <FilterBar
              label={filter.kind === "field" ? humanize(filter.label) : filter.label}
              source={
                filter.kind === "category"
                  ? "from Disciplinary categories"
                  : filter.kind === "section"
                    ? "— one section"
                    : "— one field"
              }
              onClear={() => setDismissedKey(requestKey)}
            />
          )}
          {/* Filtered to one field (a map click): render just that field's row, resolved
              from the record by its dotted path. `showAbsent` so a state the map colored
              "no data" still explains itself instead of opening an empty Sheet. */}
          {filter.kind === "field" && (
            <Section title={humanize(filter.label)}>
              <EvidenceRow
                label={filter.label}
                ev={evidenceByLabel[filter.label]}
                sections={sections}
                showAbsent
              />
            </Section>
          )}
          {showsSection(SHEET_SECTION.baseLicensure) && (
          <Section title={SHEET_SECTION.baseLicensure}>
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
            {/* These had no row at all — the table showed advisory-board and renewal-fee
                values whose quote and citation were unreachable anywhere in the UI. */}
            <EvidenceRow label="renewal_fee_usd" ev={lic.renewal_fee_usd} sections={sections} />
            <EvidenceRow label="national_certification" ev={lic.national_certification} sections={sections} />
            <EvidenceRow label="national_association" ev={lic.national_association} sections={sections} />
            {lic.advisory_board && (
              <>
                <EvidenceRow label="advisory_board.exists" ev={lic.advisory_board.exists} sections={sections} />
                <EvidenceRow label="advisory_board.name" ev={lic.advisory_board.name} sections={sections} />
                <EvidenceRow label="advisory_board.authority" ev={lic.advisory_board.authority} sections={sections} />
              </>
            )}
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
          )}

          {showsSection(SHEET_SECTION.exams) && lic.exams && lic.exams.length > 0 && (
            <Section title={SHEET_SECTION.exams}>
              {lic.exams.map((e, i) => (
                <EvidenceRow
                  key={i}
                  label={e.name || "exam"}
                  // Spread first: the build attaches quote_spans (the highlight), plus
                  // unverified / approximate, to the ITEM. Rebuilding a bare
                  // {value,quote,citation} silently dropped all three, so a list item
                  // could never highlight or show a verification badge no matter what
                  // the data said.
                  ev={{ ...e, value: e.name || "", quote: e.quote || "", citation: e.citation || "" }}
                  sections={sections}
                />
              ))}
            </Section>
          )}

          {showsSection(SHEET_SECTION.disciplinaryGrounds) && lic.disciplinary_grounds && lic.disciplinary_grounds.length > 0 && (
            <Section title={SHEET_SECTION.disciplinaryGrounds}>
              {groupGroundsByCategory(lic.disciplinary_grounds)
                .filter(([cat]) => filter.kind !== "category" || cat === filter.label)
                .map(
                ([cat, grounds]) => (
                  <div
                    key={cat}
                    data-category-group={cat || undefined}
                    className="mb-2"
                  >
                    {cat && (
                      <p className="text-xs font-mono uppercase tracking-wider text-muted-foreground mb-1">
                        {cat} · {grounds.length}
                      </p>
                    )}
                    {grounds.map((g, i) => (
                      <EvidenceRow
                        key={`${cat}-${i}`}
                        label={g.short_label || "ground"}
                        // Spread first — see the exams row above. Without it the
                        // ground's quote_spans / unverified never reach the UI.
                        ev={{ ...g, value: g.description || "", quote: g.quote || "", citation: g.citation || "" }}
                        sections={sections}
                      />
                    ))}
                  </div>
                ),
              )}
            </Section>
          )}

          {showsSection(SHEET_SECTION.scopeOfPractice) && scope && (scope.definition_quote || scope.methods_authorized || scope.drug_authority) && (
            <Section title={SHEET_SECTION.scopeOfPractice}>
              <EvidenceRow label="definition_quote" ev={scope.definition_quote} sections={sections} />
              <EvidenceRow label="methods_authorized" ev={scope.methods_authorized} sections={sections} />
              <EvidenceRow label="drug_authority" ev={scope.drug_authority} sections={sections} />
            </Section>
          )}

          {Object.keys(byCat)
            .sort()
            // Profession-specific groups are sections too, so they obey the same rule.
            .filter((cat) => showsSection(cat))
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
    </DetailSheet>
    </BucketContext.Provider>
    </AutoExpandContext.Provider>
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

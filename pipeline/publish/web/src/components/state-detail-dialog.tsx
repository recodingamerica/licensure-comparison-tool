"use client";

import { useMemo, useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import type { DiscoveredField, Row, SectionRef } from "@/lib/types";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { EvidenceRow, SearchQueryContext } from "./evidence-row";
import { searchSnippets } from "@/lib/format";

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
};

// Renamed visually from "Dialog" → "Sheet" (slide-in side panel) because the
// table now carries the full value set per state — the panel's job is the
// per-claim evidence drilldown (verbatim quote + citation + source link),
// not "all the data for this row" duplication. Keeping the export name
// StateDetailDialog so callers don't need to change.
export function StateDetailDialog({ rows, fields, openState, onOpenChange, searchQuery }: Props) {
  const row = useMemo(
    () => rows.find((r) => r.state === openState) || null,
    [rows, openState]
  );

  if (!row) {
    return (
      <Sheet open={!!openState} onOpenChange={onOpenChange}>
        <SheetContent side="right" />
      </Sheet>
    );
  }

  const lic = row._full.licensure;
  const scope = row._full.scope;
  const spec = row._full.profession_specific;

  const sections: Record<string, SectionRef> = {};
  (row.sections || []).forEach((s) => {
    if (s.citation) {
      sections[s.citation] = s;
      sections[`[${s.citation}]`] = s;
    }
  });

  if (row.coverage_gap) {
    return (
      <Sheet open onOpenChange={onOpenChange}>
        <SheetContent side="right" className="sm:max-w-md">
          <SheetHeader>
            <SheetTitle>{row.state} — coverage gap</SheetTitle>
            <SheetDescription>
              {row.coverage_gap_label || "no data"}{" "}
              <code className="ml-2 text-xs">{row.coverage_gap_reason || ""}</code>
            </SheetDescription>
          </SheetHeader>
        </SheetContent>
      </Sheet>
    );
  }

  // Group profession-specific fields by category
  const byCat: Record<string, Array<{ def: DiscoveredField; ev: Evidence }>> = {};
  fields.forEach((f) => {
    const ev = spec?.[f.name];
    if (!ev) return;
    (byCat[f.category] ||= []).push({ def: f, ev: ev as Evidence });
  });

  return (
    <SearchQueryContext.Provider value={searchQuery ?? ""}>
    <Sheet open onOpenChange={onOpenChange}>
      <SheetContent
        side="right"
        className="w-full sm:max-w-2xl lg:max-w-4xl p-0 gap-0 flex flex-col"
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
          </SheetTitle>
          <SheetDescription className="text-xs text-muted-foreground">
            Verbatim statute quote and citation for every claim. Click{" "}
            <em>in context</em> on any row to see the surrounding section text
            with the quote highlighted.
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
                <EvidenceRow label="education.degree_required" ev={lic.education.degree_required} sections={sections} />
                <EvidenceRow label="education.accrediting_body" ev={lic.education.accrediting_body} sections={sections} />
              </>
            )}
            {lic.post_degree_experience && (
              <>
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
              {lic.disciplinary_grounds.map((g, i) => (
                <EvidenceRow
                  key={i}
                  label={g.short_label || "ground"}
                  ev={{ value: g.description || "", quote: g.quote || "", citation: g.citation || "" }}
                  sections={sections}
                />
              ))}
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
                  <EvidenceRow key={def.name} label={def.name} ev={ev} sections={sections} />
                ))}
              </Section>
            ))}
        </SheetBody>
      </SheetContent>
    </Sheet>
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

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h3 className="text-xs font-mono uppercase tracking-widest text-muted-foreground mb-2">
        {title}
      </h3>
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
      <h3 className="text-xs font-mono uppercase tracking-widest text-muted-foreground mb-2">
        Statute text matches for{" "}
        <span className="text-foreground">&ldquo;{q}&rdquo;</span>{" "}
        <span className="text-muted-foreground">({snippets.length})</span>
      </h3>
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

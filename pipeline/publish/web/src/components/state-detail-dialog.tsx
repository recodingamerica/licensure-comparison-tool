"use client";

import { useMemo } from "react";
import type { DiscoveredField, Row, SectionRef } from "@/lib/types";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { EvidenceRow } from "./evidence-row";

type Props = {
  rows: Row[];
  fields: DiscoveredField[];
  openState: string | null;
  onOpenChange: (open: boolean) => void;
};

export function StateDetailDialog({ rows, fields, openState, onOpenChange }: Props) {
  const row = useMemo(
    () => rows.find((r) => r.state === openState) || null,
    [rows, openState]
  );

  if (!row) {
    return (
      <Dialog open={!!openState} onOpenChange={onOpenChange}>
        <DialogContent />
      </Dialog>
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
      <Dialog open onOpenChange={onOpenChange}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{row.state} — coverage gap</DialogTitle>
            <DialogDescription>
              {row.coverage_gap_label || "no data"}{" "}
              <code className="ml-2 text-xs">{row.coverage_gap_reason || ""}</code>
            </DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
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
    <Dialog open onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl md:max-w-3xl lg:max-w-4xl max-h-[85vh] overflow-y-auto p-0 gap-0 w-[95vw]">
        <DialogHeader className="border-b px-6 py-4 sticky top-0 bg-background z-10">
          <DialogTitle className="text-xl">
            {row.state} — {row._full.profession.replace(/_/g, " ")}
          </DialogTitle>
          {row.source_chapter_urls && row.source_chapter_urls.length > 0 && (
            <DialogDescription className="text-xs font-mono break-all">
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
            </DialogDescription>
          )}
        </DialogHeader>

        <div className="px-6 py-4 space-y-6">
          <Section title="Base licensure">
            <EvidenceRow label="regulatory_model" ev={lic.regulatory_model} sections={sections} />
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
        </div>
      </DialogContent>
    </Dialog>
  );
}

type Evidence = NonNullable<Parameters<typeof EvidenceRow>[0]["ev"]>;

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

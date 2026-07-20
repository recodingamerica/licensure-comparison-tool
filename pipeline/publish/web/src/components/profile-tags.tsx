"use client";

// Profile "Tags" tab — renders this profession's section of the shared
// tag_sheet.json (the same data /reports/tag-sheet uses), so the per-field
// bucket tags (incl. per-item discipline) are visible on the profile page.
// Self-contained on purpose: it reads its own copy of the payload and does
// not touch the existing profile table / map / statutes code paths.
//
// Atharv #76: clicking a tag now opens a right-side Sheet with the full
// per-state breakdown (matching the home /reports/tag-sheet panel), instead
// of a cramped hover popover that was hard to read in depth.

import { useEffect, useState } from "react";
import { Eyebrow } from "@/components/ui/eyebrow";
import { type Field, type ProfData } from "@/lib/tag-sheet";
import { TagBreakdownSheet } from "@/components/tag-breakdown-sheet";

type Payload = { generated_at: string; data: ProfData[] };

type PanelTarget = { field: Field; tagLabel: string };

export function ProfileTags({ professionId }: { professionId: string }) {
  const [prof, setProf] = useState<ProfData | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "absent" | "error">(
    "loading",
  );
  const [panel, setPanel] = useState<PanelTarget | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch("/data/tag_sheet.json")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d: Payload) => {
        if (cancelled) return;
        const p = d.data.find((x) => x.profession === professionId) ?? null;
        setProf(p);
        setState(p ? "ready" : "absent");
      })
      .catch(() => {
        if (!cancelled) setState("error");
      });
    return () => {
      cancelled = true;
    };
  }, [professionId]);

  if (state === "loading")
    return <p className="text-sm text-muted-foreground">Loading…</p>;
  if (state === "error")
    return (
      <p className="text-sm text-muted-foreground">
        Couldn&apos;t load field tags.
      </p>
    );
  if (state === "absent" || !prof)
    return (
      <p className="text-sm text-muted-foreground">
        No bucketed field tags for this profession yet.
      </p>
    );

  const priority = prof.fields.filter((f) => f.priority);
  const other = prof.fields.filter((f) => !f.priority);
  const onOpenTag = (field: Field, tagLabel: string) =>
    setPanel({ field, tagLabel });

  return (
    <div className="max-w-4xl">
      <p className="text-muted-foreground mb-6 text-sm max-w-3xl">
        Plain-English tags for this profession&apos;s fields, derived by
        clustering each field&apos;s actual state values into a handful of
        buckets. Click a tag to open its full per-state breakdown. Same data as
        the{" "}
        <a href="/reports/tag-sheet" className="underline">
          Field Tag Sheet
        </a>
        .
      </p>

      <SectionHeading>Priority fields</SectionHeading>
      {priority.map((f) => (
        <FieldBlock key={f.label} field={f} onOpenTag={onOpenTag} />
      ))}

      {other.length > 0 && (
        <>
          <SectionHeading>Other bucketed fields</SectionHeading>
          {other.map((f) => (
            <FieldBlock key={f.label} field={f} onOpenTag={onOpenTag} />
          ))}
        </>
      )}

      <TagBreakdownSheet
        field={panel?.field ?? null}
        tagLabel={panel?.tagLabel ?? null}
        description={
          panel ? `${prof.profession} — full per-state breakdown` : ""
        }
        noun="grounds"
        onClose={() => setPanel(null)}
      />
    </div>
  );
}

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <Eyebrow as="h3" className="border-b pb-2 mt-8 mb-4">
      {children}
    </Eyebrow>
  );
}

function FieldBlock({
  field,
  onOpenTag,
}: {
  field: Field;
  onOpenTag: (field: Field, tagLabel: string) => void;
}) {
  return (
    <section className="mb-7">
      <h4 className="text-base font-medium mb-1">{field.label}</h4>
      {!field.present && (
        <p className="text-sm text-muted-foreground">No bucketed tags.</p>
      )}
      {field.subfields.map((sf) => (
        <div key={sf.field_name} className="mb-3">
          <p className="text-xs font-mono text-muted-foreground mb-2">
            {sf.field_name} · {sf.unit} per tag ·{" "}
            <span className="text-muted-foreground/70">
              click a tag for its breakdown
            </span>
          </p>
          <div className="flex flex-wrap gap-2">
            {sf.tags.map((t) => (
              <button
                key={t.label}
                type="button"
                onClick={() => onOpenTag(field, t.label)}
                className="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-sm cursor-pointer hover:border-foreground/40 hover:bg-muted/40 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                {t.label}
                <span className="font-mono text-xs text-muted-foreground">
                  {t.count}
                </span>
              </button>
            ))}
          </div>
          {sf.rationale && (
            <p className="text-xs text-muted-foreground mt-2 max-w-3xl">
              {sf.rationale}
            </p>
          )}
        </div>
      ))}
    </section>
  );
}

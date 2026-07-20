"use client";

import { BackLink } from "@/components/ui/back-link";
import { Eyebrow } from "@/components/ui/eyebrow";
import { ErrorBanner } from "@/components/ui/error-banner";
import { useEffect, useState, type ReactNode } from "react";
import { type Field, type ProfData } from "@/lib/tag-sheet";
import { TagBreakdownSheet } from "@/components/tag-breakdown-sheet";

// Shape of `public/data/tag_sheet.json` — produced by
// `python -m pipeline.publish.build_tag_sheet`. The tag-sheet page adds
// concepts/professions on top of the shared per-profession shapes.
type Payload = {
  generated_at: string;
  concepts: string[];
  professions: string[];
  data: ProfData[];
};

// What the pinned breakdown panel renders: the whole field, with the tag the
// user clicked highlighted/scrolled into view.
type PanelTarget = { profession: string; field: Field; tagLabel: string | null };

function profLabel(key: string): string {
  return key
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

export default function TagSheetPage() {
  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string>("");
  const [panel, setPanel] = useState<PanelTarget | null>(null);

  useEffect(() => {
    fetch("/data/tag_sheet.json")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d: Payload) => {
        setData(d);
        // Default to optometry (the field we focused on) when present.
        setSelected(
          d.professions.includes("optometry")
            ? "optometry"
            : d.professions[0] ?? "",
        );
      })
      .catch((e) => setError(String(e)));
  }, []);

  const prof = data?.data.find((p) => p.profession === selected) ?? null;

  // Switching profession closes a stale panel (its field belongs to the old one).
  const onSelectProf = (key: string) => {
    setSelected(key);
    setPanel(null);
  };

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <BackLink href="/">home</BackLink>

      <Eyebrow className="mt-6">Report</Eyebrow>
      <h1 className="text-3xl font-semibold tracking-tight mt-1 mb-2">
        Field tag sheet
      </h1>
      <p className="text-muted-foreground max-w-3xl mb-6">
        Plain-English tags for each profession&apos;s key licensure fields,
        derived by clustering the actual state values for each field into a
        handful of buckets (no per-row hand-curation). Counts are states per tag
        — or disciplinary grounds per tag, for Discipline. Scope wording is
        profession-specific, so the underlying field name varies.{" "}
        <span className="text-foreground">
          Click any tag to pin its full breakdown in a side panel.
        </span>
      </p>

      {error && (
        <ErrorBanner>Failed to load tag sheet: {error}</ErrorBanner>
      )}

      {!data && !error && (
        <p className="text-sm text-muted-foreground">Loading…</p>
      )}

      {data && (
        <>
          <div className="flex items-center gap-3 mb-6">
            <label
              htmlFor="prof"
              className="text-xs font-mono uppercase tracking-widest text-muted-foreground"
            >
              Profession
            </label>
            <select
              id="prof"
              value={selected}
              onChange={(e) => onSelectProf(e.target.value)}
              className="rounded border bg-background px-3 py-1.5 text-sm"
            >
              {data.professions.map((p) => (
                <option key={p} value={p}>
                  {profLabel(p)}
                </option>
              ))}
            </select>
            <span className="text-xs font-mono text-muted-foreground">
              Generated {new Date(data.generated_at).toLocaleString()}
            </span>
          </div>

          {prof && (
            <>
              <SectionHeading>Priority fields</SectionHeading>
              {prof.fields
                .filter((f) => f.priority)
                .map((field) => (
                  <FieldBlock
                    key={field.label}
                    field={field}
                    onOpenTag={(tagLabel) =>
                      setPanel({ profession: selected, field, tagLabel })
                    }
                  />
                ))}

              {prof.fields.some((f) => !f.priority) && (
                <>
                  <SectionHeading>Other bucketed fields</SectionHeading>
                  <p className="text-sm text-muted-foreground -mt-3 mb-5 max-w-3xl">
                    Every other field the bucketing pass tagged for this
                    profession.
                  </p>
                  {prof.fields
                    .filter((f) => !f.priority)
                    .map((field) => (
                      <FieldBlock
                        key={field.label}
                        field={field}
                        onOpenTag={(tagLabel) =>
                          setPanel({ profession: selected, field, tagLabel })
                        }
                      />
                    ))}
                </>
              )}
            </>
          )}
        </>
      )}

      <TagBreakdownSheet
        field={panel?.field ?? null}
        tagLabel={panel?.tagLabel ?? null}
        description={
          panel
            ? `${profLabel(panel.profession)} — full per-state breakdown`
            : ""
        }
        copyHeader={panel ? profLabel(panel.profession) : undefined}
        onClose={() => setPanel(null)}
      />
    </main>
  );
}

function SectionHeading({ children }: { children: ReactNode }) {
  return (
    <Eyebrow as="h2" className="border-b pb-2 mt-10 mb-5">
      {children}
    </Eyebrow>
  );
}

function FieldBlock({
  field,
  onOpenTag,
}: {
  field: Field;
  onOpenTag: (tagLabel: string) => void;
}) {
  return (
    <section className="mb-8">
      <h3 className="text-base font-medium mb-1">{field.label}</h3>
      {!field.present && (
        <p className="text-sm text-muted-foreground">
          No bucketed tags for this field (data too sparse or not yet run).
        </p>
      )}
      {field.subfields.map((sf) => (
        <div key={sf.field_name} className="mb-4">
          <p className="text-xs font-mono text-muted-foreground mb-2">
            {sf.field_name} · {sf.unit} per tag ·{" "}
            <span className="text-muted-foreground/70">
              click a tag to pin its breakdown
            </span>
          </p>
          <div className="flex flex-wrap gap-2">
            {sf.tags.map((t) => (
              <button
                key={t.label}
                type="button"
                onClick={() => onOpenTag(t.label)}
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

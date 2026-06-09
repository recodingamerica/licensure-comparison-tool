"use client";

import Link from "next/link";
import { useEffect, useState, type ReactNode } from "react";

// Shape of `public/data/tag_sheet.json` — produced by
// `python -m pipeline.publish.build_tag_sheet`.
type Tag = { label: string; count: number; states?: number };
type SubField = {
  field_name: string;
  kind: "scalar" | "per_item";
  unit: string;
  rationale: string;
  tags: Tag[];
  assignments: { state: string; bucket: string }[];
};
type Field = {
  label: string;
  priority: boolean;
  present: boolean;
  subfields: SubField[];
};
type ProfData = { profession: string; fields: Field[] };
type Payload = {
  generated_at: string;
  concepts: string[];
  professions: string[];
  data: ProfData[];
};

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

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <Link
        href="/"
        className="text-xs font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
      >
        ← home
      </Link>

      <p className="mt-6 text-xs font-mono tracking-widest uppercase text-muted-foreground">
        Report
      </p>
      <h1 className="text-3xl font-semibold tracking-tight mt-1 mb-2">
        Field tag sheet
      </h1>
      <p className="text-muted-foreground max-w-3xl mb-6">
        Plain-English tags for each profession&apos;s key licensure fields,
        derived by clustering the actual state values for each field into a
        handful of buckets (no per-row hand-curation). Counts are states per tag
        — or disciplinary grounds per tag, for Discipline. Scope wording is
        profession-specific, so the underlying field name varies.
      </p>

      {error && (
        <div className="rounded border border-destructive bg-destructive/5 px-4 py-3 text-sm text-destructive">
          Failed to load tag sheet: {error}
        </div>
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
              onChange={(e) => setSelected(e.target.value)}
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
                  <FieldBlock key={field.label} field={field} />
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
                      <FieldBlock key={field.label} field={field} />
                    ))}
                </>
              )}
            </>
          )}
        </>
      )}
    </main>
  );
}

function SectionHeading({ children }: { children: ReactNode }) {
  return (
    <h2 className="text-xs font-mono uppercase tracking-widest text-muted-foreground border-b pb-2 mt-10 mb-5">
      {children}
    </h2>
  );
}

function FieldBlock({ field }: { field: Field }) {
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
            {sf.field_name} · {sf.unit} per tag
          </p>
          <div className="flex flex-wrap gap-2">
            {sf.tags.map((t) => (
              <span
                key={t.label}
                className="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-sm"
                title={
                  sf.kind === "per_item" && t.states !== undefined
                    ? `${t.count} grounds across ${t.states} states`
                    : `${t.count} states`
                }
              >
                {t.label}
                <span className="font-mono text-xs text-muted-foreground">
                  {t.count}
                </span>
              </span>
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

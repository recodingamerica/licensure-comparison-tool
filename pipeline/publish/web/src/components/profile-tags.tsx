"use client";

// Profile "Tags" tab — renders this profession's section of the shared
// tag_sheet.json (the same data /reports/tag-sheet uses), so the per-field
// bucket tags (incl. per-item discipline) are visible on the profile page.
// Self-contained on purpose: it reads its own copy of the payload and does
// not touch the existing profile table / map / statutes code paths.

import { useEffect, useState } from "react";

type Tag = { label: string; count: number; states?: number };
type Assignment = { state: string; bucket: string; text: string };
type SubField = {
  field_name: string;
  kind: "scalar" | "per_item";
  unit: string;
  rationale: string;
  tags: Tag[];
  assignments: Assignment[];
};
type Field = {
  label: string;
  priority: boolean;
  present: boolean;
  subfields: SubField[];
};
type ProfData = { profession: string; fields: Field[] };
type Payload = { generated_at: string; data: ProfData[] };

export function ProfileTags({ professionId }: { professionId: string }) {
  const [prof, setProf] = useState<ProfData | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "absent" | "error">(
    "loading",
  );

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

  return (
    <div className="max-w-4xl">
      <p className="text-muted-foreground mb-6 text-sm max-w-3xl">
        Plain-English tags for this profession&apos;s fields, derived by
        clustering each field&apos;s actual state values into a handful of
        buckets. Hover a tag to see which states fall under it and their
        original text. Same data as the{" "}
        <a href="/reports/tag-sheet" className="underline">
          Field Tag Sheet
        </a>
        .
      </p>

      <SectionHeading>Priority fields</SectionHeading>
      {priority.map((f) => (
        <FieldBlock key={f.label} field={f} />
      ))}

      {other.length > 0 && (
        <>
          <SectionHeading>Other bucketed fields</SectionHeading>
          {other.map((f) => (
            <FieldBlock key={f.label} field={f} />
          ))}
        </>
      )}
    </div>
  );
}

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-xs font-mono uppercase tracking-widest text-muted-foreground border-b pb-2 mt-8 mb-4">
      {children}
    </h3>
  );
}

function FieldBlock({ field }: { field: Field }) {
  return (
    <section className="mb-7">
      <h4 className="text-base font-medium mb-1">{field.label}</h4>
      {!field.present && (
        <p className="text-sm text-muted-foreground">No bucketed tags.</p>
      )}
      {field.subfields.map((sf) => {
        const byBucket = new Map<string, Assignment[]>();
        for (const a of sf.assignments) {
          const arr = byBucket.get(a.bucket);
          if (arr) arr.push(a);
          else byBucket.set(a.bucket, [a]);
        }
        return (
          <div key={sf.field_name} className="mb-3">
            <p className="text-xs font-mono text-muted-foreground mb-2">
              {sf.field_name} · {sf.unit} per tag ·{" "}
              <span className="text-muted-foreground/70">
                hover a tag for details
              </span>
            </p>
            <div className="flex flex-wrap gap-2">
              {sf.tags.map((t) => (
                <TagChip
                  key={t.label}
                  tag={t}
                  kind={sf.kind}
                  members={byBucket.get(t.label) ?? []}
                />
              ))}
            </div>
            {sf.rationale && (
              <p className="text-xs text-muted-foreground mt-2 max-w-3xl">
                {sf.rationale}
              </p>
            )}
          </div>
        );
      })}
    </section>
  );
}

function TagChip({
  tag,
  kind,
  members,
}: {
  tag: Tag;
  kind: "scalar" | "per_item";
  members: Assignment[];
}) {
  const summary =
    kind === "per_item" && tag.states !== undefined
      ? `${tag.count} grounds across ${tag.states} states`
      : `${tag.count} states`;
  return (
    <span className="relative group inline-flex">
      <span className="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-sm cursor-default group-hover:border-foreground/40 group-hover:bg-muted/40">
        {tag.label}
        <span className="font-mono text-xs text-muted-foreground">
          {tag.count}
        </span>
      </span>
      {members.length > 0 && (
        <div className="invisible group-hover:visible absolute z-50 left-0 top-full mt-1 w-96 max-h-72 overflow-auto rounded-lg border bg-popover text-popover-foreground shadow-lg p-3">
          <p className="text-xs font-medium mb-2">
            {tag.label}{" "}
            <span className="font-normal text-muted-foreground">
              — {summary}
            </span>
          </p>
          <ul className="space-y-1.5">
            {members.map((m, i) => (
              <li key={`${m.state}-${i}`} className="text-xs leading-snug">
                <span className="font-mono font-semibold mr-1.5">
                  {m.state}
                </span>
                <span className="text-muted-foreground">{m.text}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </span>
  );
}

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
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import {
  type Tag,
  type SubField,
  type Field,
  type ProfData,
  groupByBucket,
} from "@/lib/tag-sheet";

type Payload = { generated_at: string; data: ProfData[] };

type PanelTarget = { field: Field; tagLabel: string };

function tagSummary(tag: Tag, kind: SubField["kind"]): string {
  return kind === "per_item" && tag.states !== undefined
    ? `${tag.count} grounds across ${tag.states} states`
    : `${tag.count} states`;
}

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
        target={panel}
        profession={prof.profession}
        onClose={() => setPanel(null)}
      />
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

// Plain-text dump of a field's whole breakdown for copy-paste.
function breakdownText(field: Field): string {
  const lines: string[] = [field.label];
  for (const sf of field.subfields) {
    lines.push("", sf.field_name);
    const byBucket = groupByBucket(sf);
    for (const tag of sf.tags) {
      lines.push(`  ${tag.label} (${tagSummary(tag, sf.kind)})`);
      for (const m of byBucket.get(tag.label) ?? []) {
        lines.push(`    ${m.state}  ${m.text}`);
      }
    }
  }
  return lines.join("\n");
}

function TagBreakdownSheet({
  target,
  profession,
  onClose,
}: {
  target: PanelTarget | null;
  profession: string;
  onClose: () => void;
}) {
  const [copied, setCopied] = useState(false);

  // Reset the "Copied" affordance whenever the panel target changes.
  useEffect(() => {
    setCopied(false);
  }, [target]);

  const copy = () => {
    if (!target) return;
    navigator.clipboard
      .writeText(breakdownText(target.field))
      .then(() => setCopied(true))
      .catch(() => setCopied(false));
  };

  return (
    <Sheet open={!!target} onOpenChange={(open) => !open && onClose()}>
      <SheetContent
        side="right"
        className="w-full sm:max-w-md lg:max-w-xl flex flex-col p-0"
      >
        {target && (
          <>
            <SheetHeader className="border-b px-6 py-4 flex-shrink-0 bg-background">
              <SheetTitle className="text-lg">{target.field.label}</SheetTitle>
              <SheetDescription>
                {profession} — full per-state breakdown
              </SheetDescription>
              <div className="mt-2">
                <Button variant="outline" size="sm" onClick={copy}>
                  {copied ? "Copied ✓" : "Copy all"}
                </Button>
              </div>
            </SheetHeader>

            <div className="flex-1 overflow-auto px-6 py-4 space-y-6">
              {target.field.subfields.map((sf) => {
                const byBucket = groupByBucket(sf);
                return (
                  <div key={sf.field_name}>
                    <p className="text-xs font-mono text-muted-foreground mb-3">
                      {sf.field_name} · {sf.unit} per tag
                    </p>
                    <div className="space-y-4">
                      {sf.tags.map((tag) => {
                        const members = byBucket.get(tag.label) ?? [];
                        const isFocus = tag.label === target.tagLabel;
                        return (
                          <div
                            key={tag.label}
                            className={
                              isFocus
                                ? "rounded-md border border-foreground/30 bg-muted/40 p-3"
                                : "rounded-md border p-3"
                            }
                          >
                            <p className="text-sm font-medium mb-2">
                              {tag.label}{" "}
                              <span className="font-normal text-muted-foreground">
                                — {tagSummary(tag, sf.kind)}
                              </span>
                            </p>
                            {members.length > 0 ? (
                              <ul className="space-y-1.5">
                                {members.map((m, i) => (
                                  <li
                                    key={`${m.state}-${i}`}
                                    className="text-xs leading-snug"
                                  >
                                    <span className="font-mono font-semibold mr-1.5">
                                      {m.state}
                                    </span>
                                    <span className="text-muted-foreground">
                                      {m.text}
                                    </span>
                                  </li>
                                ))}
                              </ul>
                            ) : (
                              <p className="text-xs text-muted-foreground">
                                No member detail recorded.
                              </p>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </SheetContent>
    </Sheet>
  );
}

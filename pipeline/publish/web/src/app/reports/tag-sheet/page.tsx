"use client";

import { BackLink } from "@/components/ui/back-link";
import { Eyebrow } from "@/components/ui/eyebrow";
import { useEffect, useState, type ReactNode } from "react";
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

function tagSummary(tag: Tag, kind: "scalar" | "per_item"): string {
  return kind === "per_item" && tag.states !== undefined
    ? `${tag.count} items across ${tag.states} states`
    : `${tag.count} states`;
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

      <BreakdownPanel target={panel} onClose={() => setPanel(null)} />
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

// Builds a plain-text dump of the whole field's breakdown for copy-paste.
function breakdownText(target: PanelTarget): string {
  const lines: string[] = [
    `${target.field.label} — ${profLabel(target.profession)}`,
  ];
  for (const sf of target.field.subfields) {
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

function BreakdownPanel({
  target,
  onClose,
}: {
  target: PanelTarget | null;
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
      .writeText(breakdownText(target))
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
                {profLabel(target.profession)} — full per-state breakdown
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

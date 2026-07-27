"use client";

// The right-side Sheet that shows a field's full per-state tag breakdown, shared
// by the home /reports/tag-sheet report and the per-profession Tags tab so the
// two can't drift (they were ~100 lines of identical JSX). Callers differ only in
// the description line, the per-item noun, and the copy-text header.

import { useEffect, useState } from "react";
import { useOpenStateDetail } from "@/components/state-focus";
import { DetailSheet, SheetScrollBody } from "@/components/ui/detail-sheet";
import { FilterBar } from "@/components/ui/filter-bar";
import { SEMANTIC_CLASSES as SC } from "@/lib/web-colors";

import { Button } from "@/components/ui/button";
import {
  type Field,
  groupByBucket,
  tagSummary,
  breakdownText,
} from "@/lib/tag-sheet";

export function TagBreakdownSheet({
  field,
  tagLabel,
  description,
  noun,
  copyHeader,
  onClose,
}: {
  /** The field to break down; null closes the sheet. */
  field: Field | null;
  /** The tag the user clicked — highlighted/focused in the list. */
  tagLabel: string | null;
  /** Sub-header line, e.g. "Optometry — full per-state breakdown". */
  description: string;
  /** Per-item unit passed to tagSummary ("items" default, "grounds" for discipline). */
  noun?: string;
  /** Appended to the field label as the copy-text header line (e.g. the profession). */
  copyHeader?: string;
  onClose: () => void;
}) {
  const open = useOpenStateDetail();
  // Clicking a tag FILTERS this breakdown to it, and says so. It used to merely tint the
  // matching group: all five still listed, one with a slightly different border, nothing
  // naming what you clicked and no way to drop it. That reads as a filter you can't undo.
  // Derived rather than mirrored — track only what the user dismissed (see FilterBar).
  const requestKey = tagLabel ? `${field?.label ?? ""}:${tagLabel}` : null;
  const [dismissedTagKey, setDismissedTagKey] = useState<string | null>(null);
  const filterTag = requestKey && dismissedTagKey !== requestKey ? tagLabel : null;
  const [copied, setCopied] = useState(false);

  // Reset the "Copied" affordance whenever the target changes.
  useEffect(() => {
    setCopied(false);
  }, [field]);

  const copy = () => {
    if (!field) return;
    navigator.clipboard
      .writeText(breakdownText(field, { header: copyHeader, noun }))
      .then(() => setCopied(true))
      .catch(() => setCopied(false));
  };

  return (
    <DetailSheet
      open={!!field}
      onOpenChange={(o) => !o && onClose()}
      title={field?.label ?? ""}
      description={description}
      headerExtra={
        field ? (
          <div className="mt-2">
            <Button variant="outline" size="sm" onClick={copy}>
              {copied ? "Copied ✓" : "Copy all"}
            </Button>
          </div>
        ) : null
      }
    >
        {field && (
          <>
            <SheetScrollBody>
              {filterTag && (
                <FilterBar
                  label={filterTag}
                  source="from this field's tags"
                  onClear={() => setDismissedTagKey(requestKey)}
                />
              )}
              {field.subfields.map((sf) => {
                const byBucket = groupByBucket(sf);
                return (
                  <div key={sf.field_name}>
                    <p className="text-xs font-mono text-muted-foreground mb-3">
                      {sf.field_name} · {sf.unit} per tag
                    </p>
                    <div className="space-y-4">
                      {sf.tags
                        .filter((tag) => !filterTag || tag.label === filterTag)
                        .map((tag) => {
                        const members = byBucket.get(tag.label) ?? [];
                        return (
                          <div key={tag.label} className="rounded-md border p-3">
                            <p className="text-sm font-medium mb-2">
                              {tag.label}{" "}
                              <span className="font-normal text-muted-foreground">
                                — {tagSummary(tag, sf.kind, noun)}
                              </span>
                            </p>
                            {members.length > 0 ? (
                              <ul className="space-y-1.5">
                                {members.map((m, i) => (
                                  <li
                                    key={`${m.state}-${i}`}
                                    className="text-xs leading-snug"
                                  >
                                    {open ? (
                                      <button
                                        type="button"
                                        onClick={() => {
                                          // Close this breakdown first — otherwise the
                                          // state Sheet opens on top of it and two
                                          // right-side panels stack.
                                          onClose();
                                          open(m.state, { fieldPath: sf.field_name });
                                        }}
                                        title={`Open ${m.state} — ${sf.field_name}`}
                                        className={`font-mono font-semibold mr-1.5 hover:underline focus-visible:outline-none focus-visible:ring-2 ${SC.interaction.focusRing}`}
                                      >
                                        {m.state}
                                      </button>
                                    ) : (
                                      <span className="font-mono font-semibold mr-1.5">
                                        {m.state}
                                      </span>
                                    )}
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
            </SheetScrollBody>
          </>
        )}
    </DetailSheet>
  );
}

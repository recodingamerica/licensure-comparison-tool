"use client";

import { SEMANTIC_CLASSES as SC } from "@/lib/web-colors";

/**
 * The three reasons a value can be missing — which are NOT the same thing, and were
 * rendering as five different strings ("—", "no data", "No data", "not addressed", a
 * coverage-gap label) across six components.
 *
 * The distinction that matters to a reader is whether they're looking at a finding about
 * the law or a gap in our coverage:
 *
 *   not-addressed  — a FINDING. We have the statute; it is silent on this.
 *   not-extracted  — a GAP in us. We have the statute but recorded no value.
 *   no-statute     — a GAP in us. We could not obtain the law for this cell.
 *
 * Styled to match: the finding reads as ordinary muted text, the two gaps carry the
 * `attention` role, so a glance tells you which kind of thing you're seeing.
 */
export type AbsenceKind =
  | "not-addressed"
  | "not-extracted"
  | "no-statute"
  // Deliberately ambiguous. In a dense grid cell we often CANNOT tell whether the
  // statute was silent or we simply didn't record a value — the Sheet can, because it
  // knows the profession's field schema, but the grid can't. Saying "no value" is
  // honest; picking one of the two above would be a guess presented as a finding.
  | "unknown";

export const ABSENCE: Record<
  AbsenceKind,
  { label: string; help: string; isGap: boolean }
> = {
  "not-addressed": {
    label: "Not addressed",
    help: "This state's statute is silent on this — which is different from saying no.",
    isGap: false,
  },
  "not-extracted": {
    label: "Not extracted",
    help: "We have this state's statute but haven't recorded a value for this field.",
    isGap: true,
  },
  "no-statute": {
    label: "No statute available",
    help: "We couldn't obtain this state's law for this profession.",
    isGap: true,
  },
  unknown: {
    label: "No value",
    help: "No value recorded for this field — either the statute is silent or we haven't extracted it. Open the state to see which.",
    isGap: false,
  },
};

/**
 * `compact` renders the dash a dense grid cell needs, but carries the meaning in the
 * tooltip — so the table stays scannable without the three cases collapsing into one
 * unexplained character.
 */
export function Absent({
  kind,
  compact = false,
}: {
  kind: AbsenceKind;
  compact?: boolean;
}) {
  const { label, help, isGap } = ABSENCE[kind];
  const tone = isGap ? SC.attention.text : "text-muted-foreground";

  if (compact) {
    return (
      <span className={tone} title={`${label} — ${help}`}>
        —
      </span>
    );
  }

  return (
    <div className="space-y-1">
      <div className={`font-medium text-sm ${tone}`}>{label}</div>
      <p className="text-[11px] not-italic text-muted-foreground leading-snug">{help}</p>
    </div>
  );
}

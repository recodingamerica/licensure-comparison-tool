"use client";

import { SEMANTIC_CLASSES as SC } from "@/lib/web-colors";

/**
 * "You are seeing a subset, here's why, here's how to stop."
 *
 * Any filtering the UI applies on the user's behalf gets one of these. A filter the user
 * can't see is an invisible reason they're not seeing everything — and a highlight with
 * no label reads as a filter anyway, so it needs the same treatment.
 */
export function FilterBar({
  label,
  source,
  onClear,
  clearLabel = "Show all",
}: {
  /** What was clicked — the thing being filtered TO. */
  label: string;
  /** Where the click came from, e.g. "from Disciplinary categories". */
  source?: string;
  onClear: () => void;
  clearLabel?: string;
}) {
  return (
    <div
      className={`mb-3 flex items-center gap-2 rounded-md border ${SC.interaction.border} ${SC.interaction.bgSubtle} px-3 py-2 text-xs`}
    >
      <span className="text-muted-foreground">Filtered to</span>
      <span className="font-medium">{label}</span>
      {source && <span className="text-muted-foreground">{source}</span>}
      <button
        type="button"
        onClick={onClear}
        className={`ml-auto rounded px-2 py-0.5 font-medium ${SC.interaction.text} ${SC.interaction.hoverBg} focus-visible:outline-none focus-visible:ring-2 ${SC.interaction.focusRing}`}
        aria-label={`${clearLabel} — clear this filter`}
      >
        {clearLabel} ✕
      </button>
    </div>
  );
}

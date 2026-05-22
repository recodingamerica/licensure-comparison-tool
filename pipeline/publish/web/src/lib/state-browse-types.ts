// Types for the state-level /browse/[state] payload. Mirrors what
// pipeline/publish/build_state_browse.py emits per state.

import type { BrowseEvidence } from "@/lib/types";

export type StateBrowseAudience = "universal" | "multi" | "single";

export type StateBrowseSection = {
  url: string;
  citation: string;
  label: string;
  text: string;
  // "universal"  — applies to every licensed profession in the state
  // "multi"      — applies to a specific named set of professions
  // "single"     — a profession's practice-act section (one profession)
  audience: StateBrowseAudience;
  // For "multi": the explicit set of professions this applies to.
  // For "single": [profession].
  // For "universal": null (applies to all by definition).
  applies_to: string[] | null;
  // For "single": which profession's practice act this section belongs to.
  // null otherwise.
  profession: string | null;
  scope_source: string | null;
  // Evidence quotes from any profession that found a match in this section.
  // The `profession` field on each entry identifies which extraction
  // produced it.
  evidence: BrowseEvidence[];
};

export type StateBrowsePayload = {
  state: string;
  professions_available: string[];
  sections: StateBrowseSection[];
};

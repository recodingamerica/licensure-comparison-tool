// Shared audience taxonomy used wherever the app shows "who does this
// regulation apply to":
//   universal — applies to every licensed profession in the state
//   multi     — applies to a defined set of professions (>1)
//   single    — applies to one profession only
//
// Used by /browse/[state] (state-level) and /umbrella/profession/[id]
// (profession-level). Keep labels + colors here so both views stay in sync.

export type AudienceKind = "universal" | "multi" | "single";

export const AUDIENCE_LABEL: Record<AudienceKind, string> = {
  universal: "Applies to everyone",
  multi: "Shared with multiple professions",
  single: "Profession-specific",
};

export const AUDIENCE_DOT: Record<AudienceKind, string> = {
  universal: "bg-purple-500",
  multi: "bg-emerald-500",
  single: "bg-sky-500",
};

export const AUDIENCE_KINDS: AudienceKind[] = ["universal", "multi", "single"];

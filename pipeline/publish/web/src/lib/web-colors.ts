// GENERATED FROM pipeline/config/web_colors.yaml by scripts/generate-colors.mjs.
// Do not edit by hand — edit the yaml and re-run `npm run predev` or
// `node scripts/generate-colors.mjs`.

export type AudienceKind = "universal" | "multi" | "single";

export type HueClasses = {
  bg: string;
  text: string;
  border: string;
  dot: string;
};

export const AUDIENCE_HUE: Record<AudienceKind, string> = {
  "universal": "purple",
  "multi": "emerald",
  "single": "sky"
};

export const AUDIENCE_CLASSES: Record<AudienceKind, HueClasses> = {
  "universal": {
    "bg": "bg-purple-100",
    "text": "text-purple-800",
    "border": "border-purple-300",
    "dot": "bg-purple-500"
  },
  "multi": {
    "bg": "bg-emerald-100",
    "text": "text-emerald-800",
    "border": "border-emerald-300",
    "dot": "bg-emerald-500"
  },
  "single": {
    "bg": "bg-sky-100",
    "text": "text-sky-800",
    "border": "border-sky-300",
    "dot": "bg-sky-500"
  }
};

export const AUDIENCE_LABEL: Record<AudienceKind, string> = {
  "universal": "Applies to everyone",
  "multi": "Shared with multiple professions",
  "single": "Profession-specific"
};

export const AUDIENCE_KINDS: AudienceKind[] = ["universal", "multi", "single"];

export const FAMILY_HUES = ["emerald", "sky", "violet", "amber", "slate", "rose", "orange", "teal", "indigo", "fuchsia", "lime"] as const;

export type FamilyHue = (typeof FAMILY_HUES)[number];

export const FAMILY_CLASSES: Record<FamilyHue, HueClasses> = {
  "emerald": {
    "bg": "bg-emerald-100",
    "text": "text-emerald-800",
    "border": "border-emerald-300",
    "dot": "bg-emerald-500"
  },
  "sky": {
    "bg": "bg-sky-100",
    "text": "text-sky-800",
    "border": "border-sky-300",
    "dot": "bg-sky-500"
  },
  "violet": {
    "bg": "bg-violet-100",
    "text": "text-violet-800",
    "border": "border-violet-300",
    "dot": "bg-violet-500"
  },
  "amber": {
    "bg": "bg-amber-100",
    "text": "text-amber-800",
    "border": "border-amber-300",
    "dot": "bg-amber-500"
  },
  "slate": {
    "bg": "bg-slate-100",
    "text": "text-slate-800",
    "border": "border-slate-300",
    "dot": "bg-slate-500"
  },
  "rose": {
    "bg": "bg-rose-100",
    "text": "text-rose-800",
    "border": "border-rose-300",
    "dot": "bg-rose-500"
  },
  "orange": {
    "bg": "bg-orange-100",
    "text": "text-orange-800",
    "border": "border-orange-300",
    "dot": "bg-orange-500"
  },
  "teal": {
    "bg": "bg-teal-100",
    "text": "text-teal-800",
    "border": "border-teal-300",
    "dot": "bg-teal-500"
  },
  "indigo": {
    "bg": "bg-indigo-100",
    "text": "text-indigo-800",
    "border": "border-indigo-300",
    "dot": "bg-indigo-500"
  },
  "fuchsia": {
    "bg": "bg-fuchsia-100",
    "text": "text-fuchsia-800",
    "border": "border-fuchsia-300",
    "dot": "bg-fuchsia-500"
  },
  "lime": {
    "bg": "bg-lime-100",
    "text": "text-lime-800",
    "border": "border-lime-300",
    "dot": "bg-lime-500"
  }
};

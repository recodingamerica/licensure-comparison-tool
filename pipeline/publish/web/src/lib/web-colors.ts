// GENERATED FROM pipeline/config/web_colors.yaml by scripts/generate-colors.mjs.
// Do not edit by hand — edit the yaml and re-run `npm run predev` or
// `node scripts/generate-colors.mjs`.

export type AudienceKind = "universal" | "multi" | "single";

export type HueClasses = {
  bg: string;
  text: string;
  border: string;
  dot: string;
  hoverBg: string;
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
    "dot": "bg-purple-500",
    "hoverBg": "hover:bg-purple-100"
  },
  "multi": {
    "bg": "bg-emerald-100",
    "text": "text-emerald-800",
    "border": "border-emerald-300",
    "dot": "bg-emerald-500",
    "hoverBg": "hover:bg-emerald-100"
  },
  "single": {
    "bg": "bg-sky-100",
    "text": "text-sky-800",
    "border": "border-sky-300",
    "dot": "bg-sky-500",
    "hoverBg": "hover:bg-sky-100"
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
    "dot": "bg-emerald-500",
    "hoverBg": "hover:bg-emerald-100"
  },
  "sky": {
    "bg": "bg-sky-100",
    "text": "text-sky-800",
    "border": "border-sky-300",
    "dot": "bg-sky-500",
    "hoverBg": "hover:bg-sky-100"
  },
  "violet": {
    "bg": "bg-violet-100",
    "text": "text-violet-800",
    "border": "border-violet-300",
    "dot": "bg-violet-500",
    "hoverBg": "hover:bg-violet-100"
  },
  "amber": {
    "bg": "bg-amber-100",
    "text": "text-amber-800",
    "border": "border-amber-300",
    "dot": "bg-amber-500",
    "hoverBg": "hover:bg-amber-100"
  },
  "slate": {
    "bg": "bg-slate-100",
    "text": "text-slate-800",
    "border": "border-slate-300",
    "dot": "bg-slate-500",
    "hoverBg": "hover:bg-slate-100"
  },
  "rose": {
    "bg": "bg-rose-100",
    "text": "text-rose-800",
    "border": "border-rose-300",
    "dot": "bg-rose-500",
    "hoverBg": "hover:bg-rose-100"
  },
  "orange": {
    "bg": "bg-orange-100",
    "text": "text-orange-800",
    "border": "border-orange-300",
    "dot": "bg-orange-500",
    "hoverBg": "hover:bg-orange-100"
  },
  "teal": {
    "bg": "bg-teal-100",
    "text": "text-teal-800",
    "border": "border-teal-300",
    "dot": "bg-teal-500",
    "hoverBg": "hover:bg-teal-100"
  },
  "indigo": {
    "bg": "bg-indigo-100",
    "text": "text-indigo-800",
    "border": "border-indigo-300",
    "dot": "bg-indigo-500",
    "hoverBg": "hover:bg-indigo-100"
  },
  "fuchsia": {
    "bg": "bg-fuchsia-100",
    "text": "text-fuchsia-800",
    "border": "border-fuchsia-300",
    "dot": "bg-fuchsia-500",
    "hoverBg": "hover:bg-fuchsia-100"
  },
  "lime": {
    "bg": "bg-lime-100",
    "text": "text-lime-800",
    "border": "border-lime-300",
    "dot": "bg-lime-500",
    "hoverBg": "hover:bg-lime-100"
  }
};

// Semantic roles — one named color per meaning (see config/web_colors.yaml).
export type SemanticRole = "attention" | "highlight" | "restrictive" | "permissive";

export type SolidClasses = { bg: string; text: string; border: string };

export const SEMANTIC_HUE: Record<SemanticRole, string> = {
  "attention": "amber",
  "highlight": "yellow",
  "restrictive": "rose",
  "permissive": "emerald"
};

export const SEMANTIC_CLASSES: Record<SemanticRole, HueClasses> = {
  "attention": {
    "bg": "bg-amber-100",
    "text": "text-amber-800",
    "border": "border-amber-300",
    "dot": "bg-amber-500",
    "hoverBg": "hover:bg-amber-100"
  },
  "highlight": {
    "bg": "bg-yellow-100",
    "text": "text-yellow-800",
    "border": "border-yellow-300",
    "dot": "bg-yellow-500",
    "hoverBg": "hover:bg-yellow-100"
  },
  "restrictive": {
    "bg": "bg-rose-100",
    "text": "text-rose-800",
    "border": "border-rose-300",
    "dot": "bg-rose-500",
    "hoverBg": "hover:bg-rose-100"
  },
  "permissive": {
    "bg": "bg-emerald-100",
    "text": "text-emerald-800",
    "border": "border-emerald-300",
    "dot": "bg-emerald-500",
    "hoverBg": "hover:bg-emerald-100"
  }
};

export const SEMANTIC_SOLID: Record<SemanticRole, SolidClasses> = {
  "attention": {
    "bg": "bg-amber-600",
    "text": "text-white",
    "border": "border-amber-600"
  },
  "highlight": {
    "bg": "bg-yellow-600",
    "text": "text-white",
    "border": "border-yellow-600"
  },
  "restrictive": {
    "bg": "bg-rose-600",
    "text": "text-white",
    "border": "border-rose-600"
  },
  "permissive": {
    "bg": "bg-emerald-600",
    "text": "text-white",
    "border": "border-emerald-600"
  }
};

// Category palettes — value → HueClasses, per named palette (see config yaml).
export const CATEGORY_CLASSES: Record<string, Record<string, HueClasses>> = {
  "regulatory": {
    "license": {
      "bg": "bg-sky-100",
      "text": "text-sky-800",
      "border": "border-sky-300",
      "dot": "bg-sky-500",
      "hoverBg": "hover:bg-sky-100"
    },
    "mandatory_certification": {
      "bg": "bg-emerald-100",
      "text": "text-emerald-800",
      "border": "border-emerald-300",
      "dot": "bg-emerald-500",
      "hoverBg": "hover:bg-emerald-100"
    },
    "certification": {
      "bg": "bg-emerald-100",
      "text": "text-emerald-800",
      "border": "border-emerald-300",
      "dot": "bg-emerald-500",
      "hoverBg": "hover:bg-emerald-100"
    },
    "registration": {
      "bg": "bg-amber-100",
      "text": "text-amber-800",
      "border": "border-amber-300",
      "dot": "bg-amber-500",
      "hoverBg": "hover:bg-amber-100"
    },
    "exemption": {
      "bg": "bg-zinc-100",
      "text": "text-zinc-800",
      "border": "border-zinc-300",
      "dot": "bg-zinc-500",
      "hoverBg": "hover:bg-zinc-100"
    },
    "voluntary_certification": {
      "bg": "bg-violet-100",
      "text": "text-violet-800",
      "border": "border-violet-300",
      "dot": "bg-violet-500",
      "hoverBg": "hover:bg-violet-100"
    },
    "market_forces": {
      "bg": "bg-rose-100",
      "text": "text-rose-800",
      "border": "border-rose-300",
      "dot": "bg-rose-500",
      "hoverBg": "hover:bg-rose-100"
    },
    "none": {
      "bg": "bg-rose-100",
      "text": "text-rose-800",
      "border": "border-rose-300",
      "dot": "bg-rose-500",
      "hoverBg": "hover:bg-rose-100"
    }
  },
  "novel_category": {
    "Degree": {
      "bg": "bg-slate-100",
      "text": "text-slate-800",
      "border": "border-slate-300",
      "dot": "bg-slate-500",
      "hoverBg": "hover:bg-slate-100"
    },
    "Experience": {
      "bg": "bg-teal-100",
      "text": "text-teal-800",
      "border": "border-teal-300",
      "dot": "bg-teal-500",
      "hoverBg": "hover:bg-teal-100"
    },
    "Discipline": {
      "bg": "bg-rose-100",
      "text": "text-rose-800",
      "border": "border-rose-300",
      "dot": "bg-rose-500",
      "hoverBg": "hover:bg-rose-100"
    },
    "Scope": {
      "bg": "bg-sky-100",
      "text": "text-sky-800",
      "border": "border-sky-300",
      "dot": "bg-sky-500",
      "hoverBg": "hover:bg-sky-100"
    },
    "Regulation": {
      "bg": "bg-violet-100",
      "text": "text-violet-800",
      "border": "border-violet-300",
      "dot": "bg-violet-500",
      "hoverBg": "hover:bg-violet-100"
    },
    "Authority": {
      "bg": "bg-amber-100",
      "text": "text-amber-800",
      "border": "border-amber-300",
      "dot": "bg-amber-500",
      "hoverBg": "hover:bg-amber-100"
    },
    "License": {
      "bg": "bg-indigo-100",
      "text": "text-indigo-800",
      "border": "border-indigo-300",
      "dot": "bg-indigo-500",
      "hoverBg": "hover:bg-indigo-100"
    }
  }
};

// Concrete color values for JS consumers (SVG map fills, d3 scales) that can't
// use a CSS var(). Prefer the CSS custom properties (var(--<token>)) for HTML;
// use these where a real value is required. `token(name)` reads the current
// theme's value off the CSS custom property, falling back to the light value.
export type ColorToken = "scope-has" | "scope-prohibited" | "scope-none" | "scope-focus" | "scope-focus-weak" | "map-no-data" | "map-ramp-lo" | "map-ramp-hi" | "mark-search" | "mark-quote" | "kind-coverage" | "kind-value" | "spread-lo" | "spread-hi" | "grid-header" | "grid-row" | "grid-hover" | "grid-border" | "map-stroke" | "map-highlight" | "nav-fill";

export const COLOR_TOKENS: { light: Record<string, string>; dark: Record<string, string> } = {
  light: {
  "scope-has": "#14b8a6",
  "scope-prohibited": "#e11d48",
  "scope-none": "#eceff2",
  "scope-focus": "#d97706",
  "scope-focus-weak": "#fdf1e3",
  "map-no-data": "#e5e7eb",
  "map-ramp-lo": "#dbeafe",
  "map-ramp-hi": "#1e3a8a",
  "mark-search": "#fde047",
  "mark-quote": "#fde68a",
  "kind-coverage": "#b45309",
  "kind-value": "#0369a1",
  "spread-lo": "#eeece4",
  "spread-hi": "#b45309",
  "grid-header": "#f8fafc",
  "grid-row": "#ffffff",
  "grid-hover": "#f1f5f9",
  "grid-border": "#e2e8f0",
  "map-stroke": "#ffffff",
  "map-highlight": "#111827",
  "nav-fill": "#bfdbfe"
},
  dark: {
  "scope-has": "#2dd4bf",
  "scope-prohibited": "#fb7185",
  "scope-none": "#1b1f26",
  "scope-focus": "#f59e0b",
  "scope-focus-weak": "#2a2114",
  "map-no-data": "#e5e7eb",
  "map-ramp-lo": "#dbeafe",
  "map-ramp-hi": "#1e3a8a",
  "mark-search": "#fde047",
  "mark-quote": "#78560f",
  "kind-coverage": "#fbbf24",
  "kind-value": "#38bdf8",
  "spread-lo": "#3a3524",
  "spread-hi": "#fbbf24",
  "grid-header": "#1e293b",
  "grid-row": "#0f172a",
  "grid-hover": "#1e293b",
  "grid-border": "#334155",
  "map-stroke": "#0b0e12",
  "map-highlight": "#e5e7eb",
  "nav-fill": "#1e3a5f"
},
};

export const MAP_PALETTE = ["#0ea5e9", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6", "#f97316", "#6366f1", "#84cc16", "#a855f7", "#06b6d4"] as const;

export function token(name: ColorToken): string {
  if (typeof document !== "undefined") {
    const v = getComputedStyle(document.documentElement)
      .getPropertyValue(`--${name}`)
      .trim();
    if (v) return v;
  }
  return COLOR_TOKENS.light[name];
}

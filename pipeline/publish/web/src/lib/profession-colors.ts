// Profession visual metadata — color (per family, not per profession),
// abbreviation, display name. Single source of truth lives in
// pipeline/config/professions.yaml; build_frontend.py forwards the fields
// into each profession blob, fetch-blob-data.mjs aggregates them into
// /professions.json on prebuild, and the frontend reads from there.
//
// Color-per-family scales as we add more professions. Six professions
// today; the canonical registry has ~50. Two professions in the same
// family share a color, which is informative: "this rule is for health
// professions" reads at a glance no matter how many individual leaves
// exist beneath it.

export type ProfessionMeta = {
  key: string;
  display: string;
  abbrev: string;
  family: string | null;
  family_color: string | null;  // Tailwind hue name: "emerald" | "amber" | "slate" | "rose"
  family_label: string | null;
};

export type ProfessionStyle = {
  bg: string;
  text: string;
  border: string;
  dot: string;
  abbr: string;
  display: string;
  family: string | null;
  family_label: string | null;
};

// Tailwind class lookups by hue name. Avoids dynamic class names that
// would otherwise be purged at build time.
const HUE_CLASSES: Record<string, Omit<ProfessionStyle, "abbr" | "display" | "family" | "family_label">> = {
  emerald: {
    bg: "bg-emerald-100",
    text: "text-emerald-800",
    border: "border-emerald-300",
    dot: "bg-emerald-500",
  },
  amber: {
    bg: "bg-amber-100",
    text: "text-amber-800",
    border: "border-amber-300",
    dot: "bg-amber-500",
  },
  slate: {
    bg: "bg-slate-200",
    text: "text-slate-700",
    border: "border-slate-300",
    dot: "bg-slate-500",
  },
  rose: {
    bg: "bg-rose-100",
    text: "text-rose-800",
    border: "border-rose-300",
    dot: "bg-rose-500",
  },
  sky: {
    bg: "bg-sky-100",
    text: "text-sky-800",
    border: "border-sky-300",
    dot: "bg-sky-500",
  },
  violet: {
    bg: "bg-violet-100",
    text: "text-violet-800",
    border: "border-violet-300",
    dot: "bg-violet-500",
  },
};

const NEUTRAL = {
  bg: "bg-muted",
  text: "text-foreground",
  border: "border-border",
  dot: "bg-muted-foreground",
};

// Module-level cache. Populated by useProfessionMeta() (a React hook that
// returns a re-render trigger so components update when the registry
// finishes loading).
let registry: Map<string, ProfessionMeta> | null = null;
let loadPromise: Promise<void> | null = null;
const listeners = new Set<() => void>();

function loadOnce(): Promise<void> {
  if (loadPromise) return loadPromise;
  loadPromise = (async () => {
    try {
      const res = await fetch("/professions.json");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const list: Array<ProfessionMeta & { profession?: string }> = await res.json();
      const m = new Map<string, ProfessionMeta>();
      for (const p of list) m.set(p.key ?? p.profession ?? "", p);
      registry = m;
    } catch {
      registry = new Map();
    }
    for (const fn of listeners) fn();
  })();
  return loadPromise;
}

import { useEffect, useState } from "react";

/** Call from any component that uses professionStyle(). Triggers a
 *  re-render once /professions.json is loaded so colors appear instead
 *  of the neutral fallback. Returns whether the registry is ready. */
export function useProfessionMeta(): boolean {
  const [, force] = useState(0);
  useEffect(() => {
    if (registry) return;
    const tick = () => force((n) => n + 1);
    listeners.add(tick);
    loadOnce();
    return () => {
      listeners.delete(tick);
    };
  }, []);
  return registry !== null;
}

export function professionStyle(key: string): ProfessionStyle {
  const meta = registry?.get(key);
  const hue = meta?.family_color ?? null;
  const classes = (hue && HUE_CLASSES[hue]) || NEUTRAL;
  return {
    ...classes,
    abbr: meta?.abbrev ?? key.slice(0, 3).toUpperCase(),
    display: meta?.display ?? key.replace(/_/g, " "),
    family: meta?.family ?? null,
    family_label: meta?.family_label ?? null,
  };
}

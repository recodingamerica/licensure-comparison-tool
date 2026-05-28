// Audience taxonomy — thin re-export over web-colors.ts (which is generated
// from pipeline/config/web_colors.yaml). The yaml is the single source of
// truth for color hues + labels; this module exposes the names callers
// already use.

export type { AudienceKind } from "./web-colors";
import {
  AUDIENCE_CLASSES,
  AUDIENCE_KINDS as KINDS,
  AUDIENCE_LABEL as LABEL,
  type AudienceKind,
} from "./web-colors";

export const AUDIENCE_LABEL = LABEL;
export const AUDIENCE_KINDS = KINDS;

// Map AudienceKind → "bg-…-500" dot class. Callers across the app expect a
// flat string per kind, so we derive from AUDIENCE_CLASSES here rather than
// have every call site read .dot.
export const AUDIENCE_DOT: Record<AudienceKind, string> = {
  universal: AUDIENCE_CLASSES.universal.dot,
  multi: AUDIENCE_CLASSES.multi.dot,
  single: AUDIENCE_CLASSES.single.dot,
};

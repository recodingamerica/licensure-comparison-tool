#!/usr/bin/env node
// Read pipeline/config/web_colors.yaml and emit src/lib/web-colors.ts so
// audience.ts and profession-colors.ts have one source of truth. Tailwind
// purge needs literal classes, so we emit explicit class-strings here
// rather than concatenate at runtime.
//
// Run by `npm run predev` / `npm run prebuild`. Safe to re-run; output is
// deterministic.

import { readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml } from "yaml";

const HERE = dirname(fileURLToPath(import.meta.url));
// yaml lives inside the web/ subtree so Vercel ships it with the build —
// Vercel only checks out the rootDirectory (web/) so a parent-dir yaml
// would 404 on production builds.
const YAML_PATH = resolve(HERE, "..", "config", "web_colors.yaml");
const OUT_PATH = resolve(HERE, "..", "src", "lib", "web-colors.ts");

function hueClasses(hue) {
  return {
    bg: `bg-${hue}-100`,
    text: `text-${hue}-800`,
    border: `border-${hue}-300`,
    dot: `bg-${hue}-500`,
  };
}

const raw = await readFile(YAML_PATH, "utf8");
const cfg = parseYaml(raw);

const audienceHues = cfg.audience;
const familyHues = cfg.families;
const audienceLabels = cfg.audience_labels;

const audienceClasses = Object.fromEntries(
  Object.entries(audienceHues).map(([k, hue]) => [k, hueClasses(hue)]),
);
const familyClasses = Object.fromEntries(
  familyHues.map((hue) => [hue, hueClasses(hue)]),
);

const out = `// GENERATED FROM pipeline/config/web_colors.yaml by scripts/generate-colors.mjs.
// Do not edit by hand — edit the yaml and re-run \`npm run predev\` or
// \`node scripts/generate-colors.mjs\`.

export type AudienceKind = ${Object.keys(audienceHues)
  .map((k) => `"${k}"`)
  .join(" | ")};

export type HueClasses = {
  bg: string;
  text: string;
  border: string;
  dot: string;
};

export const AUDIENCE_HUE: Record<AudienceKind, string> = ${JSON.stringify(audienceHues, null, 2)};

export const AUDIENCE_CLASSES: Record<AudienceKind, HueClasses> = ${JSON.stringify(
  audienceClasses,
  null,
  2,
)};

export const AUDIENCE_LABEL: Record<AudienceKind, string> = ${JSON.stringify(audienceLabels, null, 2)};

export const AUDIENCE_KINDS: AudienceKind[] = [${Object.keys(audienceHues)
  .map((k) => `"${k}"`)
  .join(", ")}];

export const FAMILY_HUES = [${familyHues.map((h) => `"${h}"`).join(", ")}] as const;

export type FamilyHue = (typeof FAMILY_HUES)[number];

export const FAMILY_CLASSES: Record<FamilyHue, HueClasses> = ${JSON.stringify(
  familyClasses,
  null,
  2,
)};
`;

await writeFile(OUT_PATH, out);
console.log(`wrote ${OUT_PATH} (audience: ${Object.keys(audienceHues).join(", ")}; families: ${familyHues.join(", ")})`);

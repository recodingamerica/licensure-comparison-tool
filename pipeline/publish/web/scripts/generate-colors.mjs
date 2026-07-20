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
const GLOBALS_PATH = resolve(HERE, "..", "src", "app", "globals.css");

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
const tokens = cfg.tokens ?? {};
const mapPalette = cfg.map_palette ?? [];
const theme = cfg.theme ?? {}; // shadcn base theme (light/dark)
const themeStatic = cfg.theme_static ?? {}; // non-color base tokens (radius…)

// Split the {name: {light, dark}} tokens into two flat maps of concrete values.
const tokenLight = Object.fromEntries(
  Object.entries(tokens).map(([k, v]) => [k, v.light]),
);
const tokenDark = Object.fromEntries(
  Object.entries(tokens).map(([k, v]) => [k, v.dark]),
);
const themeLight = Object.fromEntries(
  Object.entries(theme).map(([k, v]) => [k, v.light]),
);
const themeDark = Object.fromEntries(
  Object.entries(theme).map(([k, v]) => [k, v.dark]),
);

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

// Concrete color values for JS consumers (SVG map fills, d3 scales) that can't
// use a CSS var(). Prefer the CSS custom properties (var(--<token>)) for HTML;
// use these where a real value is required. \`token(name)\` reads the current
// theme's value off the CSS custom property, falling back to the light value.
export type ColorToken = ${Object.keys(tokens)
  .map((k) => `"${k}"`)
  .join(" | ") || "string"};

export const COLOR_TOKENS: { light: Record<string, string>; dark: Record<string, string> } = {
  light: ${JSON.stringify(tokenLight, null, 2)},
  dark: ${JSON.stringify(tokenDark, null, 2)},
};

export const MAP_PALETTE = [${mapPalette.map((c) => `"${c}"`).join(", ")}] as const;

export function token(name: ColorToken): string {
  if (typeof document !== "undefined") {
    const v = getComputedStyle(document.documentElement)
      .getPropertyValue(\`--\${name}\`)
      .trim();
    if (v) return v;
  }
  return COLOR_TOKENS.light[name];
}
`;

await writeFile(OUT_PATH, out);
console.log(`wrote ${OUT_PATH} (audience: ${Object.keys(audienceHues).join(", ")}; families: ${familyHues.join(", ")}; tokens: ${Object.keys(tokens).join(", ")})`);

// Inject the CSS custom properties into globals.css between markers (kept in the
// main entry so Tailwind/Turbopack always processes them — a separate @import
// file was not reliably picked up).
const cssLines = (map) =>
  Object.entries(map)
    .map(([k, v]) => `  --${k}: ${v};`)
    .join("\n");
const START = "/* @color-tokens:start — generated from config/web_colors.yaml, do not edit */";
const END = "/* @color-tokens:end */";
// One place for every color value: shadcn base theme + static tokens + the
// scope/map value tokens, split into :root (light) and .dark.
const lightAll = { ...themeLight, ...themeStatic, ...tokenLight };
const darkAll = { ...themeDark, ...tokenDark };
const block = `${START}
:root {
${cssLines(lightAll)}
}
.dark {
${cssLines(darkAll)}
}
${END}`;
let globals = await readFile(GLOBALS_PATH, "utf8");
const re = new RegExp(`${START.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}[\\s\\S]*?${END.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}`);
if (re.test(globals)) {
  globals = globals.replace(re, block);
} else {
  throw new Error("globals.css is missing the @color-tokens:start/end markers");
}
await writeFile(GLOBALS_PATH, globals);
console.log(`injected ${Object.keys(tokens).length} tokens into ${GLOBALS_PATH}`);

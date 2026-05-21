#!/usr/bin/env node
// Prebuild step: pull every data/<prof>.json from Vercel Blob into public/data/
// and rebuild public/professions.json so the home page picker stays in sync.
// Reads BLOB_READ_WRITE_TOKEN from env (load via `node --env-file=.env.local`).

import { list } from "@vercel/blob";
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const PUBLIC_DIR = resolve(HERE, "..", "public");
const DATA_DIR = resolve(PUBLIC_DIR, "data");

const { blobs } = await list({ prefix: "data/" });
if (!blobs.length) {
  console.warn("no data/* blobs found — building with empty data");
}

await mkdir(DATA_DIR, { recursive: true });

const items = [];
for (const blob of blobs) {
  if (!blob.pathname.endsWith(".json")) continue;
  const res = await fetch(blob.url);
  if (!res.ok) {
    throw new Error(`fetch ${blob.url} → ${res.status}`);
  }
  const text = await res.text();
  const localName = blob.pathname.replace(/^data\//, "");
  await writeFile(resolve(DATA_DIR, localName), text);

  const d = JSON.parse(text);
  console.log(`fetched ${blob.pathname} (${text.length} bytes)`);

  // The data/ prefix carries both per-profession data and one-off reports
  // (e.g. scorecard.json). Profession files are the ones with `profession`
  // + `rows`; everything else just lands on disk for the route that wants
  // it (e.g. /reports/scorecard reads /data/scorecard.json directly).
  if (!d.profession || !Array.isArray(d.rows)) continue;

  const rows = d.rows ?? [];
  const ev = d.evidence_summary ?? {};
  const v = ev.verified ?? 0;
  const u = ev.unverified ?? 0;
  items.push({
    profession: d.profession,
    display: d.display ?? d.profession,
    covered: rows.filter((r) => !r.coverage_gap).length,
    gaps: rows.filter((r) => r.coverage_gap).length,
    fields: (d.discovered_fields ?? []).length,
    verified_pct: v + u ? Math.round((1000 * v) / (v + u)) / 10 : null,
  });
}

items.sort((a, b) => a.profession.localeCompare(b.profession));
await writeFile(
  resolve(PUBLIC_DIR, "professions.json"),
  JSON.stringify(items, null, 2),
);
console.log(`wrote professions.json with ${items.length} entries`);

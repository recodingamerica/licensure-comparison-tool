#!/usr/bin/env node
// Bulk-upload public/data/umbrella/** to Vercel Blob.
// Used to seed/refresh prod data after a build_umbrella_browse run.
//   node --env-file=.env.local scripts/upload-umbrella-bulk.mjs
import { put } from "@vercel/blob";
import { readFile, readdir } from "node:fs/promises";
import { dirname, join, resolve, relative } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..", "public", "data", "umbrella");

async function* walk(dir) {
  for (const ent of await readdir(dir, { withFileTypes: true })) {
    const p = join(dir, ent.name);
    if (ent.isDirectory()) yield* walk(p);
    else if (ent.isFile() && p.endsWith(".json")) yield p;
  }
}

const CONCURRENCY = 8;
const files = [];
for await (const f of walk(ROOT)) files.push(f);
console.log(`uploading ${files.length} umbrella files to blob…`);

let done = 0;
async function worker(slice) {
  for (const file of slice) {
    const body = await readFile(file, "utf8");
    const rel = relative(resolve(HERE, "..", "public"), file).replace(/\\/g, "/"); // data/umbrella/<...>
    await put(rel, body, {
      access: "public",
      contentType: "application/json",
      addRandomSuffix: false,
      allowOverwrite: true,
    });
    done++;
    if (done % 25 === 0 || done === files.length) console.log(`  ${done}/${files.length}`);
  }
}
const chunks = Array.from({ length: CONCURRENCY }, (_, i) =>
  files.filter((_, idx) => idx % CONCURRENCY === i),
);
await Promise.all(chunks.map(worker));
console.log("done");

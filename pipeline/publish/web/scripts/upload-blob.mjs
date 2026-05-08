#!/usr/bin/env node
// Upload one JSON payload to Vercel Blob at a fixed pathname.
// Usage:
//   node scripts/upload-blob.mjs <pathname> < payload.json
// Reads BLOB_READ_WRITE_TOKEN from env (load via `node --env-file=.env.local`).

import { put } from "@vercel/blob";

const pathname = process.argv[2];
if (!pathname) {
  console.error("usage: upload-blob.mjs <pathname>");
  process.exit(2);
}

const body = await new Promise((resolve, reject) => {
  const chunks = [];
  process.stdin.on("data", (c) => chunks.push(c));
  process.stdin.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
  process.stdin.on("error", reject);
});

const blob = await put(pathname, body, {
  access: "public",
  contentType: "application/json",
  addRandomSuffix: false,
  allowOverwrite: true,
});

console.log(blob.url);

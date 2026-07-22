#!/usr/bin/env node
// Upload one JSON payload to Vercel Blob at a fixed pathname.
// Usage:
//   node scripts/upload-blob.mjs <pathname> < payload.json
// Reads BLOB_READ_WRITE_TOKEN from env (load via `node --env-file=.env.local`).

import { put } from "@vercel/blob";

const pathname = process.argv[2];
const contentType = process.argv[3] || "application/json";
if (!pathname) {
  console.error("usage: upload-blob.mjs <pathname> [contentType]");
  process.exit(2);
}

// Read stdin as a raw Buffer so binary payloads (e.g. .xlsx) survive; JSON is a
// UTF-8 buffer, which put() handles identically to a string.
const body = await new Promise((resolve, reject) => {
  const chunks = [];
  process.stdin.on("data", (c) => chunks.push(c));
  process.stdin.on("end", () => resolve(Buffer.concat(chunks)));
  process.stdin.on("error", reject);
});

const blob = await put(pathname, body, {
  access: "public",
  contentType,
  addRandomSuffix: false,
  allowOverwrite: true,
});

console.log(blob.url);

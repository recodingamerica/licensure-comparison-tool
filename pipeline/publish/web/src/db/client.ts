// Shared Drizzle client backed by Neon's HTTP driver. Edge-runtime-safe so
// the /api/search route can run anywhere.
//
// Lazy-initialized: we DON'T read DATABASE_URL at import time, because Next
// imports route modules during build (to discover routes) — at which point
// the env var may not be set. Reading it lazily means a missing env var
// fails the FIRST request to /api/search with a clear error, while build
// still succeeds.

import { neon, type NeonQueryFunction } from "@neondatabase/serverless";
import { drizzle, type NeonHttpDatabase } from "drizzle-orm/neon-http";
import * as schema from "./schema";

let _db: NeonHttpDatabase<typeof schema> | null = null;

export function getDb(): NeonHttpDatabase<typeof schema> {
  if (_db) return _db;
  const url = process.env.DATABASE_URL;
  if (!url) {
    throw new Error(
      "DATABASE_URL is not set. Add it to .env.local for dev or to the Vercel project env for production.",
    );
  }
  const sql: NeonQueryFunction<false, false> = neon(url);
  _db = drizzle(sql, { schema });
  return _db;
}

export { schema };

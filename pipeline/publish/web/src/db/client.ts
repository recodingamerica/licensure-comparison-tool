// Shared Drizzle client backed by Neon's HTTP driver. Edge-runtime-safe so
// the /api/search route can run anywhere.

import { neon } from "@neondatabase/serverless";
import { drizzle } from "drizzle-orm/neon-http";
import * as schema from "./schema";

const url = process.env.DATABASE_URL;
if (!url) {
  // Throwing at import time means an unset DATABASE_URL fails the build,
  // not the first /api/search request — easier to diagnose.
  throw new Error("DATABASE_URL is required. Set it in .env.local for dev and via Vercel env for prod.");
}

const sql = neon(url);

export const db = drizzle(sql, { schema });
export { schema };

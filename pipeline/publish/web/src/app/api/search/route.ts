// /api/search — phrase search across the Postgres data
//
// Two query targets:
//   scope=quotes   → LLM-extracted Evidence quotes (the substantive
//                    excerpts grounding each structured claim)
//   scope=statutes → raw section text (broader — finds language we may
//                    not have explicitly extracted)
//   scope=both     → returns both, the client tabs between them
//
// The Postgres FTS is via the generated tsvector columns + GIN indexes
// created by migrations 0008 / 0009. We use plainto_tsquery (treats q
// as a phrase, no operator parsing) so users don't have to learn FTS
// syntax. ts_rank orders results; ts_headline gives a 20-word
// highlighted snippet for statute hits.

import { NextResponse, type NextRequest } from "next/server";
import { sql } from "drizzle-orm";
import { db } from "@/db/client";

export const runtime = "edge";

const MAX_RESULTS = 100;

type QuoteHit = {
  kind: "quote";
  state: string;
  profession: string;
  field_path: string;
  value_text: string | null;
  quote: string;
  citation: string;
  unverified: boolean;
  rank: number;
};

type StatuteHit = {
  kind: "statute";
  state: string;
  profession: string | null;
  citation: string | null;
  label: string;
  hierarchy_level: string;
  is_umbrella: boolean;
  snippet: string;
  rank: number;
};

function clean(q: string): string {
  return q.trim().slice(0, 200);
}

export async function GET(req: NextRequest) {
  const params = req.nextUrl.searchParams;
  const q = clean(params.get("q") ?? "");
  if (!q) {
    return NextResponse.json({ quotes: [], statutes: [], q });
  }

  const scope = (params.get("scope") ?? "both") as "quotes" | "statutes" | "both";
  const profession = params.get("profession"); // optional filter
  const state = params.get("state");           // optional filter
  const unverifiedOnly = params.get("unverified") === "1";

  const tsq = sql`plainto_tsquery('english', ${q})`;

  let quotes: QuoteHit[] = [];
  let statutes: StatuteHit[] = [];

  if (scope === "quotes" || scope === "both") {
    const rows = await db.execute(sql`
      SELECT e.state,
             p.key  AS profession,
             e.field_path,
             e.value_text,
             e.quote,
             e.citation,
             e.unverified,
             ts_rank(e.quote_tsv, ${tsq}) AS rank
      FROM evidence e
      JOIN professions p ON p.id = e.profession_id
      WHERE e.quote_tsv @@ ${tsq}
        ${profession ? sql`AND p.key = ${profession}` : sql``}
        ${state ? sql`AND e.state = ${state}` : sql``}
        ${unverifiedOnly ? sql`AND e.unverified` : sql``}
      ORDER BY rank DESC
      LIMIT ${MAX_RESULTS}
    `);
    quotes = (rows as unknown as QuoteHit[]).map((r) => ({ ...r, kind: "quote" }));
  }

  if (scope === "statutes" || scope === "both") {
    // The hierarchy path may name a profession (per-profession sections)
    // OR be umbrella. Either way we leftjoin via documents → professions
    // by way of practice_acts, but since the load doesn't populate
    // practice_acts yet, we leave profession=NULL for statute hits and
    // let the client display "(umbrella)" vs the practice-act tag.
    const rows = await db.execute(sql`
      SELECT d.state,
             NULL::text AS profession,
             d.citation,
             d.label,
             d.hierarchy_level,
             d.is_umbrella,
             ts_headline(
               'english',
               d.text,
               ${tsq},
               'MaxFragments=2,MaxWords=24,MinWords=10,ShortWord=3,HighlightAll=false'
             ) AS snippet,
             ts_rank(d.text_tsv, ${tsq}) AS rank
      FROM documents d
      WHERE d.text_tsv @@ ${tsq}
        AND d.hierarchy_level = 'section'
        ${state ? sql`AND d.state = ${state}` : sql``}
      ORDER BY rank DESC
      LIMIT ${MAX_RESULTS}
    `);
    statutes = (rows as unknown as StatuteHit[]).map((r) => ({ ...r, kind: "statute" }));
  }

  return NextResponse.json({ q, quotes, statutes });
}

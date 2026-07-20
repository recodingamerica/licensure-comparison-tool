"use client";

// StateStatutesView — state portfolio / structural overview.
//
// Shows which professions one state regulates, each linked to the
// /professions/<X> cross-state page. A prominent "Open full statute tree"
// button leads to /browse/<state> where the filterable hierarchy lives.
//
// Does NOT inline the per-(state, profession) statute content (lives at
// /professions/<X>?view=statutes and /browse/<state>/<X>) and does NOT list
// the cross-cutting umbrella chapters separately — the tree groups statutes
// by audience tier, which is the richer place to see them.

import { useMemo, useState } from "react";
import Link from "next/link";
import type { StateBrowsePayload } from "@/lib/state-browse-types";
import { professionStyle, useProfessionMeta } from "@/lib/profession-colors";
import { humanize as fmtProf } from "@/lib/format";
import { Eyebrow } from "@/components/ui/eyebrow";

function summariseForProfession(payload: StateBrowsePayload, prof: string) {
  let practice = 0,
    universal = 0,
    multi = 0;
  for (const s of payload.sections) {
    if (s.audience === "universal") universal++;
    else if (s.audience === "multi" && (s.applies_to ?? []).includes(prof)) multi++;
    else if (s.audience === "single" && s.profession === prof) practice++;
  }
  return { practice, universal, multi };
}

function ProfessionEntry({
  state,
  prof,
  practice,
  universal,
  multi,
}: {
  state: string;
  prof: string;
  practice: number;
  universal: number;
  multi: number;
}) {
  return (
    <div className="rounded border bg-card hover:border-foreground/30 transition-colors px-4 py-3 flex items-center justify-between gap-4 flex-wrap">
      <div className="flex items-baseline gap-3 flex-wrap">
        <Link
          href={`/professions/${prof}/`}
          className="text-lg font-semibold underline-offset-2 hover:underline flex items-center gap-2"
        >
          <span className={`w-2 h-2 rounded-full shrink-0 ${professionStyle(prof).dot}`} />
          {fmtProf(prof)}
        </Link>
        <span className="text-xs text-muted-foreground flex flex-wrap items-center gap-2">
          <span>
            <strong className="text-foreground">{practice}</strong> practice-act section
            {practice === 1 ? "" : "s"}
          </span>
          {universal > 0 && (
            <span>
              · <strong className="text-foreground">{universal}</strong> universal umbrella
            </span>
          )}
          {multi > 0 && (
            <span>
              · <strong className="text-foreground">{multi}</strong> shared
            </span>
          )}
        </span>
      </div>
      <span className="text-xs flex items-center gap-3">
        <Link
          href={`/browse/${state}/${prof}`}
          className="text-muted-foreground hover:text-foreground underline-offset-2 hover:underline"
        >
          full statute tree →
        </Link>
        <Link
          href={`/professions/${prof}/`}
          className="text-muted-foreground hover:text-foreground underline-offset-2 hover:underline"
        >
          profession page →
        </Link>
      </span>
    </div>
  );
}

export function StateStatutesView({ payload }: { payload: StateBrowsePayload }) {
  const [profFilter] = useState<string>("all");
  void profFilter;
  // Trigger /professions.json load so the family-color dots resolve.
  useProfessionMeta();

  const summaries = useMemo(() => {
    return payload.professions_available
      .map((prof) => ({ prof, ...summariseForProfession(payload, prof) }))
      .filter((s) => s.practice + s.universal + s.multi > 0)
      .sort((a, b) => b.practice - a.practice || a.prof.localeCompare(b.prof));
  }, [payload]);

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <p className="text-sm text-muted-foreground max-w-3xl">
          {summaries.length} profession{summaries.length === 1 ? "" : "s"} regulated in{" "}
          {payload.state}. Click a profession to compare it across states, or open the full
          statute tree to read this state&apos;s hierarchy with profession + audience filters.
        </p>
        <Link
          href={`/browse/${payload.state}/`}
          className="text-sm rounded border px-3 py-2 bg-card hover:border-foreground/30 hover:bg-muted/30 transition-colors whitespace-nowrap"
        >
          Open full statute tree →
        </Link>
      </div>

      <section>
        <Eyebrow as="h2" className="mb-3">
          Professions regulated
        </Eyebrow>
        <div className="grid gap-3">
          {summaries.map((s) => (
            <ProfessionEntry
              key={s.prof}
              state={payload.state}
              prof={s.prof}
              practice={s.practice}
              universal={s.universal}
              multi={s.multi}
            />
          ))}
        </div>
      </section>
    </div>
  );
}

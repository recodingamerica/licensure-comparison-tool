import Link from "next/link";

import { BackLink } from "@/components/ui/back-link";
import { Eyebrow } from "@/components/ui/eyebrow";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";

// Reports index. As we add more generated artifacts (scorecards, citation
// audits, field listings, etc.), they get registered here so the homepage
// link stays useful as the list grows.

const REPORTS = [
  {
    href: "/reports/scorecard",
    title: "Universal field cross-comparison",
    blurb:
      "Per (universal field × profession), fraction of states populating each field. Mirrors Atharv's PDF cross-comparison table at full coverage.",
  },
  {
    href: "/reports/tag-sheet",
    title: "Field tag sheet",
    blurb:
      "Plain-English tags for each profession's key licensure fields (degree, experience, licensing authority, scope, discipline), with how many states fall under each tag.",
  },
];

export default function ReportsPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <BackLink href="/">home</BackLink>
      <Eyebrow className="mt-6 mb-3">Reports & artifacts</Eyebrow>
      <h1 className="text-3xl font-semibold tracking-tight mb-2">Reports</h1>
      <p className="text-muted-foreground mb-8 max-w-2xl">
        Generated artifacts built off the same data the profession pages run on,
        plus per-build summaries. Re-run automatically when the data is rebuilt.
      </p>

      <div className="grid gap-3">
        {REPORTS.map((r) => (
          <Link key={r.href} href={r.href} className="block group">
            <Card className="py-3 transition-colors hover:border-foreground/30">
              <CardHeader className="space-y-1">
                <CardTitle className="text-base font-medium group-hover:underline">
                  {r.title}
                </CardTitle>
                <p className="text-xs text-muted-foreground">{r.blurb}</p>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </main>
  );
}

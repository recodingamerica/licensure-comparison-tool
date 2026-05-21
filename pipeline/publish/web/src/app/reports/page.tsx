import Link from "next/link";
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
];

export default function ReportsPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <Link
        href="/"
        className="text-xs font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
      >
        ← home
      </Link>
      <p className="mt-6 text-xs font-mono tracking-widest uppercase text-muted-foreground mb-3">
        Reports & artifacts
      </p>
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

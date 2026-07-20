"use client";

import { BackLink } from "@/components/ui/back-link";
import { Eyebrow } from "@/components/ui/eyebrow";
import { useEffect, useState } from "react";
import { SEMANTIC_CLASSES as SC } from "@/lib/web-colors";

// Shape of `public/data/scorecard.json` — produced by
// `python -m pipeline.publish.cross_comparison_scorecard`.
type Cell = { filled: number; total: number; symbol: string };
type Payload = {
  generated_at: string;
  professions: string[];
  fields: { label: string; professions: Record<string, Cell> }[];
};

// Display name overrides so the header row reads like Atharv's PDF table
// rather than our internal snake_case profession keys.
const PROFESSION_LABELS: Record<string, string> = {
  podiatry: "Podiatry",
  nursing: "Nursing",
  medicine: "Medicine",
  dentistry: "Dentistry",
  optometry: "Optometry",
  public_accountancy: "Accountancy",
  construction_trades: "Contractors",
  electrician: "Electricians",
  plumbing: "Plumbers",
  hvac: "HVAC",
};

const SYMBOL_CLASS: Record<string, string> = {
  "✓": SC.permissive.text,
  "~": SC.attention.text,
  "✗": SC.restrictive.text,
  "—": "text-muted-foreground",
};

export default function ScorecardPage() {
  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/data/scorecard.json")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d: Payload) => setData(d))
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <BackLink href="/">home</BackLink>

      <Eyebrow className="mt-6">Report</Eyebrow>
      <h1 className="text-3xl font-semibold tracking-tight mt-1 mb-2">
        Universal field cross-comparison
      </h1>
      <p className="text-muted-foreground max-w-3xl mb-6">
        How well our extracted data matches Atharv&apos;s universal-field
        schema. One row per field, one column per profession. Each cell
        shows{" "}
        <span className="font-mono">symbol (populated/total)</span> —{" "}
        <span className={`${SYMBOL_CLASS["✓"]} font-mono`}>✓</span> ≥80% populated,{" "}
        <span className={`${SYMBOL_CLASS["~"]} font-mono`}>~</span> 1–79%,{" "}
        <span className={`${SYMBOL_CLASS["✗"]} font-mono`}>✗</span> 0%.
      </p>

      {error && (
        <div className="rounded border border-destructive bg-destructive/5 px-4 py-3 text-sm text-destructive">
          Failed to load scorecard: {error}
        </div>
      )}

      {!data && !error && (
        <p className="text-sm text-muted-foreground">Loading…</p>
      )}

      {data && (
        <>
          <p className="text-xs font-mono text-muted-foreground mb-4">
            Generated {new Date(data.generated_at).toLocaleString()}
          </p>
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="bg-muted/40">
                <tr>
                  <th className="text-left px-4 py-3 font-medium">
                    Universal Category
                  </th>
                  {data.professions.map((p) => (
                    <th key={p} className="text-center px-4 py-3 font-medium whitespace-nowrap">
                      {PROFESSION_LABELS[p] ?? p}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.fields.map((f) => (
                  <tr key={f.label} className="border-t">
                    <td className="px-4 py-2.5">{f.label}</td>
                    {data.professions.map((p) => {
                      const c = f.professions[p];
                      const cls = SYMBOL_CLASS[c.symbol] ?? "";
                      return (
                        <td
                          key={p}
                          className={`text-center px-4 py-2.5 font-mono text-xs ${cls}`}
                          title={`${c.filled} of ${c.total} states populated`}
                        >
                          <span className="font-semibold">{c.symbol}</span>{" "}
                          <span className="text-muted-foreground">
                            {c.filled}/{c.total}
                          </span>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </main>
  );
}

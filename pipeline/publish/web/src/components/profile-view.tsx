"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { ProfilePayload, Row } from "@/lib/types";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { humanize } from "@/lib/format";
import { StateDetailDialog } from "./state-detail-dialog";

const PILL = {
  yes: "bg-emerald-100 text-emerald-900 hover:bg-emerald-100",
  no: "bg-rose-100 text-rose-900 hover:bg-rose-100",
  unk: "bg-muted text-muted-foreground hover:bg-muted",
} as const;

function YesNo({ v }: { v: boolean | null }) {
  if (v === true)
    return <Badge variant="secondary" className={PILL.yes}>yes</Badge>;
  if (v === false)
    return <Badge variant="secondary" className={PILL.no}>no</Badge>;
  return <span className="text-muted-foreground">—</span>;
}

function Cell({ value }: { value: string | number | null | undefined }) {
  if (value === null || value === undefined || value === "")
    return <span className="text-muted-foreground">—</span>;
  return <>{value}</>;
}

function VerifyBadge({ row }: { row: Row }) {
  if (row.coverage_gap)
    return <span className="text-muted-foreground">—</span>;
  const v = row.evidence_verified || 0;
  const u = row.evidence_unverified || 0;
  if (v + u === 0) return <span className="text-muted-foreground">—</span>;
  return (
    <span
      className={
        "font-mono text-xs " +
        (u > 0 ? "text-amber-700" : "text-emerald-700")
      }
      title="Verbatim quotes regex-checked against the cleaned source"
    >
      {u > 0 ? "⚠ " : "✓ "}
      {v}/{v + u}
    </span>
  );
}

function regChip(slug: string | null) {
  if (!slug) return null;
  const colors: Record<string, string> = {
    license: "bg-sky-100 text-sky-900",
    mandatory_certification: "bg-emerald-100 text-emerald-900",
    registration: "bg-amber-100 text-amber-900",
    exemption: "bg-zinc-100 text-zinc-700",
    voluntary_certification: "bg-violet-100 text-violet-900",
    market_forces: "bg-rose-100 text-rose-900",
  };
  const cls = colors[slug] || "bg-muted text-muted-foreground";
  return (
    <Badge variant="secondary" className={cls + " hover:" + cls}>
      {humanize(slug)}
    </Badge>
  );
}

export function ProfileView({ payload }: { payload: ProfilePayload }) {
  const { rows, evidence_summary, discovered_fields } = payload;
  const display = payload.display || payload.profession;
  const covered = rows.filter((r) => !r.coverage_gap).length;
  const gaps = rows.length - covered;
  const total = (evidence_summary?.verified || 0) + (evidence_summary?.unverified || 0);
  const pct = total
    ? ((100 * (evidence_summary?.verified || 0)) / total).toFixed(1)
    : "—";

  // Filters
  const [search, setSearch] = useState("");
  const [regModelFilter, setRegModelFilter] = useState<string | null>(null);
  const [reciprocityFilter, setReciprocityFilter] = useState<string | null>(null);
  const [openState, setOpenState] = useState<string | null>(null);

  const regModels = useMemo(() => {
    const s = new Set<string>();
    rows.forEach((r) => r.regulatory_model && s.add(r.regulatory_model));
    return Array.from(s).sort();
  }, [rows]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return rows.filter((r) => {
      if (q) {
        const hay = [
          r.state,
          r.issuing_authority,
          r.education_degree,
          r.regulatory_model,
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();
        if (!hay.includes(q)) return false;
      }
      if (regModelFilter && r.regulatory_model !== regModelFilter)
        return false;
      if (reciprocityFilter) {
        const want = reciprocityFilter === "yes";
        if (r.reciprocity_available !== want) return false;
      }
      return true;
    });
  }, [rows, search, regModelFilter, reciprocityFilter]);

  return (
    <main className="mx-auto max-w-7xl px-6 py-10">
      <Link
        href="/"
        className="text-xs font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
      >
        ← all professions
      </Link>

      <p className="mt-6 text-xs font-mono tracking-widest uppercase text-muted-foreground">
        Profession profile
      </p>
      <h1 className="text-3xl font-semibold tracking-tight mt-1 mb-2">
        {display}
      </h1>
      <p className="text-muted-foreground max-w-3xl mb-6">
        Side-by-side licensure and scope of practice across 50 states,
        auto-extracted from state statutes. Every claim is backed by a
        verbatim quote validated against the source — click any row to see the
        quotes and citations.
      </p>

      <div className="flex flex-wrap gap-x-8 gap-y-2 rounded-lg border bg-muted/30 px-4 py-3 mb-8 text-sm">
        <Stat label="states with extracted records" value={covered} />
        <Stat label="coverage gaps" value={gaps} />
        <Stat label="auto-discovered profession-specific fields" value={discovered_fields.length} />
        <Stat
          label={`evidence verified (${evidence_summary?.verified}/${total} quotes match source)`}
          value={`${pct}%`}
        />
      </div>

      <div className="flex flex-wrap gap-3 items-center mb-4">
        <Input
          placeholder="Search state, board, education…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
        <Select value={regModelFilter ?? ""} onValueChange={(v) => setRegModelFilter(v || null)}>
          <SelectTrigger className="w-[220px]">
            <SelectValue placeholder="All regulatory models" />
          </SelectTrigger>
          <SelectContent>
            {regModels.map((m) => (
              <SelectItem key={m} value={m}>{humanize(m)}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        {regModelFilter && (
          <button
            onClick={() => setRegModelFilter(null)}
            className="text-xs font-mono text-muted-foreground hover:text-foreground"
          >
            clear
          </button>
        )}
        <Select value={reciprocityFilter ?? ""} onValueChange={(v) => setReciprocityFilter(v || null)}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="All reciprocity" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="yes">reciprocity: yes</SelectItem>
            <SelectItem value="no">reciprocity: no</SelectItem>
          </SelectContent>
        </Select>
        {reciprocityFilter && (
          <button
            onClick={() => setReciprocityFilter(null)}
            className="text-xs font-mono text-muted-foreground hover:text-foreground"
          >
            clear
          </button>
        )}
        <span className="text-xs font-mono text-muted-foreground ml-auto">
          {filtered.length} of {rows.length} states
        </span>
      </div>

      <div className="rounded-lg border overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-12">State</TableHead>
              <TableHead>Regulatory model</TableHead>
              <TableHead>Issuing authority</TableHead>
              <TableHead>Education</TableHead>
              <TableHead>Post-degree exp.</TableHead>
              <TableHead className="text-center">Exams</TableHead>
              <TableHead className="text-center">Renewal (yrs)</TableHead>
              <TableHead className="text-center">CE hrs / yrs</TableHead>
              <TableHead className="text-center">Reciprocity</TableHead>
              <TableHead className="text-center">Evidence</TableHead>
              <TableHead className="w-16"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((r) => (
              <TableRow key={r.state} className="align-top">
                <TableCell className="font-mono text-sm">{r.state}</TableCell>
                <TableCell>
                  {r.coverage_gap ? (
                    <span
                      className="text-xs italic text-muted-foreground"
                      title={r.coverage_gap_reason || ""}
                    >
                      {r.coverage_gap_label || "—"}
                    </span>
                  ) : (
                    regChip(r.regulatory_model)
                  )}
                </TableCell>
                <TableCell className="text-sm"><Cell value={r.issuing_authority} /></TableCell>
                <TableCell className="text-sm"><Cell value={r.education_degree} /></TableCell>
                <TableCell className="text-sm"><Cell value={r.post_degree_duration} /></TableCell>
                <TableCell className="text-center text-sm"><Cell value={r.exams_count || null} /></TableCell>
                <TableCell className="text-center text-sm"><Cell value={r.renewal_years} /></TableCell>
                <TableCell className="text-center text-sm">
                  {r.ce_hours == null && r.ce_period_years == null ? (
                    <span className="text-muted-foreground">—</span>
                  ) : (
                    <>{r.ce_hours ?? "—"} / {r.ce_period_years ?? "—"}</>
                  )}
                </TableCell>
                <TableCell className="text-center"><YesNo v={r.reciprocity_available} /></TableCell>
                <TableCell className="text-center"><VerifyBadge row={r} /></TableCell>
                <TableCell>
                  <button
                    onClick={() => setOpenState(r.state)}
                    className="text-xs font-mono uppercase tracking-wide text-muted-foreground hover:text-foreground"
                  >
                    view
                  </button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <StateDetailDialog
        rows={rows}
        fields={discovered_fields}
        openState={openState}
        onOpenChange={(o) => !o && setOpenState(null)}
      />
    </main>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <span className="font-semibold text-foreground">{value}</span>{" "}
      <span className="text-muted-foreground">{label}</span>
    </div>
  );
}

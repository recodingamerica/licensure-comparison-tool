"use client";

// State-comparison matrix (Scope tab). Every bool/enum/list field that carries a
// meaningful included / excluded / not-addressed signal, per state, grouped by
// the field's plain-English category. Built from ALREADY-EXTRACTED values (no
// re-extraction) by pipeline/publish/build_scope_matrices.py.
//   included_excluded : bool (polarity-normalized) or a re-extracted list item →
//                        included (teal) / excluded (red) / not addressed (grey)
//   condition         : *_required bool → required (amber) / not (faint) / · (grey)
//   graded            : enum → per-state value on an ordinal ramp; explicit
//                        not_authorized/excluded values render red. Value on hover.
// Data: /data/scope_matrices.json.

import { useMemo, useState } from "react";
import { useJsonData } from "@/lib/use-json-data";
import { useOpenStateDetail } from "@/components/state-focus";
import { SEMANTIC_CLASSES as SC } from "@/lib/web-colors";
import { STATE_CODES as STATES, FOCUS_STATE as FOCUS } from "@/lib/states";

type Kind = "included_excluded" | "condition" | "graded";
type Row = {
  label: string;
  field: string;
  kind: Kind;
  cells: Record<string, string>;
  category: string;
  is_scope: boolean;
  order?: string[];
  excluded_values?: string[];
};
type Data = Record<string, { display: string; rows: Row[] }>;

const TEAL = "var(--scope-has)";
const RED = "var(--scope-prohibited)";
const GREY = "var(--scope-none)";
const AMBER = "var(--scope-focus)";

function cellColor(row: Row, value: string | undefined): string {
  if (value == null || value === "not_addressed") return GREY;
  if (row.kind === "graded") {
    if (row.excluded_values?.includes(value)) return RED;
    const order = row.order ?? [];
    const idx = Math.max(0, order.indexOf(value));
    const frac = order.length > 1 ? idx / (order.length - 1) : 1;
    // light→dark teal ramp by position (opacity over the teal token)
    return `color-mix(in srgb, ${TEAL} ${Math.round(35 + 55 * frac)}%, transparent)`;
  }
  if (value === "included") return TEAL;
  if (value === "excluded") return RED;
  if (value === "required") return AMBER;
  if (value === "not_required") return `color-mix(in srgb, ${AMBER} 22%, transparent)`;
  return GREY;
}

function cellTitle(state: string, row: Row, value: string | undefined): string {
  const v = value && value !== "not_addressed" ? value.replace(/_/g, " ") : "not addressed";
  return `${state} · ${row.label}: ${v}`;
}

export function ScopeMatrixView({ professionId }: { professionId: string }) {
  const open = useOpenStateDetail();
  const { data: all } = useJsonData<Data>("/data/scope_matrices.json");
  const [scopeOnly, setScopeOnly] = useState(false);
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});

  const prof = all?.[professionId];

  // Group rows by category; scope categories first, then by row count.
  const groups = useMemo(() => {
    const rows = (prof?.rows ?? []).filter((r) => !scopeOnly || r.is_scope);
    const by = new Map<string, Row[]>();
    for (const r of rows) {
      if (!by.has(r.category)) by.set(r.category, []);
      by.get(r.category)!.push(r);
    }
    return [...by.entries()]
      .map(([category, rs]) => ({
        category,
        rows: rs,
        anyScope: rs.some((r) => r.is_scope),
      }))
      .sort((a, b) => Number(b.anyScope) - Number(a.anyScope) || b.rows.length - a.rows.length);
  }, [prof, scopeOnly]);

  if (!all || !prof) return null;
  const totalRows = prof.rows.length;
  const scopeRows = prof.rows.filter((r) => r.is_scope).length;

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-sm font-medium">State-by-state comparison — included / excluded / not addressed</h3>
        <p className="max-w-3xl text-xs text-muted-foreground">
          Every attribute where the statute gives a per-state yes/no signal, grouped by category.
          <span style={{ color: "var(--scope-has)" }}> Teal = included/authorized</span>,
          <span style={{ color: "var(--scope-prohibited)" }}> red = explicitly excluded/prohibited</span>,
          grey = not addressed;
          <span style={{ color: "var(--scope-focus)" }}> amber = a required condition</span>;
          graded (enum) fields ramp by level and show the value on hover. Utah is highlighted. Built from
          already-extracted data — no re-extraction.
        </p>
      </div>

      <div className="flex items-center gap-4 text-xs">
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={scopeOnly} onChange={(e) => setScopeOnly(e.target.checked)} />
          Scope-of-practice fields only
        </label>
        <span className="text-muted-foreground tabular-nums">
          {scopeOnly ? scopeRows : totalRows} rows · {groups.length} categories
        </span>
      </div>

      {groups.map((g) => {
        const isCol = collapsed[g.category];
        return (
          <div key={g.category} className="rounded-md border">
            <button
              onClick={() => setCollapsed((c) => ({ ...c, [g.category]: !c[g.category] }))}
              className="flex w-full items-center justify-between px-4 py-2 text-left"
            >
              <span className="text-sm font-medium capitalize">
                {g.category}
                {g.anyScope && (
                  <span className="ml-2 rounded bg-muted px-1.5 py-0.5 text-[10px] font-normal uppercase tracking-wide text-muted-foreground">
                    scope
                  </span>
                )}
              </span>
              <span className="font-mono text-[11px] text-muted-foreground">
                {g.rows.length} · {isCol ? "show" : "hide"}
              </span>
            </button>
            {!isCol && (
              <div className="overflow-x-auto p-2">
                <table className="border-separate border-spacing-0 text-xs">
                  <thead>
                    <tr>
                      <th className="sticky left-0 z-10 bg-card px-3 text-left align-bottom">
                        <span className="font-mono text-[10px] text-muted-foreground">attribute · state</span>
                      </th>
                      {STATES.map((s) => (
                        <th key={s} className="h-16 align-bottom text-center">
                          <span
                            className={"inline-block font-mono text-[10px] " + (s === FOCUS ? "font-bold" : "text-muted-foreground")}
                            style={{
                              writingMode: "vertical-rl",
                              transform: "rotate(180deg)",
                              paddingBottom: 3,
                              color: s === FOCUS ? "var(--scope-focus)" : undefined,
                            }}
                          >
                            {s}
                          </span>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {g.rows.map((r) => (
                      <tr key={r.field + r.label}>
                        <td
                          className="sticky left-0 z-10 bg-card px-3 py-0"
                          style={{ minWidth: 260, maxWidth: 260 }}
                        >
                          <span
                            className="block max-w-[236px] overflow-hidden text-ellipsis whitespace-nowrap font-medium"
                            title={r.label}
                          >
                            {r.label}
                          </span>
                        </td>
                        {STATES.map((s) => {
                          const v = r.cells[s];
                          return (
                            <td
                              key={s}
                              // Every cell here IS a (state, field) pair, so it follows the
                              // standard: click opens that state's Sheet filtered to this
                              // field. Only interactive when a Sheet exists in the tree.
                              className={`p-0 ${open ? `cursor-pointer focus-visible:outline-none focus-visible:ring-2 ${SC.interaction.focusRing}` : ""}`}
                              style={{ width: 19, height: 19, background: s === FOCUS ? "var(--scope-focus-weak)" : undefined }}
                              title={
                                open
                                  ? `${cellTitle(s, r, v)} · click to open ${s}`
                                  : cellTitle(s, r, v)
                              }
                              role={open ? "button" : undefined}
                              tabIndex={open ? 0 : undefined}
                              onClick={
                                open
                                  ? () =>
                                      open(s, {
                                        fieldPath: `profession_specific.${r.field}`,
                                      })
                                  : undefined
                              }
                              onKeyDown={
                                open
                                  ? (e) => {
                                      if (e.key === "Enter" || e.key === " ") {
                                        e.preventDefault();
                                        open(s, {
                                          fieldPath: `profession_specific.${r.field}`,
                                        });
                                      }
                                    }
                                  : undefined
                              }
                            >
                              <span
                                className="mx-auto my-0.5 block h-[15px] w-[15px] rounded-[3px]"
                                style={{
                                  background: cellColor(r, v),
                                  outline: s === FOCUS ? "1.5px solid var(--scope-focus)" : undefined,
                                  outlineOffset: -1,
                                }}
                              />
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

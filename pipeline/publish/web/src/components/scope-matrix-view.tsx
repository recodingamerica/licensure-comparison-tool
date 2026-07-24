"use client";

// Three-state scope MATRIX (Scope tab, above the capability presence-matrix).
// For a corpus-discovered vocabulary of a scope dimension (e.g. optometry laser
// procedures), each state is authorized / prohibited / not_addressed per item —
// the prohibited vs not-addressed distinction the binary capability view can't
// show. Data: /data/scope_matrices.json (built by
// pipeline/publish/build_scope_matrices.py). Renders nothing for a profession
// with no discovered scope matrices.

import { useMemo, useState } from "react";
import { UsMap } from "@/components/us-map";
import { useJsonData } from "@/lib/use-json-data";
import { token } from "@/lib/web-colors";
import { STATE_CODES as STATES, FOCUS_STATE as FOCUS } from "@/lib/states";

type Status = "authorized" | "prohibited" | "not_addressed" | "present" | "absent";
type Dimension = {
  source_field: string;
  label: string;
  eval_flavor: "three_state" | "present_absent";
  vocab: string[];
  matrix: Record<string, Record<string, Status>>;
};
type ScopeMatrices = Record<string, { display: string; dimensions: Dimension[] }>;

const CELL_VAR: Record<Status, string> = {
  authorized: "var(--scope-has)",
  present: "var(--scope-has)",
  prohibited: "var(--scope-prohibited)",
  not_addressed: "var(--scope-none)",
  absent: "var(--scope-none)",
};

function statusFor(dim: Dimension, state: string, item: string): Status {
  const s = dim.matrix[state]?.[item];
  if (s) return s;
  return dim.eval_flavor === "present_absent" ? "absent" : "not_addressed";
}

export function ScopeMatrixView({ professionId }: { professionId: string }) {
  const { data: all } = useJsonData<ScopeMatrices>("/data/scope_matrices.json");
  const [dimIdx, setDimIdx] = useState(0);
  const [itemIdx, setItemIdx] = useState(0);

  const prof = all?.[professionId];
  const dims = prof?.dimensions ?? [];
  const dim = dims[Math.min(dimIdx, Math.max(0, dims.length - 1))];

  // Per-item counts for the selected dimension (drives the map + summary).
  const counts = useMemo(() => {
    if (!dim) return { auth: 0, proh: 0 };
    const item = dim.vocab[Math.min(itemIdx, dim.vocab.length - 1)];
    let auth = 0, proh = 0;
    for (const s of STATES) {
      const st = statusFor(dim, s, item);
      if (st === "authorized" || st === "present") auth++;
      else if (st === "prohibited") proh++;
    }
    return { auth, proh };
  }, [dim, itemIdx]);

  if (!all || dims.length === 0 || !dim) return null;

  const selItem = dim.vocab[Math.min(itemIdx, dim.vocab.length - 1)];
  const authColor = token("scope-has");
  const prohColor = token("scope-prohibited");
  const noneColor = token("scope-none");
  const focusColor = token("scope-focus");
  const flavor = dim.eval_flavor;
  const authLabel = flavor === "present_absent" ? "provides for it" : "authorizes it";

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-sm font-medium">Scope matrices — discovered per procedure</h3>
        <p className="max-w-3xl text-xs text-muted-foreground">
          For a vocabulary of {dim.label.toLowerCase()} discovered from the statutes, each state is
          shown as {flavor === "present_absent" ? "present or absent" : (
            <>authorized, <span style={{ color: "var(--scope-prohibited)" }}>prohibited</span>, or not
            addressed</>
          )}. Unlike the capability matrix below, an explicit prohibition reads differently from silence.
          Utah is highlighted. Click a row to map it.
        </p>
      </div>

      {/* Dimension switcher */}
      {dims.length > 1 && (
        <div className="flex flex-wrap gap-2">
          {dims.map((d, i) => (
            <button
              key={d.source_field}
              onClick={() => { setDimIdx(i); setItemIdx(0); }}
              className={
                "rounded-md border px-3 py-1 text-xs " +
                (i === dimIdx ? "bg-muted font-medium" : "text-muted-foreground hover:bg-muted/50")
              }
            >
              {d.label} <span className="tabular-nums">({d.vocab.length})</span>
            </button>
          ))}
        </div>
      )}

      {/* Matrix */}
      <div className="rounded-md border">
        <div className="overflow-x-auto p-2">
          <table className="border-separate border-spacing-0 text-xs">
            <thead>
              <tr>
                <th className="sticky left-0 z-10 bg-card px-3 text-left align-bottom">
                  <span className="font-mono text-[10px] text-muted-foreground">procedure · state</span>
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
              {dim.vocab.map((item, i) => {
                const isSel = i === Math.min(itemIdx, dim.vocab.length - 1);
                const nAuth = STATES.filter((s) => {
                  const st = statusFor(dim, s, item);
                  return st === "authorized" || st === "present";
                }).length;
                return (
                  <tr key={item} onClick={() => setItemIdx(i)} className="cursor-pointer">
                    <td
                      className="sticky left-0 z-10 bg-card px-3 py-0"
                      style={{ minWidth: 250, maxWidth: 250, background: isSel ? "var(--scope-focus-weak)" : undefined }}
                    >
                      <span
                        className="block max-w-[226px] overflow-hidden text-ellipsis whitespace-nowrap font-medium"
                        style={{ color: isSel ? "var(--scope-focus)" : undefined }}
                        title={item}
                      >
                        {item}
                      </span>
                      <span className="block font-mono text-[11px] text-muted-foreground tabular-nums">
                        {nAuth} {flavor === "present_absent" ? "have" : "authorize"}
                      </span>
                    </td>
                    {STATES.map((s) => {
                      const st = statusFor(dim, s, item);
                      return (
                        <td
                          key={s}
                          className="p-0"
                          style={{ width: 19, height: 19, background: s === FOCUS ? "var(--scope-focus-weak)" : undefined }}
                          title={`${s}: ${st.replace("_", " ")}`}
                        >
                          <span
                            className="mx-auto my-0.5 block h-[15px] w-[15px] rounded-[3px]"
                            style={{
                              background: CELL_VAR[st],
                              outline: s === FOCUS ? "1.5px solid var(--scope-focus)" : undefined,
                              outlineOffset: -1,
                            }}
                          />
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Per-item map + legend */}
      <div className="grid gap-5 md:grid-cols-[minmax(0,1fr)_260px] md:items-start">
        <div className="rounded-md border">
          <div className="px-4 pt-3">
            <div className="text-sm font-semibold">{selItem}</div>
            <div className="text-xs text-muted-foreground tabular-nums">
              {counts.auth} {authLabel} · {counts.proh} prohibit · {STATES.length - counts.auth - counts.proh} silent
            </div>
          </div>
          <div className="px-3 pb-3 pt-1">
            <UsMap
              key={dim.source_field + selItem}
              bare
              highlightState={FOCUS}
              highlightColor={focusColor}
              fillFor={(st) => {
                const s = statusFor(dim, st, selItem);
                return s === "authorized" || s === "present" ? authColor : s === "prohibited" ? prohColor : noneColor;
              }}
              renderTooltip={(st) => (
                <div className="text-xs">
                  <span className="font-mono font-semibold">{st}</span>{" "}
                  {statusFor(dim, st, selItem).replace("_", " ")}
                </div>
              )}
            />
          </div>
        </div>
        <div className="rounded-md border p-4 text-xs">
          <div className="mb-3 flex flex-col gap-2 text-muted-foreground">
            <span className="inline-flex items-center gap-1.5">
              <span className="inline-block h-3 w-3 rounded-[3px]" style={{ background: "var(--scope-has)" }} />
              {authLabel}
            </span>
            {flavor !== "present_absent" && (
              <span className="inline-flex items-center gap-1.5">
                <span className="inline-block h-3 w-3 rounded-[3px]" style={{ background: "var(--scope-prohibited)" }} />
                statute prohibits it
              </span>
            )}
            <span className="inline-flex items-center gap-1.5">
              <span className="inline-block h-3 w-3 rounded-[3px]" style={{ background: "var(--scope-none)" }} />
              {flavor === "present_absent" ? "absent" : "not addressed"}
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="inline-block h-3 w-3 rounded-[3px] border-2" style={{ borderColor: "var(--scope-focus)" }} />
              Utah
            </span>
          </div>
          <p className="leading-relaxed text-muted-foreground">
            The vocabulary is discovered from the corpus, then every item is classified per state.
            Click a procedure to map it.
          </p>
        </div>
      </div>
    </div>
  );
}

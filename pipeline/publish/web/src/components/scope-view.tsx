"use client";

// Scope of Practice view (Map tab). Scope is multi-dimensional and list/text-
// valued, so a single choropleth can't represent it. This shows the capabilities
// that are comparable across states (present in >= N of them) as a presence
// matrix, with a per-capability US map below. Data: /data/scope_capabilities.json
// (built by pipeline/publish/build_scope_capabilities.py). Colors come from the
// token source (config/web_colors.yaml -> var(--scope-*) / token()).

import { useMemo, useState } from "react";
import { UsMap } from "@/components/us-map";
import { useJsonData } from "@/lib/use-json-data";
import { token } from "@/lib/web-colors";
import { STATE_CODES as STATES, FOCUS_STATE as FOCUS } from "@/lib/states";

type Capability = { label: string; states: string[] };
type ScopeData = Record<string, { display: string; capabilities: Capability[] }>;

export function ScopeView({ professionId }: { professionId: string }) {
  const { data: all, error: err } = useJsonData<ScopeData>("/data/scope_capabilities.json");
  const [n, setN] = useState(15);
  const [sel, setSel] = useState(0);

  const caps = all?.[professionId]?.capabilities ?? [];
  const shown = useMemo(() => caps.filter((c) => c.states.length >= n), [caps, n]);
  const hidden = caps.length - shown.length;
  const selCap = shown[Math.min(sel, Math.max(0, shown.length - 1))];

  if (err) return <p className="text-sm text-destructive">Couldn&apos;t load scope data.</p>;
  if (!all) return <p className="text-xs text-muted-foreground">Loading…</p>;

  // Resolve token colors for the map fills (SVG fill needs a concrete value, not
  // a CSS var); read per render so a theme toggle re-colors on the next render.
  const hasColor = token("scope-has");
  const noneColor = token("map-no-data");
  const focusColor = token("scope-focus");

  return (
    <div className="space-y-5">
      <p className="text-sm text-muted-foreground max-w-3xl">
        Scope of practice differs from state to state along many separate capabilities.
        This shows the ones comparable across states — present in ≥ N of them — as a
        presence matrix, with a per-capability map. Drag N to set how widely shared a
        capability has to be to appear.
      </p>

      {/* N control + counts */}
      <div className="flex flex-wrap items-center gap-x-6 gap-y-2 rounded-md border bg-muted/30 px-4 py-3">
        <label className="flex items-center gap-3 text-xs">
          <span className="font-mono uppercase tracking-wider text-muted-foreground">
            Show capabilities in ≥ N states
          </span>
          <input
            type="range"
            min={5}
            max={30}
            value={n}
            onChange={(e) => {
              setN(+e.target.value);
              setSel(0);
            }}
            className="w-40"
          />
          <span className="font-mono text-base font-semibold tabular-nums">{n}</span>
        </label>
        <span className="text-xs text-muted-foreground">
          <strong className="text-foreground tabular-nums">{shown.length}</strong> comparable
          {" · "}
          <strong className="tabular-nums">{hidden}</strong> hidden (rarer)
        </span>
      </div>

      {shown.length === 0 ? (
        <div className="rounded-md border p-6 text-sm text-muted-foreground">
          No capabilities are shared across ≥ {n} states for this profession — its scope is
          nearly all state-specific one-offs ({caps.length} rarer capabilities). There&apos;s
          little to compare geographically here; lower N, or read the scope definition per
          state in the table. Rare capabilities live in the <span className="font-medium">Tags</span> tab.
        </div>
      ) : (
        <>
          {/* Presence matrix */}
          <div className="rounded-md border">
            <div className="border-b px-4 py-2.5">
              <h3 className="text-sm font-medium">Comparable capabilities</h3>
              <p className="text-xs text-muted-foreground">
                Each row is a capability shared across ≥ {n} states; a filled cell means that
                state authorizes it. Utah is highlighted. Click a row to map it.
              </p>
            </div>
            <div className="overflow-x-auto p-2">
              <table className="border-separate border-spacing-0 text-xs">
                <thead>
                  <tr>
                    <th className="sticky left-0 z-10 bg-card px-3 text-left align-bottom">
                      <span className="font-mono text-[10px] text-muted-foreground">
                        capability · state
                      </span>
                    </th>
                    {STATES.map((s) => (
                      <th key={s} className="h-16 align-bottom text-center">
                        <span
                          className={
                            "inline-block font-mono text-[10px] " +
                            (s === FOCUS ? "font-bold" : "text-muted-foreground")
                          }
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
                  {shown.map((c, i) => {
                    const set = new Set(c.states);
                    const isSel = i === Math.min(sel, shown.length - 1);
                    return (
                      <tr
                        key={c.label}
                        onClick={() => setSel(i)}
                        className="cursor-pointer"
                      >
                        <td
                          className="sticky left-0 z-10 bg-card px-3 py-0"
                          style={{
                            minWidth: 230,
                            maxWidth: 230,
                            background: isSel ? "var(--scope-focus-weak)" : undefined,
                          }}
                        >
                          <span
                            className="block max-w-[206px] overflow-hidden text-ellipsis whitespace-nowrap font-medium"
                            style={{ color: isSel ? "var(--scope-focus)" : undefined }}
                            title={c.label}
                          >
                            {c.label}
                          </span>
                          <span className="block font-mono text-[11px] text-muted-foreground">
                            {c.states.length} states
                          </span>
                        </td>
                        {STATES.map((s) => (
                          <td
                            key={s}
                            className="p-0"
                            style={{
                              width: 19,
                              height: 19,
                              background:
                                s === FOCUS ? "var(--scope-focus-weak)" : undefined,
                            }}
                          >
                            <span
                              className="mx-auto my-0.5 block h-[15px] w-[15px] rounded-[3px]"
                              style={{
                                background: set.has(s)
                                  ? "var(--scope-has)"
                                  : "var(--scope-none)",
                                outline:
                                  set.has(s) && s === FOCUS
                                    ? "1.5px solid var(--scope-focus)"
                                    : undefined,
                                outlineOffset: -1,
                              }}
                            />
                          </td>
                        ))}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <p className="px-4 pb-3 pt-1 text-xs text-muted-foreground">
              Not shown: <strong className="text-foreground">{hidden}</strong> rarer
              capabilit{hidden === 1 ? "y" : "ies"} in fewer than {n} states — the long tail
              of state-specific one-offs, which live in the Tags tab.
            </p>
          </div>

          {/* Per-capability map + legend */}
          <div className="grid gap-5 md:grid-cols-[minmax(0,1fr)_260px] md:items-start">
            <div className="rounded-md border">
              {selCap && (
                <>
                  <div className="px-4 pt-3">
                    <div className="text-sm font-semibold">{selCap.label}</div>
                    <div className="text-xs text-muted-foreground">
                      {selCap.states.length} of {STATES.length} states · Utah outlined
                    </div>
                  </div>
                  <div className="px-3 pb-3 pt-1">
                    <UsMap
                      key={selCap.label}
                      bare
                      highlightState={FOCUS}
                      highlightColor={focusColor}
                      fillFor={(st) =>
                        new Set(selCap.states).has(st) ? hasColor : noneColor
                      }
                      renderTooltip={(st) => (
                        <div className="text-xs">
                          <span className="font-mono font-semibold">{st}</span>{" "}
                          {new Set(selCap.states).has(st) ? "authorizes it" : "doesn't"}
                        </div>
                      )}
                    />
                  </div>
                </>
              )}
            </div>
            <div className="rounded-md border p-4 text-xs">
              <div className="mb-3 flex flex-wrap gap-3 text-muted-foreground">
                <span className="inline-flex items-center gap-1.5">
                  <span
                    className="inline-block h-3 w-3 rounded-[3px]"
                    style={{ background: "var(--scope-has)" }}
                  />
                  authorizes it
                </span>
                <span className="inline-flex items-center gap-1.5">
                  <span
                    className="inline-block h-3 w-3 rounded-[3px]"
                    style={{ background: "var(--scope-none)" }}
                  />
                  doesn&apos;t
                </span>
                <span className="inline-flex items-center gap-1.5">
                  <span
                    className="inline-block h-3 w-3 rounded-[3px] border-2"
                    style={{ borderColor: "var(--scope-focus)" }}
                  />
                  Utah
                </span>
              </div>
              <p className="text-muted-foreground leading-relaxed">
                Only capabilities shared across ≥ N states are shown; drag N to trade coverage
                for a tighter set. Click a capability to map it. Rarer, state-specific
                capabilities live in the Tags tab.
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

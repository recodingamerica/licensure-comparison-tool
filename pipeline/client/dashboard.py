"""Generate the client dashboard — a single self-contained HTML file the client opens
to see, per occupation, how far each state got, whether it's still current, what it would
cost to finish/refresh, and where the law came from — then pick occupations and get the
exact commands to run (including publishing to the site).

    python -m pipeline.client.dashboard      # writes results/status/dashboard.html

The status data (pipeline.client.status) is embedded inline, so the page is fully offline.
No file to download: the shown commands take the occupation name(s) directly
(`pipeline.client.run --professions X,Y`), which looks up which states need work itself,
live, when you run it — the same "run" flag this page uses to color/count cells. Cells
that need a fetch are shown but are never runnable via these commands.
"""
from __future__ import annotations

import json

from pipeline.client.status import build, OUT, COST_TRIM, COST_EXTRACT
from pipeline.ingest.trim_state import DEFAULT_MODEL as TRIM_MODEL
from pipeline.extract.extract_state_batch import DEFAULT_MODEL as EXTRACT_MODEL
from pipeline.paths import WEB_PUBLIC_DIR

HTML_OUT = OUT.parent / "dashboard.html"

# Client runs from the repo root with the project venv.
PY = "pipeline/.venv/bin/python"

_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Licensing pipeline — pick occupations to process</title>
<style>
  :root {
    --done:#2e7d32; --unstamped:#9ccc9e; --stale:#c62828; --ready:#1565c0;
    --noschema:#6a1b9a; --fetch:#ef6c00; --absent:#9e9e9e; --unknown:#d8d8d8;
    --ink:#1a1a1a; --muted:#666; --line:#e2e2e2; --bg:#fafafa; --card:#fff;
  }
  * { box-sizing: border-box; }
  body { font: 15px/1.5 -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
         color: var(--ink); background: var(--bg); margin: 0; padding: 0 0 300px; }
  header { padding: 24px 28px 8px; }
  h1 { font-size: 22px; margin: 0 0 4px; }
  .sub { color: var(--muted); margin: 0 0 12px; max-width: 900px; }
  details.explain { margin: 6px 0 12px; max-width: 900px; }
  details.explain summary { cursor: pointer; color: var(--ready); font-size: 14px; }
  details.explain table { margin: 10px 0 0; font-size: 13.5px; }
  details.explain td { padding: 3px 12px 3px 0; }
  .totals { display: flex; gap: 22px; flex-wrap: wrap; margin: 8px 0 4px; }
  .totals b { font-size: 20px; }
  .legend { display: flex; gap: 14px; flex-wrap: wrap; font-size: 13px; color: var(--muted);
            padding: 6px 28px 14px; }
  .swatch { display: inline-block; width: 11px; height: 11px; border-radius: 2px;
            margin-right: 5px; vertical-align: -1px; }
  .controls { padding: 0 28px 12px; display: flex; gap: 12px; align-items: center; }
  input[type=search] { padding: 7px 10px; border: 1px solid var(--line); border-radius: 6px;
                       width: 260px; font-size: 14px; }
  table.grid-tbl { border-collapse: collapse; width: calc(100% - 56px); margin: 0 28px;
          background: var(--card); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
  th, td { text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--line); }
  th { font-size: 12px; text-transform: uppercase; letter-spacing: .03em; color: var(--muted);
       background: #f6f6f6; }
  tr.occ { cursor: pointer; }
  tr.occ:hover { background: #f4f8ff; }
  td.name { font-weight: 600; }
  td.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
  .cost { font-variant-numeric: tabular-nums; }
  .bar { display: flex; height: 12px; width: 190px; border-radius: 3px; overflow: hidden;
         border: 1px solid var(--line); background: #fff; }
  .bar span { display: block; height: 100%; }
  .caret { color: var(--muted); width: 14px; display: inline-block; }
  tr.detail td { background: #fbfbfb; padding: 6px 12px 14px 40px; }
  .states { display: flex; flex-wrap: wrap; gap: 4px; }
  .st { font-size: 11px; padding: 2px 6px; border-radius: 3px; color: #fff;
        font-variant-numeric: tabular-nums; text-decoration: none; }
  a.st:hover { outline: 2px solid rgba(0,0,0,.25); }
  .st.dark { color: #1a1a1a; }
  .foot { position: fixed; bottom: 0; left: 0; right: 0; background: var(--card);
          border-top: 1px solid var(--line); padding: 14px 28px; box-shadow: 0 -2px 12px rgba(0,0,0,.06); }
  .footrow { display: flex; gap: 24px; align-items: baseline; flex-wrap: wrap; }
  .footrow b { font-size: 18px; }
  button { font: inherit; padding: 8px 14px; border-radius: 6px; border: 1px solid var(--ready);
           background: var(--ready); color: #fff; cursor: pointer; }
  button:disabled { opacity: .45; cursor: default; }
  pre { background: #1e1e1e; color: #eaeaea; padding: 12px 14px; border-radius: 6px; overflow-x: auto;
        font: 12.5px/1.6 ui-monospace, Menlo, Consolas, monospace; margin: 8px 0 0; }
  .cmdnote { font-size: 12.5px; color: var(--muted); margin: 6px 0 0; }
  .paid { color: var(--fetch); font-weight: 600; }
  .free { color: var(--done); font-weight: 600; }
</style></head>
<body>
<header>
  <h1>Licensing pipeline — pick occupations to process</h1>
  <p class="sub">Each occupation's law is fetched and stored in this repo. Tick the ones you
     want structured data for, then run the commands at the bottom. Only <b>trim</b> and
     <b>extract</b> cost money; <b>clean</b> and <b>publish</b> are free.</p>
  <details class="explain">
    <summary>What does each step do?</summary>
    <table>
      <tr><td><b>clean</b> (free)</td><td>tidies the fetched statute text (de-duplicates, normalizes)</td></tr>
      <tr><td><b>trim</b> (~$__TRIM__/state, __TRIM_MODEL__)</td><td>an AI keeps only the sections relevant to this occupation</td></tr>
      <tr><td><b>extract</b> (~$__EXTRACT__/state, __EXTRACT_MODEL__)</td><td>an AI turns that law into the structured data (the deliverable)</td></tr>
      <tr><td><b>publish</b> (free)</td><td>builds the web payload so the occupation shows on the site</td></tr>
    </table>
    <p class="cmdnote" style="margin-top:8px">Trim/extract prices are for the model in use
       today — they move if the model changes. `run.py` always prints the exact estimate
       (and the model) before spending anything.</p>
  </details>
  <div class="totals">
    <span><b id="t-prof"></b> occupations</span>
    <span><b id="t-ready"></b> states with data</span>
    <span><b id="t-located"></b> located, not built</span>
    <span><b id="t-nostatute"></b> no statute</span>
    <span><b id="t-unlooked"></b> not checked</span>
  </div>
</header>
<div class="legend">
  <span><i class="swatch" style="background:var(--done)"></i><b>Data ready</b> — statute fetched &amp; extracted</span>
  <span><i class="swatch" style="background:var(--fetch)"></i><b>Located</b> — we know the statute, haven't trimmed &amp; extracted it yet</span>
  <span><i class="swatch" style="background:var(--absent)"></i><b>No statute</b> — we looked; no state statute exists (local/admin/none)</span>
  <span><i class="swatch" style="background:var(--unknown)"></i><b>Not checked</b> — we haven't looked yet</span>
  <span class="muted">Stale cells (data present but the law or prompt changed) stay in <b>Data ready</b> — the per-occupation <b>Updated</b> date shows how current it is.</span>
</div>
<div class="controls">
  <input type="search" id="q" placeholder="filter occupations…" autocomplete="off">
  <label class="muted"><input type="checkbox" id="onlyactionable"> only occupations with work to do</label>
</div>
<table class="grid-tbl">
  <thead><tr>
    <th style="width:28px"></th><th style="width:24px"></th><th>Occupation</th>
    <th>Coverage</th><th class="num">Updated</th><th class="num">To&nbsp;run</th><th class="num">Cost</th>
  </tr></thead>
  <tbody id="rows"></tbody>
</table>

<div class="foot">
  <div class="footrow">
    <span><b id="sel-occ">0</b> occupations</span>
    <span><b id="sel-cells">0</b> states to build</span>
    <span>cost <b class="cost" id="sel-cost">$0.00</b> <span class="muted" id="sel-costnote"></span></span>
  </div>
  <pre id="cmds">Pick at least one occupation to see the commands.</pre>
  <p class="cmdnote">Run from the repo root, in order. <span class="free">clean</span>/<span class="free">publish</span>
     are free; <span class="paid">trim</span>/<span class="paid">extract</span> ask before spending and
     print the exact per-cell price for the model in use at the time. Every state with work to do
     for the named occupation(s) is picked up automatically — nothing to select by hand, no file
     to download. A stale state is re-run through the whole chain.</p>
</div>

<script>
const DATA = __DATA__;
const PY = "__PY__";
const selected = new Set();

function fmt(n){ return "$" + n.toFixed(2); }

// Four plain-language buckets (Atharv #74). A cell is either: we have the
// structured data (done — stale/unstamped included, recency shown by the date);
// we know where the statute is but haven't built it (needs-fetch / pulled /
// cleaned / trimmed / no-schema); we looked and there's no state statute
// (absent); or we haven't looked (unknown).
function cellCategory(c){
  if (c.stage === "done") return "ready";
  if (c.stage === "absent") return "nostatute";
  if (c.stage === "unknown") return "unlooked";
  return "located"; // needs-fetch, pulled/cleaned/trimmed, needs_schema
}
const CAT_COLOR = {
  ready: "var(--done)", located: "var(--fetch)",
  nostatute: "var(--absent)", unlooked: "var(--unknown)",
};
function cellColor(c){ return CAT_COLOR[cellCategory(c)]; }

// ---- header totals (summed into the 4 buckets) ----
const T = DATA.totals;
let bReady = 0, bLocated = 0, bNo = 0, bUnlooked = 0;
for (const p in DATA.professions){
  const s = DATA.professions[p].summary;
  bReady    += s.done_current + s.done_unstamped + s.done_stale;
  bLocated  += s.ready + s.needs_schema + s.needs_fetch;
  bNo       += s.absent;
  bUnlooked += s.unknown;
}
document.getElementById("t-prof").textContent = T.professions;
document.getElementById("t-ready").textContent = bReady;
document.getElementById("t-located").textContent = bLocated;
document.getElementById("t-nostatute").textContent = bNo;
document.getElementById("t-unlooked").textContent = bUnlooked;

// Most-recent build date across an occupation's cells — the "last overall
// update" Atharv asked for. Cells carry last_processed (ISO); take the max.
function occUpdated(p){
  let best = "";
  for (const c of Object.values(DATA.professions[p].states)){
    const d = (c.last_processed || "").slice(0, 10);
    if (d && d > best) best = d;
  }
  return best;
}

// ---- rows ----
const rowsEl = document.getElementById("rows");
const order = Object.keys(DATA.professions).sort((a,b) =>
  DATA.professions[b].summary.cost_runnable - DATA.professions[a].summary.cost_runnable
  || a.localeCompare(b));

function bar(sm){
  const seg = (n,c) => n ? `<span style="width:${100*n/50}%;background:${c}"></span>` : "";
  const ready = sm.done_current + sm.done_unstamped + sm.done_stale;
  const located = sm.ready + sm.needs_schema + sm.needs_fetch;
  return `<div class="bar">${seg(ready,"var(--done)")}${seg(located,"var(--fetch)")}`
       + `${seg(sm.absent,"var(--absent)")}${seg(sm.unknown,"var(--unknown)")}</div>`;
}

function actionable(p){ const s = DATA.professions[p].summary; return s.ready + s.done_stale; }

for (const p of order){
  const sm = DATA.professions[p].summary;
  const tr = document.createElement("tr");
  tr.className = "occ"; tr.dataset.prof = p;
  // selectable if there's anything to process OR anything already done to publish
  const enabled = (sm.ready + sm.done_stale + sm.done) > 0;
  tr.innerHTML =
    `<td><input type="checkbox" class="pick" ${enabled ? "" : "disabled"}></td>`
  + `<td class="caret">▸</td>`
  + `<td class="name">${p.replace(/_/g," ")}</td>`
  + `<td>${bar(sm)}</td>`
  + `<td class="num" style="color:var(--muted);font-size:13px">${occUpdated(p) || "—"}</td>`
  + `<td class="num">${actionable(p) || "—"}</td>`
  + `<td class="num cost">${sm.cost_runnable ? fmt(sm.cost_runnable) : (sm.done ? "done" : "—")}</td>`;
  rowsEl.appendChild(tr);

  const detail = document.createElement("tr");
  detail.className = "detail"; detail.style.display = "none"; detail.dataset.for = p;
  const chips = Object.entries(DATA.professions[p].states).map(([s,c]) => {
    const color = cellColor(c);
    const light = color === "var(--unknown)" || color === "var(--unstamped)";
    const tip = `${s} — ${c.needs_schema ? "no schema yet — can't extract" : (c.fresh || c.stage)}`
      + (c.last_processed ? ` · ${c.last_processed.slice(0,10)}` : "")
      + (c.cost ? ` · ${fmt(c.cost)}` : "")
      + (c.source_label ? ` · ${c.source_label}` : "");
    const cls = "st" + (light ? " dark" : "");
    const url = (c.source_urls && c.source_urls[0]) || "";
    return url
      ? `<a class="${cls}" href="${url}" target="_blank" rel="noopener" title="${tip}" style="background:${color}">${s}</a>`
      : `<span class="${cls}" title="${tip}" style="background:${color}">${s}</span>`;
  }).join("");
  detail.innerHTML = `<td colspan="7"><div class="states">${chips}</div></td>`;
  rowsEl.appendChild(detail);
}

// ---- interactions ----
rowsEl.addEventListener("click", e => {
  const tr = e.target.closest("tr.occ"); if(!tr) return;
  if (e.target.classList.contains("pick")){
    const p = tr.dataset.prof;
    e.target.checked ? selected.add(p) : selected.delete(p);
    recompute();
    return;
  }
  if (e.target.closest("a")) return; // let source links work
  const d = rowsEl.querySelector(`tr.detail[data-for="${tr.dataset.prof}"]`);
  const open = d.style.display !== "none";
  d.style.display = open ? "none" : "";
  tr.querySelector(".caret").textContent = open ? "▸" : "▾";
});

document.getElementById("q").addEventListener("input", applyFilter);
document.getElementById("onlyactionable").addEventListener("change", applyFilter);
function applyFilter(){
  const term = document.getElementById("q").value.toLowerCase();
  const only = document.getElementById("onlyactionable").checked;
  for (const tr of rowsEl.querySelectorAll("tr.occ")){
    const p = tr.dataset.prof;
    const show = p.replace(/_/g," ").includes(term) && (!only || actionable(p) > 0);
    tr.style.display = show ? "" : "none";
    const d = rowsEl.querySelector(`tr.detail[data-for="${p}"]`);
    if (!show){ d.style.display = "none"; tr.querySelector(".caret").textContent = "▸"; }
  }
}

// ---- selection -> commands ----
// No queue file: run.py looks up which states have work to do for a named
// occupation itself (same "run" flag this dashboard uses to color cells), live,
// at the moment you run it. Selecting occupations here is just for seeing the
// cost preview before you commit to a command — the command only ever needs
// the occupation name(s).
function runnableCells(p){
  return Object.entries(DATA.professions[p].states).filter(([,c]) => c.run);
}

function recompute(){
  let nCells = 0, cost = 0;
  for (const p of selected){
    for (const [,c] of runnableCells(p)){ nCells++; cost += c.cost; }
  }
  document.getElementById("sel-occ").textContent = selected.size;
  document.getElementById("sel-cells").textContent = nCells;
  document.getElementById("sel-cost").textContent = fmt(cost);
  document.getElementById("sel-costnote").textContent = nCells
    ? `(~${fmt(nCells*__TRIM__)} trim @ __TRIM_MODEL__ + ~${fmt(nCells*__EXTRACT__)} extract @ __EXTRACT_MODEL__ — `
      + `today's prices; changes if the model changes)`
    : "";
  document.getElementById("cmds").textContent = selected.size ? commands(nCells) : "Pick at least one occupation to see the commands.";
}

function commands(nCells){
  const profs = [...selected].join(",");
  const lines = [];
  if (nCells > 0){
    lines.push("# 1. clean  (FREE)",
      PY + " -m pipeline.client.run clean   --professions " + profs, "",
      "# 2. trim   (asks first, prints the exact price)",
      PY + " -m pipeline.client.run trim    --professions " + profs, "",
      "# 3. extract (asks first, prints the exact price)",
      PY + " -m pipeline.client.run extract --professions " + profs, "");
  } else {
    lines.push("# nothing to process for the selection — publish only", "");
  }
  lines.push("# " + (nCells>0 ? "4. " : "") + "publish (FREE — show on the site; add --deploy to push live)",
    PY + " -m pipeline.client.run publish --professions " + profs);
  return lines.join("\\n");
}

recompute();
</script>
</body></html>
"""


def main() -> None:
    data = build()
    html = (_PAGE
            .replace("__DATA__", json.dumps(data))
            .replace("__PY__", PY)
            .replace("__TRIM__", repr(COST_TRIM))
            .replace("__EXTRACT__", repr(COST_EXTRACT))
            .replace("__TRIM_MODEL__", TRIM_MODEL)
            .replace("__EXTRACT_MODEL__", EXTRACT_MODEL))
    HTML_OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML_OUT.write_text(html)
    # Mirror into the Next.js app's public dir (same pattern as the field dictionary)
    # so it deploys at /dashboard/index.html — a status snapshot, not a live view.
    web_dir = WEB_PUBLIC_DIR / "dashboard"
    web_dir.mkdir(parents=True, exist_ok=True)
    (web_dir / "index.html").write_text(html)
    print(f"wrote {HTML_OUT}")
    print(f"  open it in a browser: open {HTML_OUT}")
    print(f"  mirrored to {web_dir / 'index.html'} — redeploy pipeline/publish/web to publish")


if __name__ == "__main__":
    main()

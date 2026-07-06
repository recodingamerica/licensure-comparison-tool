"""Generate the client dashboard — a single self-contained HTML file the client opens
to see, per occupation, how far each state got, whether it's still current, what it would
cost to finish/refresh, and where the law came from — then pick occupations and get the
exact commands to run (including publishing to the site).

    python -m pipeline.client.dashboard      # writes results/status/dashboard.html

The status data (pipeline.client.status) is embedded inline, so the page is fully offline.
Picking occupations builds a downloadable my_queue.json (only the states that need work —
ready-to-process plus stale-and-needing-refresh) plus copy-paste commands. Cells that need
a fetch are shown but never enter the queue.
"""
from __future__ import annotations

import json

from pipeline.client.status import build, OUT, COST_TRIM, COST_EXTRACT

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
      <tr><td><b>trim</b> (~$0.05/state)</td><td>an AI keeps only the sections relevant to this occupation</td></tr>
      <tr><td><b>extract</b> (~$0.15/state)</td><td>an AI turns that law into the structured data (the deliverable)</td></tr>
      <tr><td><b>publish</b> (free)</td><td>builds the web payload so the occupation shows on the site</td></tr>
    </table>
  </details>
  <div class="totals">
    <span><b id="t-prof"></b> occupations</span>
    <span><b id="t-current"></b> states with current data</span>
    <span><b id="t-ready"></b> fetched, not yet built</span>
    <span><b id="t-noschema"></b> fetched but no schema</span>
    <span><b id="t-stale"></b> stale</span>
    <span><b id="t-unstamped"></b> unverified</span>
    <span><b id="t-fetch"></b> not fetched</span>
  </div>
</header>
<div class="legend">
  <span><i class="swatch" style="background:var(--done)"></i>data ready &amp; up to date</span>
  <span><i class="swatch" style="background:var(--unstamped)"></i>data built, freshness not tracked yet</span>
  <span><i class="swatch" style="background:var(--stale)"></i>stale — law/prompt changed, rebuild</span>
  <span><i class="swatch" style="background:var(--ready)"></i>law fetched — run trim+extract to build data</span>
  <span><i class="swatch" style="background:var(--noschema)"></i>law fetched, but no schema yet — can't extract</span>
  <span><i class="swatch" style="background:var(--fetch)"></i>law not fetched yet</span>
  <span><i class="swatch" style="background:var(--absent)"></i>no such law / not checked</span>
</div>
<div class="controls">
  <input type="search" id="q" placeholder="filter occupations…" autocomplete="off">
  <label class="muted"><input type="checkbox" id="onlyactionable"> only occupations with work to do</label>
</div>
<table class="grid-tbl">
  <thead><tr>
    <th style="width:28px"></th><th style="width:24px"></th><th>Occupation</th>
    <th>Coverage</th><th class="num">To&nbsp;run</th><th class="num">Cost</th>
  </tr></thead>
  <tbody id="rows"></tbody>
</table>

<div class="foot">
  <div class="footrow">
    <span><b id="sel-occ">0</b> occupations</span>
    <span><b id="sel-cells">0</b> states to build</span>
    <span>cost <b class="cost" id="sel-cost">$0.00</b></span>
    <button id="dl" disabled>Download my_queue.json</button>
    <span class="muted" id="dlnote">select occupations to build a queue</span>
  </div>
  <pre id="cmds">Pick at least one occupation to see the commands.</pre>
  <p class="cmdnote">Run from the repo root, in order. <span class="free">clean</span>/<span class="free">publish</span>
     are free; <span class="paid">trim</span>/<span class="paid">extract</span> ask before spending.
     A stale state is re-run through the whole chain.</p>
</div>

<script>
const DATA = __DATA__;
const PY = "__PY__";
const selected = new Set();

function fmt(n){ return "$" + n.toFixed(2); }

function cellColor(c){
  if (c.stage === "done"){
    if (c.fresh === "stale") return "var(--stale)";
    if (c.fresh === "unstamped") return "var(--unstamped)";
    return "var(--done)";
  }
  if (c.needs_schema) return "var(--noschema)"; // corpus on disk but no schema → can't extract
  if (c.stage === "needs-fetch") return "var(--fetch)";
  if (c.stage === "absent") return "var(--absent)";
  if (c.stage === "unknown") return "var(--unknown)";
  return "var(--ready)"; // pulled / cleaned / trimmed
}

// ---- header totals ----
const T = DATA.totals;
document.getElementById("t-prof").textContent = T.professions;
document.getElementById("t-current").textContent = T.cells_current;
document.getElementById("t-ready").textContent = T.cells_ready;
document.getElementById("t-noschema").textContent = T.cells_needs_schema;
document.getElementById("t-stale").textContent = T.cells_stale;
document.getElementById("t-unstamped").textContent = T.cells_unstamped;
document.getElementById("t-fetch").textContent = T.cells_needs_fetch;

// ---- rows ----
const rowsEl = document.getElementById("rows");
const order = Object.keys(DATA.professions).sort((a,b) =>
  DATA.professions[b].summary.cost_runnable - DATA.professions[a].summary.cost_runnable
  || a.localeCompare(b));

function bar(sm){
  const seg = (n,c) => n ? `<span style="width:${100*n/50}%;background:${c}"></span>` : "";
  return `<div class="bar">${seg(sm.done_current,"var(--done)")}${seg(sm.done_unstamped,"var(--unstamped)")}`
       + `${seg(sm.done_stale,"var(--stale)")}${seg(sm.ready,"var(--ready)")}${seg(sm.needs_schema,"var(--noschema)")}`
       + `${seg(sm.needs_fetch,"var(--fetch)")}${seg(sm.absent+sm.unknown,"var(--absent)")}</div>`;
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
  detail.innerHTML = `<td colspan="6"><div class="states">${chips}</div></td>`;
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

// ---- selection -> queue + commands ----
function queueObj(){
  const q = {};
  for (const p of selected){
    const runs = Object.entries(DATA.professions[p].states)
      .filter(([,c]) => c.run).map(([s]) => s);
    if (runs.length) q[p] = runs;
  }
  return q;
}

function recompute(){
  const q = queueObj();
  const nCells = Object.values(q).reduce((a,v) => a+v.length, 0);
  let cost = 0;
  for (const p in q) for (const s of q[p]) cost += DATA.professions[p].states[s].cost;
  document.getElementById("sel-occ").textContent = selected.size;
  document.getElementById("sel-cells").textContent = nCells;
  document.getElementById("sel-cost").textContent = fmt(cost);
  document.getElementById("dl").disabled = nCells === 0;
  document.getElementById("dlnote").textContent = nCells
    ? `≈ ${fmt(nCells*__TRIM__)} trim + ${fmt(nCells*__EXTRACT__)} extract`
    : (selected.size ? "nothing to process — publish only" : "select occupations to build a queue");
  document.getElementById("cmds").textContent = selected.size ? commands(nCells) : "Pick at least one occupation to see the commands.";
}

function commands(nCells){
  const profs = [...selected].join(",");
  const lines = [];
  if (nCells > 0){
    lines.push("# 1. clean  (FREE)",
      PY + " -m pipeline.client.run clean   --queue my_queue.json", "",
      "# 2. trim   (~$" + __TRIM__.toFixed(2) + "/state — asks first)",
      PY + " -m pipeline.client.run trim    --queue my_queue.json", "",
      "# 3. extract (~$" + __EXTRACT__.toFixed(2) + "/state — asks first)",
      PY + " -m pipeline.client.run extract --queue my_queue.json", "");
  } else {
    lines.push("# nothing to process for the selection — publish only", "");
  }
  lines.push("# " + (nCells>0 ? "4. " : "") + "publish (FREE — show on the site; add --deploy to push live)",
    PY + " -m pipeline.client.run publish --professions " + profs);
  return lines.join("\\n");
}

document.getElementById("dl").addEventListener("click", () => {
  const blob = new Blob([JSON.stringify(queueObj(), null, 2)], {type:"application/json"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = "my_queue.json"; a.click();
  URL.revokeObjectURL(a.href);
});

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
            .replace("__EXTRACT__", repr(COST_EXTRACT)))
    HTML_OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML_OUT.write_text(html)
    print(f"wrote {HTML_OUT}")
    print(f"  open it in a browser: open {HTML_OUT}")


if __name__ == "__main__":
    main()

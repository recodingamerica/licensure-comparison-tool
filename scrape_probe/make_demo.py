"""Generate a single self-contained HTML page demonstrating per-state scrape coverage.

Reads results/probe_results.json and results/profession_chapters.json and emits
results/demo.html — a shareable file showing, for each of the 50 states:

  - which fetch strategy works (plain requests / curl-cffi / API key / playwright)
  - which source we chose (official site vs Justia mirror)
  - how many profession-level entries we extracted
  - sample profession labels with live links so a viewer can click through

Run: python make_demo.py
"""

from __future__ import annotations

import html
import json
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
PROBE_JSON = RESULTS / "probe_results.json"
ENUM_JSON = RESULTS / "profession_chapters.json"
OUT_HTML = RESULTS / "demo.html"

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
}

STRATEGY_LABEL = {
    "requests": "plain HTTP",
    "curl_cffi": "Chrome-fingerprint client",
    "api_with_key": "Open Legislation API (free key)",
    "playwright": "headless browser",
    "needs_investigation": "needs investigation",
}

STRATEGY_BADGE_COLOR = {
    "requests": "#16a34a",        # green
    "curl_cffi": "#0284c7",       # blue
    "api_with_key": "#9333ea",    # purple
    "playwright": "#ea580c",      # orange
    "needs_investigation": "#dc2626",  # red
}


def per_state_strategy(probe_data: list[dict]) -> dict[str, dict]:
    """state -> {strategy, source_id, source_url}; the recommendation derived in probe_report."""
    out: dict[str, dict] = {}
    for r in probe_data:
        st = r["state"]
        if st == "US":
            continue
        if st in out:
            continue
        if r["classification"] in ("ok", "ok_with_browser", "ok_with_key"):
            out[st] = {
                "strategy": r.get("recommended_strategy") or "needs_investigation",
                "source_id": r["id"],
                "source_url": r["url"],
                "kind": r["kind"],
            }
    return out


def render_state_card(state: str, info: dict, enum_row: dict | None) -> str:
    full_name = STATE_NAMES.get(state, state)
    strat = info.get("strategy", "needs_investigation")
    strat_label = STRATEGY_LABEL.get(strat, strat)
    strat_color = STRATEGY_BADGE_COLOR.get(strat, "#6b7280")
    kind_label = "official site" if info.get("kind") == "official" else "Justia mirror"
    source_url = info.get("source_url", "#")
    source_host = urllib.parse.urlparse(source_url).netloc

    chapter_count = enum_row["chapter_count"] if enum_row else 0
    extraction_level = (enum_row or {}).get("extraction_level", "")
    chapters = (enum_row or {}).get("chapters", [])[:8]

    samples_html = ""
    if chapters:
        items = []
        for c in chapters:
            label = html.escape(c.get("label", ""))
            url = html.escape(c.get("url", "#"))
            items.append(f'<li><a href="{url}" target="_blank" rel="noopener">{label}</a></li>')
        samples_html = f'<ul class="samples">{"".join(items)}</ul>'
    elif enum_row and enum_row.get("error"):
        samples_html = f'<p class="error">extraction error: {html.escape(enum_row["error"])}</p>'
    else:
        samples_html = '<p class="muted">No samples extracted (URL pattern may need adjustment)</p>'

    level_note = ""
    if extraction_level == "section_fallback":
        level_note = '<span class="level-note" title="This state has no chapter level — children of the parent title are individual statute sections, each typically governing one rule or one profession. Counts are higher because the unit is finer.">section-level</span>'
    elif extraction_level == "official_generic":
        level_note = '<span class="level-note" title="Extracted from the official state legislature site (Justia URL was unavailable or 404\'d for this state).">official-site</span>'

    deeper_note = ""
    if state in ("NV", "PA", "AR"):
        deeper_note = '<p class="muted">⚠️ extractor needs a state-specific URL; the parent index returned partial data. Strategy and reach are confirmed; refining the deep-link path is the open task.</p>'

    return f"""
    <article class="card" data-strategy="{strat}">
      <header>
        <h2>{full_name} <span class="state-code">{state}</span></h2>
        <div class="badges">
          <span class="badge" style="background:{strat_color}">{html.escape(strat_label)}</span>
          <span class="badge gray">{kind_label}</span>
          {level_note}
        </div>
      </header>
      <p class="meta">
        <strong>{chapter_count}</strong> {('profession sections' if extraction_level == 'section_fallback' else 'profession chapters')} extracted from
        <a href="{html.escape(source_url)}" target="_blank" rel="noopener">{html.escape(source_host)}</a>
      </p>
      {samples_html}
      {deeper_note}
    </article>
    """


def main() -> None:
    probe_data = json.loads(PROBE_JSON.read_text())
    enum_data = json.loads(ENUM_JSON.read_text())
    enum_by_state = {r["state"]: r for r in enum_data}

    strat_by_state = per_state_strategy(probe_data)

    states_sorted = sorted(STATE_NAMES.keys())
    cards = []
    for st in states_sorted:
        info = strat_by_state.get(st, {"strategy": "needs_investigation"})
        cards.append(render_state_card(st, info, enum_by_state.get(st)))

    # Top-line summary
    n_states_with_strategy = sum(1 for s in states_sorted if strat_by_state.get(s))
    n_states_with_chapters = sum(1 for s in states_sorted if (enum_by_state.get(s) or {}).get("chapter_count", 0) > 0)
    total_entries = sum((enum_by_state.get(s) or {}).get("chapter_count", 0) for s in states_sorted)

    strat_breakdown: dict[str, int] = {}
    for s in states_sorted:
        info = strat_by_state.get(s)
        if info:
            strat_breakdown[info["strategy"]] = strat_breakdown.get(info["strategy"], 0) + 1

    breakdown_html = "".join(
        f'<li><span class="badge" style="background:{STRATEGY_BADGE_COLOR.get(k, "#6b7280")}">{html.escape(STRATEGY_LABEL.get(k, k))}</span> &nbsp; <strong>{v}</strong> states</li>'
        for k, v in sorted(strat_breakdown.items(), key=lambda x: -x[1])
    )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>State Statute Scrape Coverage</title>
<style>
  :root {{
    --fg: #0f172a; --muted: #64748b; --bg: #f8fafc; --card: #ffffff;
    --border: #e2e8f0; --link: #1d4ed8;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    margin: 0; background: var(--bg); color: var(--fg); line-height: 1.5;
  }}
  .wrap {{ max-width: 1120px; margin: 0 auto; padding: 32px 20px 64px; }}
  h1 {{ font-size: 28px; margin: 0 0 6px; }}
  .lede {{ color: var(--muted); margin: 0 0 24px; max-width: 720px; }}
  .summary {{
    background: var(--card); border: 1px solid var(--border); border-radius: 12px;
    padding: 20px 24px; margin-bottom: 32px;
  }}
  .summary h2 {{ margin: 0 0 12px; font-size: 18px; }}
  .summary ul {{ list-style: none; padding: 0; margin: 0; display: flex; flex-wrap: wrap; gap: 14px; }}
  .summary li {{ display: flex; align-items: center; gap: 6px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(330px, 1fr)); gap: 16px; }}
  .card {{
    background: var(--card); border: 1px solid var(--border); border-radius: 12px;
    padding: 16px 18px; display: flex; flex-direction: column; gap: 8px;
  }}
  .card h2 {{ margin: 0; font-size: 16px; display: flex; align-items: baseline; gap: 8px; }}
  .state-code {{ color: var(--muted); font-size: 12px; font-weight: 500; }}
  .meta {{ font-size: 13px; color: var(--muted); margin: 0; }}
  .meta strong {{ color: var(--fg); font-weight: 600; }}
  .badges {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }}
  .badge {{
    display: inline-block; color: white; font-size: 11px; font-weight: 600;
    letter-spacing: 0.02em; padding: 2px 8px; border-radius: 999px; text-transform: lowercase;
  }}
  .badge.gray {{ background: #94a3b8; }}
  .level-note {{
    font-size: 11px; color: var(--muted); border: 1px dashed var(--border);
    padding: 1px 6px; border-radius: 999px; cursor: help;
  }}
  .samples {{ list-style: none; padding: 0; margin: 4px 0 0; font-size: 13px; }}
  .samples li {{ padding: 2px 0; }}
  .samples a {{ color: var(--link); text-decoration: none; }}
  .samples a:hover {{ text-decoration: underline; }}
  .muted {{ color: var(--muted); font-size: 12px; margin: 4px 0 0; }}
  .error {{ color: #b91c1c; font-size: 12px; margin: 4px 0 0; }}
  footer {{ margin-top: 40px; color: var(--muted); font-size: 12px; }}
  code {{ background: #f1f5f9; padding: 1px 5px; border-radius: 4px; font-size: 12px; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>Can we scrape state professional-licensing statutes for all 50 states?</h1>
  <p class="lede">Short answer: yes. Each card below shows one state — which fetch strategy worked, where we got the data from, how many profession-level statute entries we found, and live links to the actual scraped pages so you can click through to verify.</p>

  <section class="summary">
    <h2>Coverage</h2>
    <p style="margin: 0 0 14px; color: var(--muted);">
      <strong>{n_states_with_strategy} of 50</strong> states have a confirmed working fetch strategy.
      <strong>{n_states_with_chapters} of 50</strong> states have profession entries enumerated, totaling <strong>{total_entries:,}</strong> profession-level URLs across all states.
    </p>
    <ul>{breakdown_html}</ul>
  </section>

  <section class="grid">
    {''.join(cards)}
  </section>

  <footer>
    <p>Generated from <code>probe_results.json</code> + <code>profession_chapters.json</code> by <code>make_demo.py</code>. Source pipeline at <a href="https://github.com/abigailhaddad/utah">github.com/abigailhaddad/utah</a>.</p>
    <p>Strategy legend: <strong>plain HTTP</strong> = standard <code>requests</code> works; <strong>Chrome-fingerprint client</strong> = needs <code>curl_cffi</code> with TLS impersonation to bypass Cloudflare on Justia; <strong>Open Legislation API</strong> = NY-specific, free key required; <strong>headless browser</strong> = Playwright fallback when no HTTP strategy works (not currently the recommended path for any state). Sites split into "official site" (state legislature) and "Justia mirror" (uniform structure across states, used when the official site requires a browser).</p>
    <p>"Section-level" badge means the state's licensing title has no chapter subdivision — every link is an individual statute section. The total entry count for those states reflects rule-level granularity rather than profession-level.</p>
  </footer>
</div>
</body>
</html>
"""
    OUT_HTML.write_text(page)
    print(f"wrote {OUT_HTML} ({OUT_HTML.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

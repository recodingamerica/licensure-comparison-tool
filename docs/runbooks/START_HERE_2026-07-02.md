# START HERE — next session (handoff 2026-07-02)

Tree is clean, 513 tests green, everything committed. This is a safe cold-start.

## What got done this session (context, not TODO)

- **Caps eliminated.** 30-corpus uncapped re-pull: umbrella section-cap removed,
  fetch depth 2→6 (`depth_capped` marker), throttle unified to 3s+jitter in
  `config/limits.yaml`. No cap/guard/depth truncation remains on disk.
- **MD/NV flipped to Justia** (source-gated dispatch) + verified full text.
- **9 empty corpora filled** from Justia (WA×5, CT×3, MD×1).
- **`refresh_corpus` built** — the durable annual re-pull tool (per-chapter
  completeness, auto-update resilience, year-over-year recodification diff).
  It SUPERSEDES `.scratch/overnight_repull.py` and the `_cdp_*` batch drivers.
- Tab-leak fixed (self-heal + SIGTERM). Audits + runbooks committed.

## THE ACTIVE GOAL: everything except PA on Justia

Precise worklist in `completeness_backlog_2026-07-02.md` §Priority-5. It's **24
genuinely-official URLs** to convert (NOT auto — hand-derive + leaf-verify each,
per `feedback_automated_mapping_fragile`):

| State | count | difficulty | notes |
|---|---|---|---|
| **MN** | 9 | tractable — DO FIRST | `revisor.mn.gov/cite/147` → Justia `chapter-147` (chapter-based; ch.148 is shared) |
| **MI** | 7-8 | hard | MCL section objects, no 1:1 Justia map — verify leaf text like MD |
| UT | 4 | small | `le.utah.gov` |
| AZ | 2 | small | `azleg.gov` |
| FL / MO | 1 each | small | |

Per-state recipe (one state at a time, ONE scraper):
1. Comment the `source:` flag / clear the official `section_url_list` in
   `state_structure.yaml`.
2. Re-map the official URLs to their Justia equivalents (state_structure or
   mapping_overrides.yaml).
3. `match_profession --profession X` (or all); confirm the index nodes are now
   `law.justia.com`.
4. **Leaf-verify** (the MD check): fetch one section via CDP, confirm >200 chars
   of real statute text — Justia must actually HAVE the law before flipping.
5. `refresh_corpus --profession X --states ST` — **NOT `--force`** (the
   per-chapter completeness gate + overwrite-guard protect existing data if
   Justia comes up thin).
6. Also normalize the ~86 relative `/codes/...` index URLs to absolute
   `https://law.justia.com` (cosmetic, uniform).

**PA stays official** — the one documented exception (not on Justia).

## Other completeness axes (same backlog doc, lower priority)

- **P2 — 63 thin corpora** (≤2 sections): `audit_corpus` triage (wrong-chapter vs
  correct-short) before re-pull. Includes the 2 new thin CT fills from today
  (athlete_agent CT=2, public_adjuster CT=4).
- **P3 — umbrella backlog** (CO-heavy: 12-240/12-5/12-29/12-43/24-1/22-219/12-280,
  + MS/RI/ND/TN/AR/WY): `umbrella_from_citations` → `pull_umbrella_text`.
- **P4 — section-nested professions**: `expand_containers` → `match_sections`.

## Queued config hygiene (from the audits, no Chrome needed)

- `config/models.yaml` — 16 hardcoded model IDs → one file (`hardcoded_config_audit`).
- `limits.yaml` threshold sweep — P3/P4 from `silent_caps_audit` (similarity /
  corpus-health cutoffs) + unify the 3 runaway-guard values.
- **Delete** `.scratch/overnight_repull.py` + `_cdp_*` batch drivers (superseded
  by refresh_corpus) — deferred diet items.
- Fix: `refresh_corpus` status JSON doesn't record per-item detail (cosmetic; the
  commits + diff report are the real record).

## Before ANY harvest — read first

`docs/runbooks/cdp_repull_lessons_2026-07-02.md`. Non-negotiables: ONE scraper
(flock); start a debug Chrome, clear the challenge once (`127.0.0.1:9222`);
`refresh_corpus` is the tool now; don't run two committing processes at once
(git index.lock); faulthandler traceback (`kill -ABRT`) is the definitive
wedge-check.

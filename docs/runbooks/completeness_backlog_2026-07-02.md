# Justia completeness backlog — 2026-07-02

What we still need to pull / map from Justia, by axis. The cap/truncation axis is
DONE (30-corpus re-pull; no cap fingerprints, guard-hits, or depth-capped signals
remain). This is the broader "has a corpus ≠ has the law" frontier. Measured, not
guessed — regenerate the numbers with the scans noted per section.

Tooling: re-pulls now go through `pipeline.ingest.refresh_corpus` (per-chapter
completeness, resilience, year-over-year diff). One scraper at a time; read
`cdp_repull_lessons_2026-07-02.md` first.

## Priority 1 — 9 EMPTY corpora (outright missing law, already Justia-routed)

These have 0 sections but a mapped Justia chapter. Their index URLs are ALREADY
`law.justia.com` (the chapter_url_template retirement moved them), and
`is_wa_url`/`is_ct_url` only match the official host — so they already route
through the Justia CDP path. The empties are STALE FAILURES from before the
new_page + depth fixes. Just re-pull with current code:

```
refresh_corpus --profession anesthesiologist_assistant --states WA
refresh_corpus --profession naturopathic_medicine --states WA
refresh_corpus --profession physician_assistant --states WA
refresh_corpus --profession respiratory_care --states WA
refresh_corpus --profession speech_language_audiology --states WA
refresh_corpus --profession athlete_agent --states CT
refresh_corpus --profession insurance_producer --states CT
refresh_corpus --profession public_adjuster --states CT
refresh_corpus --profession professional_geology --states MD
```
(scan: corpora with 0 sections — see the AXIS-2 scan below.)

## Priority 2 — 63 THIN corpora (≤2 sections; wrong-chapter vs correct-short)

Likely a mix of wrong-chapter pulls (re-map + re-pull) and genuinely-short
statutes (correct). Triage with `audit_corpus --profession X` before pulling —
don't blindly re-pull, the mapping may be wrong.
Scan: `for f in results/text/*/*.json: len(sections) <= 2`.

## Priority 3 — Umbrella backlog (cited-but-unpulled shared chapters)

General-provisions chapters ≥3 professions CITE but nobody pulled. Colorado-heavy.
Detect: `corpus_status umbrella --min-profs 3`. Known (2026-07-02):
- **CO**: 12-240, 12-5, 12-29, 12-43, 24-1, 22-219, 12-280 (7 chapters!)
- **MS** 41-3 · **RI** 1-1, 1-8 · **ND** 1-16 · **TN** 63-32, 2-4 · **AR** 5-64 · **WY** 7-19
Loop: `umbrella_from_citations --write` → `pull_umbrella_text --label-filter` →
re-extract the affected professions. Adds discipline/fees/hearings context.

## Priority 4 — Section-nested professions (low coverage, invisible to matcher)

Professions that live as a SECTION inside a broad chapter — the chapter-label
matcher can't see them. Candidates (low state counts, likely nested not absent):
public_adjuster (11), wholesale_drug_distributor (3), building_inspector (3),
money_transmitter (13), loan_broker (5), athlete_agent, court_reporter (13).
Loop: `expand_containers --state X` → `match_sections --write-targets` →
`refresh_corpus`. (LLM-free; writes to mapping_overrides.yaml.)

## Priority 5 — "Everything except PA to Justia" flip (user directive 2026-07-02)

Precise worklist. Of 110 residual non-`law.justia.com` index URLs: 44 are PA
(STAY — not on Justia); ~86 are relative Justia paths (`/codes/...` missing the
host — cosmetic, normalize by prepending `https://law.justia.com`); **~24 are
genuinely official** and need a hand-derived + leaf-verified Justia equivalent
(NOT auto-convertible — see feedback_automated_mapping_fragile):

- **MN — 9 — DONE 2026-07-02.** Justia MN is RANGE-GROUPED not year-versioned:
  `law.justia.com/codes/minnesota/chapters-{LO}-{HI}/chapter-{N}/`. 147/147A/148/
  150A/153 in `144-159`; 326A in `324-342`. Ch 148 shared by chiro/nursing/
  optometry/dietetics — kept explicit section_url_lists (converted from revisor
  cites, intersected with Justia's live 148 sections; repealed auto-dropped). All
  9 re-pulled + committed.
- **UT / AZ / FL / MO — DONE 2026-07-02.** UT `title-58/chapter-55` (parts;
  source: utah_le retired), AZ `title-32` + `section_slug_pattern ^section-32-11..`
  (contractors §§32-1101..1188), FL `chapter-489/part-i`, MO `chapter-341` (no-year).
  AZ/FL/MO were already source:justia — only the pinned trade URLs changed.
- **MI — 7 — STILL OPEN. The hard one.** (`legislature.mi.gov/.../mcl-368-1978-15-
  <part>`) MCL Part-objects don't map 1:1 to Justia's structure; leaf-verify like MD.
  May not be cleanly flippable — MI = Compiled Laws Chapter 333, parts are section
  ranges (333.166xx etc.). Dentistry 166 / Medicine 170 / Nursing 172 / Optometry
  174 / Podiatry 180 / Dietetics 183A + Accountancy (Occupational Code Art 7).

Mechanism (per state, one at a time): comment the `source:` flag (or clear the
official `section_url_list`), re-map the official URLs to Justia in state_structure
/ mapping_overrides, re-run `match_profession`, **leaf-verify with
`python -m pipeline.eval.verify_urls --url <justia-url>` (must return LIVE)**, then
`refresh_corpus --profession X --states ST`. The per-chapter completeness gate +
overwrite-guard protect existing data if Justia comes up thin — do NOT `--force`.

Also: the ~42 relative-`/codes/` URLs should be normalized to absolute Justia
(prepend the host) — BUT verify first whether a relative URL actually FAILS a
re-pull (no host) rather than assuming it's only cosmetic.

**Downstream still owed (LLM):** clean→trim→extract→republish the flipped corpora
(MN 7 published profs; UT/AZ/FL/MO trades). Not user-visible until done.

**PA stays official** — genuinely not on Justia (the one documented exception).

**Leaf-verify is now a tool:** `pipeline/eval/verify_urls.py` (LLM-free,
LIVE/STUB/DEAD_404/CHALLENGE). HTTP 200 is meaningless on Justia — a wrong URL form
returns 200 + a not-found shell. Gate every new/changed Justia mapping through it.

## Housekeeping — vestigial source flags

WA, VA, CT, SD, ME, ID, RI, VT, MT, UT now carry ~all-Justia index URLs (template
retirement). Their `source:` flags are mostly dead (the Justia URLs don't match
`is_X_url`). Clean up when convenient — BUT check each isn't load-bearing for the
umbrella mechanism (WA 18.130) or a residual official URL (UT 4, CT 2, SD 4, ID 1)
before removing.

## NOT a gap (don't chase)

66 professions show <45/50 states, but many are CORRECT absences — insurance_navigator
and private_probation genuinely exist in ~1 state. Reconcile against
`verified_absences.yaml` to separate "correct blank" from "unmapped" before treating
low coverage as missing work.

## Scans to regenerate these numbers

- Coverage: `results/profession_index/_coverage.csv`
- Empty/thin: iterate `results/text/*/*.json`, count `sections`
- Umbrella: `corpus_status umbrella --min-profs 3`
- Official-URL residue per state: count index nodes whose url isn't `law.justia.com`
- Cap/depth: grep corpora for `section_cap_hit` / `depth_capped` (currently zero)

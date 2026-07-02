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

## Priority 5 — MN / MI genuine Justia flip (optional; data exists)

MN (9 official URLs, revisor_mn) and MI (8, mi_legis) still fetch from official
hosts via hand-curated `section_url_list`. Data EXISTS and is fine — flipping to
Justia is for uniformity/durability, not to fill a gap. Lower priority; needs a
per-section Justia mapping (their section_url_list points at official hosts).
**PA stays official** — genuinely not on Justia.

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

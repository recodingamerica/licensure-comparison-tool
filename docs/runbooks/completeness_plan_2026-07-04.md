# Completeness plan — "every occupation, every state, incl. umbrella" (2026-07-04)

**Goal.** Move from *"49% of cells filled, now sourced from Justia"* to a state we can
actually claim: **every (occupation, state) cell is either filled with the real law or
flagged as a verified correct-absence, plus every shared umbrella chapter pulled.**

The Justia flip (this week) delivered *source consistency*, not *coverage*. Coverage is
a separate axis. Measured baseline (2026-07-04):

- 82 professions × 50 states = **4,100 cells; 2,014 filled (>2 sections) = 49%**.
- `verified_absences.yaml` = **3 entries** → we cannot currently distinguish correct
  blanks from real gaps. This is the crux.
- Umbrella backlog = **20 chapters** cited by ≥3 professions, unpulled.
- ~8 professions at **0 states**; 44 at **<25/50**.

The gap decomposes into three workstreams, each with existing (mostly LLM-free) tooling.
Do them in order — A is bounded and high-confidence, C is what unlocks the *claim*.

---

## Workstream A — Umbrella completeness  (bounded, do first)

**What:** 20 general-provisions chapters that many professions CITE but nobody pulled, so
extraction silently misses discipline/fees/hearings law. Detected today by
`corpus_status umbrella --min-profs 3`:

- **IN**: 1-14, 1-15, 1-16, 1-18, 2-1  (5 — new, not previously flagged)
- **CO**: 12-240, 12-5, 12-29, 12-43, 24-1, 22-219, 12-280  (7)
- **MS** 41-3 · **RI** 1-1, 1-8 · **ND** 1-16 · **TN** 63-32, 2-4 · **AR** 5-64 · **WY** 7-19

**How (existing loop):**
1. `umbrella_from_citations --write` — two-factor gate (cited by ≥N AND umbrella-style
   label) → writes Justia URLs. DON'T trust the citation signal alone (it also flags
   profession chapters).
2. `pull_umbrella_text --label-filter --force` → `umbrella_text/`.
3. `extract_state` folds umbrella text in as context for every profession in the state.

**Effort:** one small CDP harvest (~20 chapters) + re-extract the affected professions.
**Confidence:** high — bounded list, known mechanism (WA 18.130 / MI Part 161 already work).

## Workstream B — Zero/thin-coverage professions  (triage, then section-nested)

**What:** professions at 0 or very low coverage. First triage each into:
- **section-nested** — lives as a section inside a broad chapter, invisible to the
  chapter-label matcher (e.g. dental_hygienist inside the dentistry chapter,
  public_adjuster inside the Insurance title). ← most of the 0s are probably this.
- **genuinely-new** — needs a fresh profession definition + patterns.
- **correct-absence** — the occupation is rare/unlicensed (belongs in Workstream C).

**How (existing loop, LLM-free):**
1. `expand_containers --state X` — depth-expands broad chapters into their section-title
   tree (CDP; one process; checkpoints every 5).
2. `match_sections --source hierarchy --profession X --write-targets` — pattern-matches
   SECTION titles, writes the parent container as a pull target into
   `profession_index/X.json`.
3. `pull_text` → clean → trim → extract.

**Start with the quick wins:** dental_hygienist, dental_assistant (nested in dentistry),
public_adjuster, money_transmitter, wholesale_drug_distributor, building_inspector,
loan_broker, court_reporter (the P4 section-nested candidates).
**Effort:** per-profession investigation + CDP pulls; iterative.

## Workstream C — Coverage reconciliation  (unlocks the completeness CLAIM)

**What:** of the ~2,000 empty cells, decide each = **correct-absence** (occupation not
licensed in that state) vs **real gap** (we missed it). Today `verified_absences.yaml`
has 3 entries, so we can't claim anything. This is the fuzziest but highest-leverage
piece: once every empty cell is classified, "complete" becomes a defensible statement.

**How:**
1. Seed licensure-by-state from external reference data used as a POINTER, not a source
   (NCSL / IJ / CareerOneStop) — which states license which occupations. Per
   `feedback_external_data_as_pointer_not_source`: never ingest their values, only use
   them to target where to look.
2. For each empty cell, LLM-classify (or reference-confirm) correct-absence vs gap; write
   confirmed correct-absences into `verified_absences.yaml` with a reason.
3. What's left after A+B+C reconciliation = the TRUE remaining gap — a short, real list.

**Effort:** the largest; reference-data plumbing + a classification pass. But it's what
turns "49% filled" into "100% accounted-for."

---

## Sequencing & the honest end-state

1. **A (umbrella)** — days; bounded; do now.
2. **B (section-nested quick wins)** — the 0-coverage professions that are really nested.
3. **C (reconciliation)** — the long pole; makes the claim true.
4. **Downstream throughout:** clean→trim→extract→republish (LLM cost) — nothing is
   user-visible until this runs per affected profession/state.

**What we can honestly say at each milestone:**
- After A: "all shared umbrella law pulled for the cited states."
- After B: "every occupation we track has its own + nested chapters where they exist."
- After C: "every (occupation, state) cell is filled or a verified correct-absence" —
  i.e. the real "all occs, all states, incl. umbrella" claim.

Relates to `project_what_to_pull_jul1`, `feedback_no_overpromising`,
`feedback_reliable_detection_ok`, `reference_corpus_drift`.

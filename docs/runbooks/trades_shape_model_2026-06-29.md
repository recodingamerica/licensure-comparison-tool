# Trades regulatory-shape model + corpus-quality findings (2026-06-29, survives /clear)

Working session on GH #53 (trades gaps) turned up two findings bigger than the issue:
a **data-model mismatch** for trades, and a **corpus-correctness** problem. This captures
both, the validated design, and the systemic fix they imply, so none of it is lost.

---

## TL;DR

1. **Trades don't fit the one-act-per-profession model** the pipeline was built for. Regulation
   of a trade is often *several parallel regimes at once* (entity registration + individual
   competency cert; LLP under $25k + contractor above; sheet-metal + refrigeration + gas).
2. **Fix: model shape as a LIST OF REGIMES**, not a flat record. Validated against the hardest
   cases — every prior "strain" dissolved into "just more regimes." Licensed professions are a
   length-1 list, so they're unchanged.
3. **The trades corpus we already have is substantially WRONG-CHAPTER.** Keyword discovery pulled
   an abandoned-refrigerator criminal law for WA HVAC, procurement rules for ND architects, a
   repealed shell for NH plumbing. So "26 hvac states / 41 architecture states covered" overstates
   real coverage.
4. **The shape+coverage extraction self-audits corpus correctness** — the same pass that lists
   regimes also says "this is the wrong law." Wire it into discovery as a **post-pull gate**.

---

## 1. Why trades break the model

The pipeline assumes: one profession ↔ one state licensing act ↔ extract comparable fields
(CE hours, degree, scope), with every state answering the same questions. That holds for
dentistry/optometry/nursing. Trades violate all of it:

- **Locus varies**: state board *or* general-contractor board *or* component/fuel boards *or*
  municipality *or* nothing.
- **Often conditional**: gated by project dollar value (TN $25k, MS $10k/$50k, ND $4k) or
  residential/commercial or system capacity (MA refrigeration "over 10 tons").
- **Subject varies**: some states license the *individual* (competency), some the *entity*
  (registration), some both — a registration hit is not a practice license.
- **Frequently absent at the state level**: regulated locally (a real null), or unregulated.

Symptoms we hit: "gaps" that aren't gaps (false negatives), "fills" that are really admin-rule
classifications, and a true-null we couldn't represent because every value in our model needs a
statute quote and an absence has none. Those are all the same root cause: **shape is a real
dimension that was constant (and so invisible) for the professions we started with, and trades
make it vary.**

---

## 2. The model change: shape = list of regimes

```
(state, trade) -> regimes: list[Regime]            # length 1 for licensed professions; 1–4 for trades
                  headline: str                      # one-line human summary
                  coverage_note: str                 # is the corpus complete / the right law?

Regime = {
  bar:      competency_license | registration | local_only | unregulated
  vehicle:  dedicated_act | combined_professions_chapter | general_contractor_board
            | component_board | fuel_board | municipal | none
  subject:  individual | entity
  scope:    "full" | "gas" | "refrigeration" | "sheet_metal" | "residential" | "commercial" | ...
  mandatory: bool                                    # false = optional/voluntary state overlay
  gating:   { trigger: unconditional | dollar_threshold | capacity | project_type | other,
              direction: below | at_or_above | null,  # threshold directionality (TN/MS need this)
              value: number | null, unit: "usd" | "tons" | null }
  where:    statutory citation (from the corpus)
  note:     free text for residual nuance (preemption, mis-citation, trade-boundary)
}
```

Why this is the right cut:
- **It generalizes** — every profession has a shape; licensed ones are uniformly
  `[{competency_license, individual, dedicated_act, full, unconditional}]`, i.e. a length-1 list,
  so their output doesn't change. Trades just have longer lists.
- **It dissolves the null** — "local-only" / "unregulated" is a legitimate *regime value*, not a
  faked `regulatory_model` field with no quote. The finding is about structure, not a missing
  field, so it doesn't need a statute quote the way a field value does.
- **Fields become conditional** — CE-hours/degree/scope only apply to `competency_license`
  regimes, and only those states get compared on them. Trades are compared on *shape* first.

---

## 3. Validation

Stress-tested the flat 4-axis schema first: **every** hard case strained, all for the same
reason — multiple parallel regimes. Re-ran with list-of-regimes; strains vanished:

| case | regimes | result |
|---|---|---|
| TN/plumber | 2 | LLP <$25k + contractor ≥$25k — clean (needs threshold *direction*) |
| WA/hvac (from doc) | 2 | entity registration + individual cert — clean |
| MA/hvac | 3 | sheet-metal + refrigeration + gas components — clean |
| MO/electrician | 2 | optional state registration `[OPTIONAL]` + local individual — clean |
| RI/hvac | 4 | 3 individual masters + entity contractor reg — clean |
| **CA/optometry** | **1** | dedicated act, individual — **licensed professions unchanged** |

Residual refinements (all small, folded into the schema above): threshold *direction*
(below vs at/above), *capacity* gating (tons), and a per-regime `note` for preemption /
mis-citation / trade-boundary nuance. No structural failures remained.

---

## 4. The corpus-quality discovery (the bigger problem)

Then we ran the shape+coverage extraction on the **raw corpus** (not the doc) for states we
"have." 1 of 5 was the correct law:

| case | what we actually pulled | verdict |
|---|---|---|
| CA/architecture | real Architects Practice Act (BPC Ch.3) | ✅ 3 clean regimes |
| WA/hvac | RCW 9.03 — child-safety criminal law re: abandoned refrigerators | ❌ wrong chapter |
| ND/architecture | Ch. 54-44.7 — state-agency *procurement* procedures | ❌ wrong chapter |
| NH/plumbing | RSA 330 — **entirely repealed** shell | ❌ wrong chapter |
| AL/architecture | empty file (0 chars) | ❌ missing |

That 5-case sample was alarming — but it was **biased**: hand-picked from the doc's known-hard /
gap states plus an empty file. The full architecture audit corrects it:

**Architecture corpus audit, all 41 states: 38 correct (93%), 3 bad.**
- ✅ 38 `correct_licensure_text` — extracted clean regime lists (1–7 regimes each).
- ❌ 2 `wrong_chapter` — **ND** (Ch. 54-44.7 procurement), **OR** (Ch. 447 Plumbing/Architectural
  Barriers instead of the Architects act).
- ❌ 1 `empty_or_repealed` — **AL** (empty corpus file).

So the honest version: **the corpus-correctness problem is real but modest — at least for
architecture (~7% wrong), not "substantially wrong."** Don't over-rotate on the biased prototype.
The wrong-chapter risk is concentrated in the genuinely-hard trades (HVAC/electrician/plumber,
where keyword titles collide with criminal/procurement/contractor statutes) — audit those next to
size it, rather than assuming.

Crucially, the `coverage_note`/`corpus_verdict` made the extraction **self-auditing**: across 41
states it flagged exactly the 3 bad ones and nothing spurious. The same pass that produces regimes
detects wrong-chapter corpus — cheap (~$1.50 for 41 states) and reliable.

Precision caveat: a few combined-professions chapters over-counted regimes (WI=7, OK=5, NC/NV=4) —
the LLM listed engineer/surveyor/designer credentials from the same chapter, not just architecture.
The extraction must scope regimes to the *target* occupation. Minor, fixable in the prompt.

---

## 5. The systemic fix this implies

**Wire the coverage-audit into discovery as a post-pull gate.** After pulling a (profession,
state) chapter, run the shape+coverage check: "is this the correct licensure law for this
occupation?" If `wrong_chapter`/`empty_or_repealed`, don't silently accept it as coverage —
route it (re-discover the right chapter, widen the title net per the #53 doc, or flag for a
fetch). This is the durable version of the false-negative fix: discovery stops *believing its
own bad pulls*. It composes with `cross_ref_siblings` (already built) and the
corpus-completeness gate.

---

## 6. Open scope (decide before committing to a build)

- **Frontend/comparison ripple** — comparing trades = comparing regime *lists* by shape, which
  the current field-by-field comparison/choropleth engine doesn't do. This is where the model
  change costs the most.
- **Discovery comprehensiveness** — you can only enumerate regimes you pulled. Listing *all* of a
  state's regimes needs the "widen the net" search (Labor / Public Health & Safety / Fire /
  omnibus Occupational Codes), which is the same project as honestly asserting a null.
- **Where shape lives** — a new shape-first extraction pass for trades, leaving licensed
  professions on the existing path (length-1 lists), vs unifying everything.

## 7. Status after the full audit (all 4 trades)

Ran the corpus-correctness audit across all four trades. **The corpus is ~95% correct — the
mapping works; the panic was overblown.**

| trade | correct | bad |
|---|---|---|
| architecture | 38/41 (93%) | ND, OR, AL |
| hvac | 25/26 (96%) | WA (abandoned-fridge criminal law) |
| electrician | 36/38 (94%) | KY (repealed), OR (fire-safety statute) |
| plumbing | 40/41 (97%) | NH (repealed) |

The auditor is **consistent** (same verdict run-to-run), **differentiates within a state**
(WA/hvac BAD but WA/electrician + WA/plumbing OK), and **accepts contractor chapters** (AZ
electrician/plumbing OK). The ~7 bad are all the predicted criminal/safety/procurement/repealed
collisions — patternable, fixable. Free fix available: WA/hvac's correct law is RCW 19.28, the
same chapter already pulled for WA/electrician → `cross_ref_siblings` fixes it with no fetch.

Built this session: `discover/cross_ref_siblings.py` (sibling reuse), `discover/audit_corpus.py`
(the gate, `--gate` exits 1 on any wrong-chapter), and per-state `corpus_from` reuse in
`ingest/clean_text.py`. `refresh_all` now auto-re-stamps #52c direction.

## 8. Next steps (resume order)

**Tier 1 — cheap, durable (small):**
1. Run `audit_corpus` across ALL professions → full corpus-health map (~$3–4).
2. Wire the gate into the harvest/grind so future pulls self-check (no silent wrong-chapter coverage).
3. `cross_ref_siblings --apply` the free bad/gap states (WA/hvac ← electrician, the 8 confirmed sibling fills).

**Tier 2 — the real trades deliverable (large, deliberate):**
4. Fix regime-extraction PRECISION first — it over-counts in combined chapters (WA=6, WI=7); scope
   regimes to the target occupation. Prerequisite for trusting shape output.
5. Scope the FRONTEND/comparison ripple (comparing regime-lists, not fields) — design before building.
6. Build the shape-first extraction for trades; leave licensed professions on the field path (length-1).

**Tier 3 — needs decisions/fetches:**
7. #19 scope-specificity: resolve LLM-cluster-vs-hand-author with Atharv.
8. The ~7 bad re-pulls + true gap states needing a fetch → one dedicated CDP-Chrome session.

NOTE — caution against over-rotating: the corpus is mostly fine and the field model already
produces usable trade data, so backfilling trades with the *current* model is low-value. The
shape model is a representation/comparison improvement, not a rescue. Don't treat it as urgent.

Related: GH #53; `docs/reports/trades_gaps_issue53_2026-06-26.md` (Atharv's findings);
`pipeline/discover/{cross_ref_siblings,audit_corpus}.py`.

# Re-extract wave — readiness plan (as of 2026-07-31 EOD)

> **OUTCOME (2026-07-31 evening): the full wave was deliberately NOT run.**
> 136 cells re-extracted for $21.6 of a projected ~$120; the rest left recipe-stale
> on purpose. Preflight blocker resolved. Read "What actually happened" at the
> bottom before acting on anything above it — several numbers in this plan are wrong.

Written as a handoff. Everything below is committed; the working tree is clean and
944 tests pass. Start here, not in the old conversation.

---

## The one blocker

**`pipeline.extract.preflight` FAILS.** Do not spend the wave's budget until it passes.

```bash
# rebuild the queue (cells whose extract isn't current) and gate it
pipeline/.venv/bin/python - <<'EOF' > /tmp/wave.json
import json
from pipeline import provenance
from pipeline.paths import published_professions, STRUCTURED_DIR
q = {}
for p in published_professions():
    sts = [f.stem for f in sorted((STRUCTURED_DIR/p).glob("*.json"))
           if not f.name.startswith("_") and provenance.check("extract", p, f.stem) != "current"]
    if sts: q[p] = sts
print(json.dumps(q))
EOF
pipeline/.venv/bin/python -m pipeline.extract.preflight --queue /tmp/wave.json
```

Current result: **626 READY, 22 NO_TRIMMED**. Those 22 split into two groups that need
different things.

### Group A — 9 cells: just run trim (~$0.45, mechanical)

They have `text/` and `clean/` but no `trimmed/`, so extract has nothing to read.

    electrician  KS NY
    hvac         KS NY SD
    plumbing     KS NY NE WY

```bash
printf '{"electrician":["KS","NY"],"hvac":["KS","NY","SD"],"plumbing":["KS","NY","NE","WY"]}' > /tmp/t.json
pipeline/.venv/bin/python -m pipeline.pipeline_stages --queue /tmp/t.json --target trim --yes
```

Note plumbing/NE has 0 sections in `text/` — trim will produce nothing and it will stay
blocked. Treat it as Group B.

### Group B — 13 cells: needs a DECISION, not a command

    construction_trades  IN ME NH TX
    electrician          IN PA
    hvac                 CO IN MO NE PA WY
    plumbing             PA

These have **no corpus at all**, and each asserts `regulatory_model = market_forces`
with **no quote and no `coverage_gap` flag**. `market_forces` is the deregulation end of
the UORF ladder — the most consequential claim we publish — and right now it rests on an
empty corpus rather than on evidence.

The extract prompt already forbids this:

> "Absence of a license act in the corpus is NOT by itself evidence of market_forces …
> the state surfaces as a coverage gap — never as market_forces."

**Web-checked 2026-07-31: the VALUES are correct.** These states genuinely have no
statewide licence for that trade — no state GC licence in IN/ME/NH/TX; no statewide
electrician licence in IN/PA (PA leaves it to 2,562 municipalities); no statewide HVAC
licence in CO/IN/MO/NE/PA/WY (Missouri's SB 31 died in the 2025 session); PA plumbing
likewise municipal.

So this is **not** a data-correctness problem. It is an **encoding** problem: an analyst
cannot distinguish "this state deliberately does not regulate" from "we failed to fetch
anything." Both render identically today.

**Suggested fix** (the same shape as the `basis` field shipped today — when you can't
cite, say how you know): add a provenance marker such as
`regulatory_model_basis: no_state_statute_found` plus a short note, so the claim carries
its own justification. Re-extraction can never fix these — with no corpus there is
nothing to extract — so they need a deliberate write, not a wave pass.

Decide this before the wave, or explicitly defer it and exclude the 13 from the queue.

---

## The wave itself

Once preflight passes:

| | |
|---|---|
| cells | 648 extract (+22 trim, 13 clean) |
| cost | **~$49 batch** / ~$97 sync (batch is ~50% cheaper and crash-durable) |
| runtime | median past batch 8 min; 13 batches ⇒ **~2–6 h**, tail risk overnight |

Runtime is inferred from batch *count*, not size — per-batch cell counts aren't recorded
(`n_requests` is null in every file under `results/batches/`). Treat it as an order of
magnitude. **De-risk by running one profession first and timing it**; a prompt problem
then surfaces on 50 cells instead of 648.

Use `pipeline.extract.extract_state_batch` (or `pipeline_stages --queue … --target
extract`), not per-state sync calls.

---

## What changed today that the wave carries

- **Two-pass scope rule** (`extract_state._scope_field_description`). Find category
  grants/exclusions once, then classify each item against them. Cut re-run churn on the
  `not_addressed` boundary **47% → 19%**, measured with replicates against a metric fixed
  in advance. Validated that it does not merely collapse the distribution: all 5 items
  where it differs from a naive re-run **restore the committed original extraction**.
  `CODE_VERSION["extract"]` 1 → 2.
  Only affects the 3 professions with `three_state` scope dims (optometry ×3, nursing ×1,
  electrician ×1). The other 644 cells were already recipe-stale from the July 29 prompt
  work.
- **63 re-trimmed corpora** — artifacts from a superseded trim had silently lost sections
  (NV/HVAC held 1 of 162). Guarded by `tests/test_trim_accounting.py`.
- **WV optometry Article 8B** ("Laser Procedures") mapped and pulled — 0/4 → 3/4 laser
  cells vs OPLR, for $0.17.
- **Four drift cells** re-cleaned + re-trimmed. Zero unexplained staleness remains.

---

## Not deployed

Nothing has shipped since the scope-matrix fix this afternoon. Local-only: the `basis`
UI, WV's data, and the rebuilt cross-profession artifacts.

**Recommendation: hold the deploy until after the wave.** Shipping now invites exactly
the before/after comparison #123 warns about, and the wave rewrites the scope matrices
anyway. One deploy after, not two around it.

```bash
# after the wave
pipeline/.venv/bin/python -m pipeline.publish.refresh_all --professions <...> --deploy
```

---

## Open issues

| # | what | state |
|---|---|---|
| **123** | 45% of `not_addressed` scope cells flip between identical re-runs | reduced to 19%, **still open** |
| **125** | 26 published cells ship sections with **no citation** (LA 8, AZ 7, OK 6, MN 3, NY, CA) — caps what those states can ever highlight | open, not urgent |
| **124** | `pull_missing_sections` reports adding sections it didn't add; want-list inflated by #125 | open |
| 118 | trim losing sections | fixed; the 63 cells need the wave's re-extract |
| 122 | scope mis-tags | stale matrix + display bugs fixed and deployed; residual is #123 |
| 115 | OPLR comparison | informational; WV correction posted |
| 119 | the wave / timeline | this document |

**Tell Atharv** (#119/#122): after the wave the Scope tab will show cells that moved for
reasons that are not improvements. He is the one who will open it Monday.

---

## Operating lesson from today, worth keeping

Six separate measurements were wrong before being checked, always in the direction of
looking worse or bigger than reality:

- a lexical "does the quote name this" heuristic (misread ranges and compound wording)
- two OPLR column mappings (mapped a narrow benchmark column onto a broad field)
- `skipped` counted as a third trim bucket (it is a subset of `sections`)
- `STALE_CLEAN` compared mtimes (2,750 alarms; content hash said 4)
- a single-run prompt experiment reported as a real effect (noise floor was 45%)

**No derived number gets acted on until it has been checked against a case whose answer
you already know.** Loose mappings and lexical proxies consistently made our data look
worse than it is; on every occasion the extraction itself held up.


---

# What actually happened (2026-07-31 evening)

## The blocker was mis-diagnosed

All 22 NO_TRIMMED cells are hand-verified absences (`config/verified_absences.yaml`,
shipped Jul 1 in `ad846429`). They already carry the provenance marker this plan
proposes as new work — `source: verified_absence` + `basis` + `note` — and
`build_frontend.py:598` / `state-detail-dialog.tsx:402` already badge them. Nothing
to design.

Group A was the dangerous half, not the mechanical one. 8 of the 22 HAVE a corpus,
and every one is a non-licensing chapter: KS electrician/hvac/plumbing on chapter-12
art. 15 (Cities and Municipalities), electrician/NY on labor art. 23 (apprenticeship),
hvac/NY on GBS art. 36-B (new-home warranty), plumbing/NY on county art. 5,
plumbing/WY on public-works contracts, and hvac/SD on **Title 36 ch. 26, the Board of
Social Work Examiners**. Extracting them would have overwritten hand-verified records
with claims from statutes that do not license the profession — one-way, since
`apply_verified_absences` never clobbers an extracted record.

Fixed in `c1830dac`: non-blocking `SKIP_ABSENCE` + `drop_skipped()` at both
`extract_state_batch` gate sites + a skip in `build_state_browse` (that blob ships
section TEXT, so a trimmed absence cell would file municipal law under the
profession's name). hvac/SD's corpus deleted in `8bf89912`.

## The cost estimate was wrong — the batch discount was applied twice

`costs.yaml` `extract: 0.15` IS already the batch rate. 648 x 0.15 = $97 is the
BATCH figure this plan labelled "sync", then halved again to reach "~$49 batch".
Corroborated by `results/batches/*.json`: the **2026-07-24 full wave ran 577 cells
across all 13 professions for $86.61 = $0.1501/cell**. Same model
(`claude-sonnet-4-6`) on all 58 recorded batches.

Runtime was also wrong: ~5-6 min per 50-cell profession, so the whole wave is ~1 h,
not "2-6 h, tail risk overnight."

## The wave's value is concentrated in ~29 cells, not spread over 626

Free check first — across 127 re-trimmed cells, **2397 new sections exist and only 6%
are cited by the current extraction**: 2245 sections of law present in the corpus and
invisible in the published data.

Then measured, not assumed. Gain tracks corpus-growth RATIO, not sections added:

| cell | growth | quote-backed claims |
|---|---|---|
| electrician/NV | 145x | 0 -> 43 |
| plumbing/VA | 44x | 21 -> 36 |
| professional_engineering/MS | 31x | 13 -> 54 |
| public_accountancy/WA | 3.3x | 65 -> 69 |
| podiatry/WA | 3.4x | 36 -> 36 (citations 14 -> 12) |
| dentistry/WA | 1.5x | 51 -> 53 |

Cells that gained 50 sections at ~3x gained nothing measurable.

## What was run ($21.57 total)

| batch | cells | cost | result |
|---|---|---|---|
| optometry (pilot) | 50 | $9.02 | 320 scope cells not_addressed -> determinate vs 18 back; +305 net quote-backed |
| medicine (calibration) | 50 | $10.45 | net **+8** quote-backed; 416/517 changes are rephrasing |
| growth-range probe | 10 | $2.10 | established the ratio rule |
| **starved cells (#118)** | 26 | $3.69 | **claims 302 -> 1136 (+276%), citations 45 -> 386 (+758%)** |

0 errored across all 136. 0 consistency violations in any of them.

## What was deliberately left stale

~470 cells. `CODE_VERSION["extract"]` is 2, so they report stale indefinitely — **by
choice, not oversight.** Medicine is the evidence: for a profession with no
`three_state` scope dims, a re-run buys net +8 quote-backed claims per 50 cells while
416 of 517 value changes are rephrasings ("LCME or COCA" -> "LCME; COCA"). That is
issue #123's churn as the dominant effect.

Re-running them buys a clean freshness ledger, not better data. If someone wants it
later it is ~$100 and ~1 h, and preflight now passes on the naive queue unaided.

Still worth doing if revisited: the 3 professions WITH scope dims (nursing,
electrician; optometry is done) — those get the two-pass rule's real gains.

## Not published

136 cells of improved data are committed but NOT deployed, so
`test_global_artifacts_fresh` fails on `scope_matrices` / `scorecard` / the cell-by-cell
check. That failure is accurate — the site is serving pre-re-extract data. It clears on
`refresh_all --deploy`.

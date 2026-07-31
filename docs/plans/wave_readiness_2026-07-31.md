# Re-extract wave — readiness plan (as of 2026-07-31 EOD)

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

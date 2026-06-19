# Similarity & outlier analysis — "what is each state like, and where is it weird"

Per occupation, for any state: which states have the **most similar** licensing
regime, and where that state is an **outlier** (doing something categorically rare,
or much stricter/looser than peers).

## Why it's a hybrid (LLM priors + deterministic math)

Pure math (field agreement) can't know two things, so it gives wrong answers:
- **which fields define a regime** — Hamming treats `advisory_board.exists` as
  mattering as much as `regulatory_model`.
- **how close two categories are** — Hamming says `doctorate` vs `master` is as
  different as `doctorate` vs `none`.

So a few **cheap LLM calls** (cost is O(fields), not O(states×fields)) supply the
semantic priors, and the math does the per-state computation deterministically:

| Layer | What it produces | Where |
|---|---|---|
| LLM (once, per profession) | `importance` per field + value `closeness` (ordinal ladder / nominal) | `config/field_semantics/<prof>.yaml` (editable) |
| seed config (universal) | baseline importance + known ordinals (UORF rung, degree ladder) | `config/field_semantics.yaml` |
| code (deterministic) | similarity → nearest neighbors; kind & stringency outliers; distinctiveness | `pipeline/analyze/similarity.py` |
| LLM (once, per profession) | one-sentence **Utah** characterization | `pipeline/analyze/utah_note.py` |

Both LLM outputs are **reviewable YAML/JSON you can hand-edit** — not hidden scores.

## What the LLM gets right (optometry example)

`gen_semantics` weighted the **scope-of-practice** fields highest —
`laser_procedures_authorized` 0.9, `surgery_prohibited` 0.9,
`oral_pharmaceutical_authority` 0.85 — and trivia lowest (renewal fee, age min 0.1).
With scope-weighting, **Oklahoma** surfaces as a top-distinctive optometry regime
(it permits the most surgical scope), which flat agreement missed.

## Utah, across the published 7 (generated)

- **optometry** — typical, most like Wyoming and Kansas, but stands out by not
  requiring pharmaceutical certification (only ~4 other states; looser than peers).
- **dietetics** — uses certification rather than licensure (only 7 states) and a
  division oversight structure (only 5); most resembles Wisconsin and Washington.
- **medicine** — among the least distinctive, closely mirrors Wisconsin and Vermont;
  no categorically rare requirements.
- **dentistry** — typical (most like CA, AK, CT); one quirk — a shared board
  structure (only 6 of 48 states).
- **nursing** — typical (most like NV, CT); houses oversight in a division rather
  than a board (only one other state).
- **podiatry** — most resembles Oklahoma; limits amputation authority to the
  Chopart joint and below (stricter than nearly all peers) while allowing
  treatment of systemic diseases (only 3 of 15 states).
- **public_accountancy** — highly typical (mirrors WI, VA, TX, TN); no rare or
  measurably stricter/looser rules.

## Running it

```
# per-profession LLM importance + closeness (writes config/field_semantics/<prof>.yaml)
python -m pipeline.analyze.gen_semantics --profession optometry

# deterministic similarity + outliers (prints; --json writes results/analysis/<prof>.json)
python -m pipeline.analyze.similarity --profession optometry --focus UT --json

# one-line Utah characterization (--write stores it in results/analysis/<prof>.json)
python -m pipeline.analyze.utah_note --profession optometry --write
```

## Method notes / knobs

- **Similarity** = importance-weighted mean of `1 − value_distance` over fields both
  states populate; needs ≥5 comparable fields (`MIN_COMPARABLE`).
- **Kind outlier** = value held by ≤20% of states AND far (by value-distance) from
  the modal value, scaled by importance.
- **Stringency outlier** = on ordinal/continuous fields, |z| ≥ 1.5 vs the
  distribution — only meaningful because the LLM supplied the ladder.
- **Distinctiveness** = 1 − mean similarity to all other states.
- Uniform fields (every state identical) are dropped — no signal.

## Not yet done

- Frontend surface (an "occupation vs peers" panel + outlier highlights on the
  existing table/map) — deferred so the numbers can be reviewed first.
- The seed orderings for nominal fields (e.g. `regulatory_authority.type`) are a
  first pass; eyeball `config/field_semantics*.yaml` and adjust.

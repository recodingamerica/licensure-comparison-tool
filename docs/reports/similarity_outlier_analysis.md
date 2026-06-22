# Similarity & outlier analysis — "what is each state like, and where is it weird"

The **Compare** tab on each profession page: for any occupation, which states have
the most similar licensing regime, where a state is an outlier, and a plain-English
line per state. Surfaced via `/data/analysis/<prof>.json` (separate from the
profession payload).

## Design principle: the calc owns the judgment, nothing is faked

Every quantitative/qualitative judgment is **deterministic and reproducible**.
The LLM is used in exactly one place — to *code*, once per profession, two things
the math can't infer:

| LLM codes (once, `gen_semantics.py` → `config/field_semantics/<prof>.yaml`, editable) |
|---|
| `importance` per field — how much each question defines the regime |
| `closeness` — value ladders (ordinal) / distance tables (nominal) |
| optional `phrase` — how to say a field=value in prose |

Everything else — overlap, outliers, the qualitative words, the per-state note —
is plain arithmetic + templates in `similarity.py`. No model sees a state pair,
computes a similarity, picks a magnitude word, or writes a sentence.

## Overlap is computed over a fixed CORE question set

`overlap(A,B) = Σ importance·(1−value_distance) / Σ importance` — but **only over a
core set of questions**: the fields that are both important (`importance ≥ 0.4`)
**and** answered by most states (`coverage ≥ 60%`). This is the key correctness
fix: otherwise overlap rides on whatever sparse subset two states happen to share,
and a state that answers few questions scores a misleadingly high overlap.

- Every pair is graded on the **same** questions → overlaps are comparable.
- A state that answers too few core questions is marked **"not enough data"**
  (shown gray on the map), never given a fake score.
- The squishy, sparsely-answered scope details still appear — as a state's
  per-field **"unusual" flags**, just not as the basis of the overlap.

## No percentages — the calc emits words, not numbers

A weighted judgment isn't a measurement, so the UI never quotes "X% alike."
Magnitude is carried by **map color** and by a **controlled vocabulary** the calc
assigns from fixed thresholds (so "rare" and "uncommon" can't both appear):

- rarity of a choice → `almost unique` · `rare` · `unusual`
- strictness vs peers → `far stricter` / `stricter than most` (and looser)
- overall spread → `vary widely` / `vary moderately` / `are broadly similar`
- per-state band → `typical` · `fairly typical` · `moderately distinctive` · `highly distinctive`

## The per-state note is templated (no LLM)

`build_note()` assembles a sentence from band + nearest neighbors + the top one or
two findings, rendering each `field=value` via name-suffix rules
(`_required`→"requires", `_prohibited`→"prohibits", …) or a `phrase` override.
Works for every state; the Utah line is just `notes["UT"]`. Examples (real output):

- *OK is highly distinctive in Optometry, most like LA, KY, AK. It does not prohibit surgery (far looser than most).*
- *UT is moderately distinctive in Optometry, most like WY, VT, KS. It does not require pharmaceutical certification (far looser than most).*
- *UT is highly distinctive in Dentistry, most like SC, IL, IA. It houses oversight in a shared board (unusual).*
- *UT is moderately distinctive in Podiatry, most like WV, LA, ME. It authorizes amputation up to the chopart joint and below (stricter than most) and does not exclude systemic disease treatment (looser than most).*

## Files

| File | Role |
|---|---|
| `config/field_semantics.yaml` | universal baseline: importance, closeness, `phrase` overrides |
| `config/field_semantics/<prof>.yaml` | per-profession (LLM `gen_semantics.py`), hand-editable |
| `pipeline/analyze/similarity.py` | the deterministic engine: core set, overlap, outliers, labels, notes |
| `pipeline/analyze/gen_semantics.py` | the one LLM step (importance + closeness per profession) |
| `pipeline/analyze/publish_analysis.py` | stage `results/analysis/<prof>.json` → `web/public/data/analysis/` |
| `web/src/components/similarity-view.tsx` | the Compare tab |

## Running it

```
python -m pipeline.analyze.gen_semantics --profession optometry      # LLM: importance + closeness
python -m pipeline.analyze.similarity   --profession optometry --json # deterministic: overlap/outliers/notes
python -m pipeline.analyze.publish_analysis                          # stage for the frontend
```

## Knobs (in `similarity.py`, all editable)

- `CORE_IMPORTANCE = 0.4`, `CORE_COVERAGE = 0.6` — what counts as a core question.
- `RARE_SHARE = 0.20`, `STRINGENCY_Z = 1.5` — outlier thresholds.
- vocabulary bands in `rarity_label` / `stringency_label` / `band_for`.

## Known rough edges (review + tune)

- Bare-leaf field labels in the UI ("Type", "Available") lose their parent — the
  *note* folds the parent in (`clause()`), the UI `fieldLabel` does not yet.
- Continuous fields are dropped from the prose note (they'd leak a raw number);
  they still drive distinctiveness.

## Publish + confidence

- `refresh_all` now runs `similarity --json` per profession (deterministic, after
  build_frontend) then `publish_analysis`, which mirrors to `public/data/analysis/`
  AND uploads to Blob at `data/analysis/<prof>.json` — same path as the payloads,
  so the live site serves it. `gen_semantics` (the one LLM step) stays manual.
- `core_coverage` per state = how much of the core it answers. States below 0.7 are
  "low confidence" (their distinctiveness rides on thin overlap): dropped from the
  headline "most distinctive" list and flagged on hover, though still mapped.
  Sub-60%-core states are excluded entirely (gray).

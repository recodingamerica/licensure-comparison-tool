# Optometry — spot-check starting points

_AI-assisted pass over the 49 extracted optometry states (June 2026). Meant as
a starting list for manual review, not a verdict._

## Overall
Optometry is in good shape. `regulatory_model` is uniformly **license** across
all 49 states (expected — optometry is a full-licensure profession everywhere),
and core fields (licensing authority, scope, discipline) are populated for
nearly every state.

## Real gaps worth checking

### 1. Centralized-discipline states (umbrella chapter not pulled)
Two states have suspiciously few disciplinary grounds because their general
disciplinary statute lives in a state-wide chapter we didn't pull — only the
profession-specific chapter was extracted:

| State | Grounds | Pulled from | General-discipline chapter to add |
|-------|---------|-------------|-----------------------------------|
| IN    | 2       | IC 25-24 (optometry) | **IC 25-1-9** (general health-profession discipline) |
| MT    | 4       | 37-10-301 (optometry) | **Title 37-1** (Uniform Professional Licensing) |

Fix = per-state scope manifest adding the umbrella discipline chapter (same
pattern documented for centralized-discipline states like WA Ch 18.130 /
NE Title 38).

### 2. MI degree (minor)
`education.degree_required` is null, but the requirement is captured in
`accrediting_body` ("a school or college of optometry recognized by the board
as fully accredited", cite 333.17412). The info exists; it just landed in the
adjacent field. Low priority.

## Unverified quotes to eyeball (7)
Extractions the verifier couldn't string-match back to source — most are
profession-specific and likely fine, but worth a glance:

- KY — controlled-substance schedule restrictions
- VA — controlled-substance schedule restrictions
- SD — minor surgical procedures authorized
- CA — spectacle prescription release required
- MN — regulatory authority name / type / advisory-board exists (MN comes from
  a non-Justia source, so formatting differs)

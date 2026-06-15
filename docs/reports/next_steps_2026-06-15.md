# Next steps — 2026-06-15

## Current state

- **Branch:** `feature/dietetics-audit-reextract`, **PR #27**, 7 commits ahead of `main` (all pushed). Not merged.
- **Live site:** utah-licensing.vercel.app. Deployed this session: dietetics, medicine, public_accountancy, nursing, podiatry payloads.
- **Issues open:** #25 (dietitians — only PA gap left), #26 (optometrists — only PA gap left), plus the engineering/feature issues #1/#2/#6/#7/#8/#14/#15/#16/#17/#19.

## Done this session (all committed on the PR branch)

- **#17 sort bug** — `regulatory_model` column now sorts by UORF rung order, not alphabetically.
- **No hard-coding of credential calls** — AZ & CO dietetics now derive `market_forces` from statute (§36-416, §6-1-707); removed CO from `no_credential_states`. New prompt rule: `credential_type=none` ⟹ `market_forces` (overrides the title/scope rung test).
- **#6/#7 year-versioned dedup** — `pull_text` now de-duplicates Justia year-versioned pages (self-snapshot drop + `_dedupe_year_versions`). **Code fix is the deliverable**; the existing committed corpora are complete (just bloated) so a mass re-pull is NOT needed (and Justia rate-limits bulk pulls — never mass-fetch; transform corpora locally). Dietetics 9 dedup states re-extracted.
- **Gap fixes (flagship near-empty records):** NC medicine (null→license/17 disc), OK medicine (null→license/22 disc), OK public_accountancy (null→license/12 disc), KY podiatry (0→16 disc via §§380–500 pattern widening), MT nursing (0→6 disc).
- **Caught regressions:** TX dietetics (`license`→corrected `voluntary_certification`); LA public_accountancy re-extract regressed → reverted.
- **`match_profession`** — opt-in `authoritative: true` flag on a state_structure entry drops label-matched siblings (used for NC medicine).
- **Root `CLAUDE.md`** — documents that fetched corpora live locally (don't re-fetch), the pull→clean→trim→extract stage order, and the skip-`clean_text` staleness gotcha.
- **Health:** project-wide cross-field consistency sweep = 0 rung-vs-protection issues.

## Next steps (priority order)

1. **Merge PR #27** (or keep iterating on the branch). 7 commits of dietetics audit + gap fixes + dedup + docs.
2. **LA public_accountancy discipline gap** — 0 disc grounds is a *corpus gap* (discipline section not pulled), not an extraction miss. Recipe = same as KY podiatry: fetch LA accountancy chapter, find the discipline section range, widen/point the `state_structure.yaml` entry, then pull→clean→trim→extract. Cheap.
3. **PA scraper (#25/#26)** — the one remaining dietitian AND optometrist gap. Justia coverage of PA is too sparse (pamphlet-law numbering); needs a custom palegis.us scraper. Bigger lift; unblocks both issues.
4. **#8 MI act-level extraction** — MI umbrella pulls whole-act blobs instead of sections; needs an act→section drill for the `mi_legis` source.
5. **Optional / cosmetic:** local-dedup the other ~85 committed corpora (year-versioned bloat). LOW value — classifications are stable under dedup, and re-extracting risks TX-type regressions. The `pull_text` code fix already prevents future bloat. **Recommend NOT mass-re-extracting.**

## Decisions waiting on the PM (don't action without OK)

- **#19** — automated LLM bucketing vs. hand-authored vocabularies for high-value fields.
- **#16** — cross-profession bucket harmonization (3 options proposed).
- **#15** — review the LLM-derived bucket labels per profession.
- Close #25 / #26? (Both substantively resolved except PA.)

## Standing rules (now in CLAUDE.md + memory)

- Fetched data is local & committed — never mass-re-fetch from Justia (it rate-limits; corrupts corpora). Transform locally.
- Re-extract = full pull→clean→trim→extract chain (skipping `clean_text` silently uses stale corpus).
- Re-extracting already-correct data risks regressions for no gain — only re-extract to fix a real gap, and verify with the cross-field consistency sweep + live distribution after.
- Never hard-code credential calls; fix the prompt instead.

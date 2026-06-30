# WA disciplinary-umbrella mechanism (supplementary umbrella chapters)

**Status:** mechanism + tests SHIPPED 2026-06-30 (LLM-free). WA rollout (re-pull → clean →
trim → extract the 6 health professions) is the only LLM/HTTP step left — do it tomorrow.

## Problem
WA centralizes disciplinary grounds in Title 18 **Ch 18.130** (Uniform Disciplinary Act).
Each health profession's own chapter (18.71 physicians, 18.79 nursing, …) defers to 18.130 for
grounds / complaints / sanctions. Our WA corpora pull only the profession-specific chapter
(verified: `text/medicine/WA.json` = 18.71 / 18.71B only, no 18.130), so the 6 WA health
professions under-capture the enforcement dimension that feeds `regulatory_model`.

The old config tried to merge 18.130/18.122/18.235 via per-section **Justia** URLs in a
duplicate `WA:` block that was silently dropped (and Justia is Cloudflare-blocked now anyway).
Recovered verbatim to `pipeline/config/_disabled/wa_disciplinary_umbrella.yaml`.

## Decision taken
Add **Ch 18.130 only** (the substantive Uniform Disciplinary Act). 18.122 (admin procedure) and
18.235 (biz-reg) are lower-value boilerplate — left out; revisit if a record looks thin. Built as
a **general state-level umbrella mechanism**, not a WA one-off, so it also serves the
centralized-discipline pattern (MI/NE/NJ/CA — see memory `reference_centralized_discipline_pattern`).

## Mechanism (how it works)
New optional state-level block in `state_structure.yaml`:

```yaml
WA:
  source: wa_official
  chapter_url_template: "https://app.leg.wa.gov/RCW/default.aspx?cite={chapter_dot}&full=true"
  umbrella:
    professions: [medicine, nursing, optometry, podiatry, dentistry, public_accountancy]
    chapters:
      - url: "https://law.justia.com/codes/washington/title-18/chapter-18-130/"
        label: "WA Ch 18.130 — Uniform Disciplinary Act (grounds, complaints, sanctions)"
```

`build_index_for` (match_profession.py): after the per-profession match list `m` is built and
after the `authoritative` pruning, if `profession in state_entry.umbrella.professions`, append one
**additive, non-authoritative** node per umbrella chapter (`via: state_structure_umbrella`),
skipping any whose url is already matched. The existing `chapter_url_template` loop then rewrites
each umbrella node's Justia chapter url → the official `cite=18.130&full=true` url — so the
umbrella is fetched from app.leg.wa.gov, never Justia.

Why a Justia-style `url` (not the official one directly): `_official_url` parses
title/chapter/section out of the Justia path; giving the umbrella the same shape lets the one
template serve practice-act and umbrella nodes identically. (You can also give a pre-built official
url; the rewrite is a no-op if `_official_url` can't parse it.)

## Rollout (tomorrow — HTTP + LLM)
1. (done) Mechanism + `umbrella:` block live; tests green.
2. Regenerate the WA index: `match_profession` for the 6 profs (deterministic, no fetch) → each
   WA index gains the 18.130 node.
3. Re-pull WA for the 6 profs (official source app.leg.wa.gov — HTTP, not Justia, not LLM):
   `pull_text --profession medicine --states WA` … (one at a time per the Justia-pull caution,
   though this hits wa_official not Justia).
4. `clean_text` (regex) → `trim_state` (Haiku) → `extract_state_batch` (Sonnet) for the 6.
   Preflight gate covers them. Fold into tomorrow's published-refresh pass (WA is published).
5. `git diff structured/*/WA.json` to confirm the discipline fields populate; then refresh_all.

## Files
- mechanism: `pipeline/discover/match_profession.py` (`_umbrella_nodes_for`, wired into `build_index_for`)
- config: `pipeline/config/state_structure.yaml` WA `umbrella:` block
- test: `tests/test_match_profession.py` (umbrella append + template rewrite)
- recovered original: `pipeline/config/_disabled/wa_disciplinary_umbrella.yaml`

# Cross-profession gap scan (June 2026)

_AI-assisted pass over all extracted states, flagging likely data gaps for
manual review. A "gap" here = a field that's suspiciously empty given the
profession, usually because the relevant statute sits in a state-wide chapter
we didn't pull (the "centralized-discipline" pattern)._

## Headline: Montana is a systemic centralized-discipline gap
Montana shows low/zero disciplinary grounds across **dentistry, nursing,
optometry, and public accountancy** — because MT centralizes professional
discipline in **Title 37-1 (Uniform Professional Licensing Act)**, which isn't
pulled for any profession. **One scope fix (add MT Title 37-1) resolves
discipline gaps across 4+ professions at once** — the highest-leverage fix on
this list.

## Per-profession flags

| Profession | Low discipline (<5 grounds) | Missing scope | Missing licensing authority |
|---|---|---|---|
| podiatry | KY(0), NH(2), WI(4), IN(4) | — | — |
| medicine | OK(0), PA(0), NC(0) | PA, MO, NC, OH | OK, NC |
| dentistry | NM(4), MT(4) | NM | — |
| nursing | MT(0) | — | — |
| optometry | MT(4), IN(2) | — | — |
| public_accountancy | OK(0), LA(0), AZ(1), MT(4) | OK, NE | OK |

## Reading the flags
- **Centralized-discipline candidates** (low grounds, profession-specific
  chapter pulled but general chapter missing): MT (everywhere), KY/NH/IN
  (podiatry), OK/LA/AZ (accountancy), NM (dentistry). Fix via per-state scope
  manifests adding the umbrella discipline chapter.
- **Hard-source states** (broad gaps — missing scope/authority too): OK
  (section-fallback source), PA (broken Justia coverage), NC, MO, OH for
  medicine. These need a source fix, not just a scope addition.

## Suggested order of attack
1. **MT Title 37-1** — one manifest entry, fixes 4+ professions.
2. OK / PA / NC medicine — source-level gaps, higher effort.
3. Profession-specific singles (KY/NH podiatry, NM dentistry, LA/AZ accountancy).

# START HERE — next session (handoff 2026-07-02, updated PM)

Tree is clean, full suite green (532+), everything committed. Safe cold-start.

## The "everything-except-PA to Justia" flip is nearly done

- **MN — DONE.** 9 professions re-pulled from Justia + committed. Justia MN is
  RANGE-GROUPED not year-versioned: `/codes/minnesota/chapters-{LO}-{HI}/chapter-
  {N}/section-{N}-{sub}/` (147/147A/148/150A/153 in `144-159`, 326A in `324-342`).
  Ch 148 is shared by chiro/nursing/optometry/dietetics — kept explicit
  `section_url_list`s (converted from revisor cites, intersected with Justia's live
  148 sections; repealed auto-dropped).
- **UT / AZ / FL / MO trades — DONE.** UT `title-58/chapter-55` (parts; source:
  utah_le retired) + 58-1 umbrella on all 4 trades; AZ `title-32` +
  `section_slug_pattern` (contractors §§32-1101..1188); FL `chapter-489/part-i`;
  MO `chapter-341` (no-year). Every url leaf-verified LIVE via `verify_urls` first.
- **MI — STILL OPEN. The one hard remainder** (7 chapters, MCL Part-objects:
  `mcl-368-1978-15-<part>`; MI = Compiled Laws Ch 333, parts are section ranges).
  May not be cleanly flippable. PA stays official (the one documented exception).

## Two new LLM-free tools (built this session)

- **`pipeline.eval.verify_urls`** — URL health probe (`LIVE|STUB|DEAD_404|CHALLENGE`).
  HTTP 200 is meaningless on Justia; this is the leaf-verify GATE as a command.
  Gate every new/changed Justia mapping through it. 8 tests.
- **`pipeline.eval.corpus_drift`** — flags committed corpora that silently diverged
  from their index mapping (HOST_DRIFT / EXTRA_CHAPTER / MISSING_CHAPTER). Skips
  active official-source states. Run in preflight/CI. 11 tests.
- **`refresh_corpus` EMPTY→DEAD split** — on a 0-section pull it now probes the
  chapter url and returns `DEAD` (bad link, `url_health` set) vs `EMPTY` (live page,
  scoping miss) instead of a silent EMPTY.

## ⭐ The big finding: corpus-level flip is only ~partly done

`corpus_drift` first run: **227 drifted (prof,state), 97 HOST_DRIFT — NV (40),
MD (30), NY (25).** These states' INDEXES were bulk-flipped to Justia (Jul-1
template retirement + MD/NV source retirement) but their CORPORA were never
re-pulled — ~95 stale official-source corpora silently answering a Justia mapping.
**This is the true remaining scope of "everything→Justia."** It's a large CDP
re-pull + extract job. Re-generate the list: `python -m pipeline.eval.corpus_drift
--host-drift-only`. (The 89 same-host EXTRA_CHAPTER cases are mostly stale umbrellas
/ dropped chapters — lower priority; review before re-pulling.)

## Downstream still owed (LLM cost — needs go-ahead)

clean→trim→extract→republish the flipped corpora (MN's 7 published profs;
UT/AZ/FL/MO trades). Nothing is user-visible until this runs. Per the re-extract
gotcha, run pull→clean→trim→extract in full (skipping clean silently uses stale text).

## Other queued non-LLM

- MI flip (above). Relative `/codes/` index URLs: 42 total, mostly redundant
  siblings, but **public_adjuster/MD is empty + hostless + section-nested** — a real
  gap. Root is likely `probe_justia.links()` storing code-relative hrefs.
- config hygiene: models.yaml (16 ids), limits.yaml threshold sweep, delete
  superseded `.scratch/_cdp*` drivers.

## Before ANY harvest — read first

`docs/runbooks/cdp_repull_lessons_2026-07-02.md`. ONE scraper (flock); start a
debug Chrome, clear the challenge once (`127.0.0.1:9222`); `refresh_corpus` is the
tool; don't run two committing processes at once (git index.lock); faulthandler
(`kill -ABRT`) is the wedge-check.

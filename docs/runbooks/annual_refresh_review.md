# Runbook — reviewing the annual refresh's held cells

The annual refresh (`refresh_corpus --all-professions`) re-pulls every committed corpus and
**commits only healthy pulls**. A pull that comes back shrunk / collapsed / partial is a
`REGRESSION`: the gate **reverts it** (keeps the committed corpus) and stages the rejected
candidate in `results/pending_review/<run-id>/`. `--skip-held` lets the run keep moving.

**No data is ever at risk here.** Every held candidate was already reverted; this review only
decides, per cell, whether to **re-pull** (the reject was a flake) or **accept** the candidate
(it was a real change the gate rejected over-conservatively). You do this once, after the run
finishes.

---

## 1. Triage — what's held and why

```bash
python -m pipeline.ingest.refresh_corpus --review --run-id annual2026
# writes pending_review/annual2026/review.html — open it in a browser
```

The review page shows every held cell with the exact sections added/removed, text samples, an
Accept checkbox (checking cells live-builds the copy-paste `--apply` command), and — grouped at
the top — an **LLM-free verdict badge** that buckets each cell on the gate's own key (citation
overlap between committed and candidate):

| Verdict | Signal | What it means | Action |
|---|---|---|---|
| 🟢 **GROWTH** | kept ~all committed citations **and added more** | a *more complete* pull the gate rejected too conservatively | inspect → **accept** (check the box) |
| 🔴 **FETCH_FLAKE** | candidate has fetch errors, or <30% citation overlap | landed on the wrong page / a different article, or truncated | **re-pull**; usually resettles to NOCHANGE. Persists → mapping problem (check the index). |
| 🟠 **CHANGE** | high overlap, a few sections dropped | a genuine repeal or a transient dropped section | re-pull to confirm; stable drop → **accept** as a real change |

## 2. Act on each bucket

**FETCH_FLAKE → re-pull** (one fetcher at a time; the crawl must be paused or done):
```bash
python -m pipeline.ingest.refresh_corpus --profession hvac --states LA
```
If the fresh pull is healthy it commits (or reports NOCHANGE) and the cell clears. If the same
bad pull repeats, it's not a flake — the mapping in `results/profession_index/<prof>.json` is
pointing at the wrong chapter/article (e.g. hvac/NC pulled ch-87 **article-5** instead of the
HVAC **article-2**); fix the mapping via `config/mapping_overrides.yaml`, then re-pull.

**GROWTH / confirmed CHANGE → accept the staged candidate** (no re-fetch — commits what's already
in `pending_review/`):
```bash
python -m pipeline.ingest.refresh_corpus --apply --run-id annual2026 \
    --accept medicine:WA,dentistry:WA,medicine:DE,medicine:UT
```
Or accept a *fresh* re-pull that's a genuine recodification with `--force`:
```bash
python -m pipeline.ingest.refresh_corpus --profession medicine --states TN --force
```

## 3. Re-extract the cells whose corpus changed

Accepting a candidate (or a `--force` re-pull) changes `results/text/`, so the downstream stages
are now stale for those cells. Re-run them (see [`pipeline_run_order.md`](pipeline_run_order.md)):
```bash
printf '{"medicine": ["WA","DE","UT","TN"]}' > /tmp/reextract.json
python -m pipeline.pipeline_stages --queue /tmp/reextract.json --target extract --start clean
python -m pipeline.publish.refresh_all --professions medicine    # rebuild + (add --deploy to ship)
```
FETCH_FLAKE cells that resettle to NOCHANGE need no re-extract — their corpus didn't change.

---

## Snapshot — the annual2026 run (mid-crawl; will grow as it finishes)

As of this writing the run has **18 held cells**: 6 FETCH_FLAKE, 2 GROWTH, 10 CHANGE. Re-run
`--review` for the current, complete set — the count climbs as the crawl reaches more cells.
Notable:

- **GROWTH (accept — better data):** `medicine/DE` (130→152), `medicine/UT` (31→53) — kept every
  usable committed citation and added more.
- **Grew but flagged CHANGE (accept after a glance):** `medicine/WA` and `dentistry/WA` both
  gained a lot of sections but dropped a handful too, so they land in CHANGE — open them, confirm
  the drops are renumbering, and accept.
- **FETCH_FLAKE (re-pull):** `acupuncture/KY` (pulled 0 sections), `hvac/LA` (pulled an unrelated
  metal-theft statute), `hvac/NC` (wrong article), `medicine/NV` (172→71), `medicine/IA` (20→6).
- **CHANGE (re-pull, then accept if stable):** mostly 1-3 section drops at ≥90% overlap
  (`cosmetology/IL`, `dental_hygienist/IL`, `dentistry/AK`, `dietetics/TX`, `medicine/TN`, …);
  `electrician/CO` (48→24) is the one worth eyeballing first.
- **Known non-issue:** `health_facility_admin/OK` is an admin-code-only regime (no statute on
  Justia) — an accepted `source_unavailable` gap, not something to re-pull.

---

## Worked example — the annual2026 holds (reviewed 2026-07-28)

108 cells held; 72 had a reviewable candidate. **Triage by STATE before working the
list**: the holds clustered (WA 6, IL 6, UT 5, CA 4), and in WA a single root cause
explained all six. Working the runbook's per-cell buckets first would have meant
re-pulling six cells to rediscover one fact.

**Do not trust the verdict badge on its own.** It keys on citation OVERLAP, not section
count, so it mislabels in both directions:

* `architecture:TX` — badged **GROWTH**, `6 -> 330 sections`. Accepting it would have
  pulled all of Title 6 (engineers, geoscientists, landscape architects, interior
  designers, land surveyors) into architecture. The cell's real problem was a
  whole-title mapping; fixed by pinning to chapter 1051 (78 sections) with
  `authoritative: true`. More sections is not more complete when the mapping is wrong.
* `nursing:WA` — badged **GROWTH**, `391 -> 169 sections`, i.e. a 57% shrink.

**The WA cluster (6 cells) was zero actual problems:**

* optometry, podiatry, public_accountancy, dentistry, medicine each lost exactly
  chapters 18-122 (19 sections) and 18-235 (27) — the constant `-46` that made the
  cluster visible. Both already live in `umbrella_text/WA.json`, which extract_state
  folds into every WA profession and build_frontend ships with the row. The sections
  stopped being duplicated into six corpora and now live once in the shared one. The
  candidates are CORRECT; no law was lost.
* nursing:WA is the reverse of how it reads. The committed 120 sections (18.79 Nursing
  + 18.130 Uniform Disciplinary Act) are the CLEAN corpus; the candidate re-adds 18.88,
  18.80, 18.52C plus 60.44 (liens) and 5.62 (definitions) — not nurse licensure. The
  index is already pinned authoritative to 18.79, so the hold is a stale artifact of the
  pre-pin mapping and a re-pull today reproduces the committed corpus exactly. Dismiss.

**Method that worked**: diff committed vs candidate by CHAPTER (group section citations
on their `NN.NN` prefix), then check whether the dropped chapters appear in
`umbrella_text/<STATE>.json`. Covered there = de-duplication, accept. Not covered =
real loss, investigate. A constant delta across unrelated professions in one state is
always a shared component, never N independent flakes.

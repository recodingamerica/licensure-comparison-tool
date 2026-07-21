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

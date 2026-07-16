"""Durable annual Justia re-pull — the tested replacement for the throwaway
`.scratch/overnight_repull.py` and the `_cdp_*` batch drivers.

`refresh_corpus` re-pulls the FROZEN url map (results/profession_index/<prof>.json)
for the annual refresh and the Utah handoff. It reuses pull_text's fetching
(`pull_state`, headless via Scrapling) — it does NOT reimplement fetching — and
wraps it in a commit gate + reporting layer:

  * a startup liveness precheck — one real Justia fetch must succeed before any work;
  * PER-CHAPTER completeness — a mapped chapter that came back with 0 sections is a
    partial and is NOT committed (the all-or-nothing total-count check would miss it);
  * ONE shared shrink guard — the commit gate is pull_text._is_regression (the SAME
    guard the interactive puller uses): a pull that loses error-free sections or
    whose text collapses is a REGRESSION and is held back unless --force. (Before
    2026-07-16 refresh_corpus had only the per-chapter check, so a corpus that
    collapsed 200->12 sections — each chapter keeping one — committed silently.)
  * real-fetch detection via `git diff` — an unchanged file after a re-pull is a
    NOCHANGE (the statute didn't change this year), NOT a failure;
  * a per-item wall-clock timeout so a genuine hang can't wedge the run forever;
  * a circuit breaker that counts only genuine FETCH FAILURES (empty/dead) — a run
    of those means the fetcher is wedged. NOCHANGE and held-back results do NOT
    advance it, so a normal low-change annual refresh completes instead of aborting
    after 3 unchanged states (the pre-2026-07-16 behavior, a CDP-era assumption:
    a dead browser used to return the cached page as NOCHANGE; under Scrapling a
    dead fetch surfaces as EMPTY, which the breaker still counts);
  * per-item commits (never `git add -A`), the message naming prof/state + old→new;
  * a year-over-year DIFF REPORT (docs/reports/refresh_diff_<runid>.md) written on
    EVERY exit path (normal, breaker, timeout) — held-back and grown/shrunk rows
    both surface for human review; recodification (a chapter vanished) is flagged.

CLI:
  python -m pipeline.ingest.refresh_corpus --profession X [--states A,B]
         [--all-professions] [--force] [--report-only] [--run-id ID]
         [--item-timeout SECONDS] [--breaker N]

`--report-only` regenerates the diff report from the last-run status WITHOUT
fetching (pure analysis of what the last refresh changed vs the pre-refresh HEAD).
"""

from __future__ import annotations

import argparse
import collections
import json
import subprocess
import sys
import threading
import time
import urllib.parse
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from pipeline.paths import RESULTS_DIR, PROFESSION_INDEX_DIR, TEXT_DIR
from pipeline.ingest import pull_text

ROOT = Path(__file__).resolve().parents[2]

# Only a genuine FETCH FAILURE (nothing usable came back) advances the circuit
# breaker — a consecutive run of these means the fetcher is wedged and the rest
# of the worklist would waste time. NOCHANGE (statute unchanged), a committed OK,
# and the held-back PARTIAL/REGRESSION all got a real response, so they RESET the
# breaker. This is why a normal annual refresh — where most states are unchanged
# NOCHANGE — no longer trips the breaker on the 3rd unchanged state.
FETCH_FAILURE = {"EMPTY", "DEAD", "NOFILE", "TIMEOUT"}

# Result -> severity label for results that are NOT committed (held back). Kept in
# one place so the run loop, the breaker, and the diff report agree on the taxonomy.
HELD_SEVERITY = {
    "REGRESSION": "held back — suspicious shrink (re-run with --force to accept)",
    "PARTIAL": "held back — partial pull (a mapped chapter came back empty)",
    "EMPTY": "held back — empty pull (no error-free sections)",
    "DEAD": "held back — empty pull (dead/stub chapter link)",
    "TIMEOUT": "held back — item timed out",
    "NOFILE": "held back — corpus file never appeared",
}


# ---------------------------------------------------------------------------
# Source liveness
# ---------------------------------------------------------------------------
def justia_reachable(url: str = "https://law.justia.com/codes/kansas/") -> bool:
    """Can we fetch a Justia page right now? A startup precheck via one real
    pull_text.fetch() (headless Scrapling) — if it can't clear Cloudflare or
    Scrapling isn't installed, the whole run aborts before touching any corpus
    rather than committing empties."""
    status, _html, err = pull_text.fetch(url)
    return status == 200 and err is None


# ---------------------------------------------------------------------------
# git helpers (per-item commit; never `git add -A`)
# ---------------------------------------------------------------------------
def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def _rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def file_changed(path: Path) -> bool:
    """True if `path` differs from its committed (HEAD) version. A re-pull of an
    incomplete corpus MUST change the file; unchanged = the pull was a no-op.

    `git diff --quiet` silently ignores UNTRACKED files (exit 0 = "no differences"
    even for brand-new content) — it only compares tracked paths. An untracked
    file with any content IS the change (there's no baseline to diff against), so
    a first-time pull of a new (profession, state) is correctly treated as changed
    (see docs/runbooks/cdp_repull_lessons_2026-07-09.md)."""
    r = _git("ls-files", "--error-unmatch", "--", _rel(path))
    if r.returncode != 0:
        return True  # untracked: never committed, so any write is new
    r = subprocess.run(["git", "diff", "--quiet", "--", _rel(path)], cwd=ROOT)
    return r.returncode != 0  # nonzero = differs


def prior_committed(path: Path) -> dict | None:
    """The corpus at HEAD (before this run touches it), or None if untracked."""
    r = _git("show", f"HEAD:{_rel(path)}")
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def revert(path: Path, has_head: bool) -> None:
    """Undo an uncommitted write. For a file with a committed baseline, restore
    HEAD. For an untracked (never-committed) file, `git checkout` is a NO-OP — so
    delete it, otherwise a bad first-time pull's empty/partial file is left on disk
    for the next stage (clean_text) to consume as if it were real."""
    if has_head:
        _git("checkout", "--", _rel(path))
    elif path.exists():
        path.unlink()


def commit(path: Path, msg: str) -> None:
    _git("add", _rel(path))
    _git("commit", "-q", "-m", msg,
         "-m", "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>")


# ---------------------------------------------------------------------------
# Per-chapter completeness (total count alone can't see a partial)
# ---------------------------------------------------------------------------
def _canon_path(url: str) -> tuple[str, ...]:
    """Path segments with Justia year segments stripped, so a section under a
    year-versioned snapshot still maps to its unversioned chapter."""
    segs = [s for s in urllib.parse.urlparse(url).path.split("/") if s]
    return tuple(s for s in segs if not pull_text.YEAR_SEG.match(s))


def sections_per_chapter(chapter_urls: list[str], sections: list[dict]) -> dict[str, int]:
    """Attribute each section to one of the mapped chapters and count.

    Justia sections share the chapter's canonical path prefix, so prefix-match.
    With exactly one mapped chapter every section belongs to it (covers an
    official-source host rewrite whose section urls won't prefix-match). With
    multiple chapters and non-prefixing urls a section is left unattributed — it
    still counts toward the total but not toward any one chapter, keeping a
    genuinely empty chapter flagged."""
    counts: dict[str, int] = {u: 0 for u in chapter_urls}
    if len(chapter_urls) == 1:
        counts[chapter_urls[0]] = len(sections)
        return counts
    canon = {u: _canon_path(u) for u in chapter_urls}
    # Longest chapter path first so a section under a nested chapter is attributed
    # to the deepest matching chapter, not a shallow ancestor.
    ordered = sorted(chapter_urls, key=lambda u: len(canon[u]), reverse=True)
    for sec in sections:
        sp = _canon_path(sec.get("url", ""))
        for u in ordered:
            cp = canon[u]
            if len(sp) >= len(cp) and sp[:len(cp)] == cp:
                counts[u] += 1
                break
    return counts


def empty_chapters(chapter_urls: list[str], sections: list[dict]) -> list[str]:
    """Mapped chapters that contributed 0 sections — the partial-pull signal."""
    counts = sections_per_chapter(chapter_urls, sections)
    return [u for u in chapter_urls if counts.get(u, 0) == 0]


# ---------------------------------------------------------------------------
# Per-item wall-clock timeout around pull_state
# ---------------------------------------------------------------------------
class _ItemTimeout(Exception):
    pass


def pull_with_timeout(state: str, profession: str, rows: list[dict],
                      cap: int | None, timeout_s: int):
    """Run pull_text.pull_state under a wall-clock timeout. Returns the corpus.
    Raises _ItemTimeout on hang, or the original exception otherwise.

    The worker is a daemon thread we CANNOT kill; on timeout the run loop aborts
    the whole run (rather than starting the next item), so the orphan can't race
    the next pull on the shared Scrapling session — the process exits and the
    daemon dies with it. See run()."""
    result: dict = {}

    def _work():
        try:
            result["corpus"] = pull_text.pull_state(state, profession, rows, cap)
        except Exception as e:  # noqa: BLE001 — re-raised in the caller thread context
            result["error"] = e

    t = threading.Thread(target=_work, daemon=True)
    t.start()
    t.join(timeout_s)
    if t.is_alive():
        raise _ItemTimeout(f"pull_state exceeded {timeout_s}s wall clock (genuine hang)")
    if "error" in result:
        raise result["error"]
    return result["corpus"]


# ---------------------------------------------------------------------------
# The per-item refresh
# ---------------------------------------------------------------------------
def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _classify_empty(chapter_urls: list[str]) -> dict[str, str]:
    """When a pull comes back with 0 sections, probe each mapped chapter url to
    say WHY it's empty: a dead/stub LINK (find a new url — the form is wrong) vs a
    LIVE page that simply had no matching sections (a scoping / section_slug_pattern
    miss). LLM-free; only runs on the rare EMPTY path. Turns a silent EMPTY into an
    actionable one."""
    try:
        from pipeline.eval.verify_urls import probe
    except Exception:
        return {}
    out = {}
    for u in chapter_urls:
        try:
            out[u] = probe(u).get("verdict", "?")
        except Exception as e:
            out[u] = f"probe-error: {type(e).__name__}"
    return out


def refresh_item(profession: str, state: str, rows: list[dict], *,
                 force: bool, cap: int | None, timeout_s: int) -> dict:
    """Re-pull one (profession, state), validate against the committed corpus, and
    commit iff the pull is healthy.

    Returns a status record with a `result` in:
      OK           — real fetch, every chapter populated, no regression; committed
      NOCHANGE     — byte-identical to HEAD (statute unchanged / nothing fetched)
      REGRESSION   — lost error-free sections or text collapsed vs HEAD; reverted,
                     NOT committed (re-run with --force to accept a real shrink).
                     `reason` carries the pull_text._is_regression message.
      PARTIAL      — a mapped chapter came back empty; reverted
      EMPTY        — 0 error-free sections, chapter urls are LIVE (scoping miss); reverted
      DEAD         — 0 error-free sections AND a chapter url probes DEAD_404/STUB
                     (the link is wrong — find a new one); reverted. `url_health` set.
      NOFILE       — the corpus file never appeared
    A pull that hangs raises _ItemTimeout (the run loop aborts the whole run); any
    other pull error propagates to the run loop, which aborts loudly rather than
    committing bad data.
    """
    out_path = TEXT_DIR / profession / f"{state}.json"
    chapter_urls = [r["chapter_url"] for r in rows]
    old_d = prior_committed(out_path) or {}
    has_head = bool(old_d)
    prev_ok, _ = pull_text._corpus_health(old_d)
    prev_n = len(old_d.get("sections") or [])

    corpus = pull_with_timeout(state, profession, rows, cap, timeout_s)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    new_d = asdict(corpus)
    out_path.write_text(json.dumps(new_d, indent=2))
    sections = new_d.get("sections") or []
    n = len(sections)
    new_ok, _ = pull_text._corpus_health(new_d)

    rec: dict = {"profession": profession, "state": state, "prev": prev_n, "new": n,
                 "prev_ok": prev_ok, "new_ok": new_ok, "at": _now()}

    # 1. No error-free sections at all → empty pull. Probe WHY (dead link vs live-
    #    but-unmatched) and revert. Uses ok-count, not raw len, so a pull whose
    #    every section errored is caught here rather than committed.
    if new_ok == 0:
        revert(out_path, has_head)
        rec["result"] = "EMPTY"
        rec["url_health"] = _classify_empty(chapter_urls)
        if any(v in ("DEAD_404", "STUB") for v in rec["url_health"].values()):
            rec["result"] = "DEAD"
        return rec

    # 2. A declared chapter contributed nothing → partial (total>0 hides it).
    empties = empty_chapters(chapter_urls, sections)
    if empties:
        revert(out_path, has_head)
        rec["result"] = "PARTIAL"
        rec["empty_chapters"] = empties
        return rec

    # 3. Shrink / text-collapse vs the committed corpus → REGRESSION. The SAME gate
    #    the interactive puller uses (pull_text._is_regression). --force accepts it
    #    (a genuine recodification that really did remove sections).
    if not force:
        reason = pull_text._is_regression(new_d, old_d)
        if reason:
            revert(out_path, has_head)
            rec["result"] = "REGRESSION"
            rec["reason"] = reason
            return rec

    # 4. Byte-identical to HEAD → nothing fresh was fetched / already current.
    if not file_changed(out_path):
        rec["result"] = "NOCHANGE"
        return rec

    # 5. Healthy real fetch → commit.
    msg = f"data: refresh {profession}/{state} — {prev_n}->{n} sections"
    if force and new_ok < prev_ok:
        msg += " [--force over regression]"
    commit(out_path, msg)
    rec["result"] = "OK"
    rec["per_chapter"] = sections_per_chapter(chapter_urls, sections)
    return rec


# ---------------------------------------------------------------------------
# Worklist assembly (from the frozen profession_index url maps)
# ---------------------------------------------------------------------------
def _rows_for(index: dict, state: str) -> list[dict]:
    rows = []
    for node in index.get("by_state", {}).get(state, {}).get("matched", []):
        rows.append({
            "state": state,
            "chapter_url": node["url"],
            "chapter_label": node.get("label", ""),
            "chapter_slug": node.get("slug", ""),
            **({"section_slug_pattern": node["section_slug_pattern"]}
               if node.get("section_slug_pattern") else {}),
            **({"section_url_list": node["section_url_list"]}
               if node.get("section_url_list") else {}),
            **({"pa_keep_sections": node["pa_keep_sections"]}
               if node.get("pa_keep_sections") else {}),
        })
    return rows


def build_worklist(professions: list[str], only_states: set[str]) -> list[tuple[str, str, list[dict]]]:
    """(profession, state, rows) for every mapped state. Uses the FROZEN index as
    the url source of truth."""
    work: list[tuple[str, str, list[dict]]] = []
    for prof in professions:
        idx_path = PROFESSION_INDEX_DIR / f"{prof}.json"
        if not idx_path.exists():
            continue
        index = json.loads(idx_path.read_text())
        for state in sorted(index.get("by_state", {})):
            if only_states and state not in only_states:
                continue
            rows = _rows_for(index, state)
            if rows:
                work.append((prof, state, rows))
    return work


def all_professions() -> list[str]:
    return sorted(p.stem for p in PROFESSION_INDEX_DIR.glob("*.json"))


# ---------------------------------------------------------------------------
# Year-over-year diff report (recodification detection + held-back review)
# ---------------------------------------------------------------------------
def _chapter_counts(corpus: dict) -> dict[str, int]:
    """Section count keyed by canonical CHAPTER path, derived from section urls
    (so it works whether or not chapter_urls is present). A section's chapter is
    its canonical path minus the leaf section segment."""
    c: collections.Counter = collections.Counter()
    for sec in corpus.get("sections") or []:
        cp = _canon_path(sec.get("url", ""))
        chap = cp[:-1] if len(cp) > 1 else cp
        c["/".join(chap)] += 1
    return dict(c)


def diff_one(old: dict | None, new: dict) -> dict:
    """Compare a pre-refresh corpus to the post-refresh corpus. Returns a record
    with the section-count delta, vanished/appeared chapters, and shrunk chapters."""
    old = old or {}
    old_n = len(old.get("sections") or [])
    new_n = len(new.get("sections") or [])
    old_ch = _chapter_counts(old)
    new_ch = _chapter_counts(new)
    vanished = sorted(k for k in old_ch if k not in new_ch)
    appeared = sorted(k for k in new_ch if k not in old_ch)
    shrunk = []
    for k, ov in old_ch.items():
        nv = new_ch.get(k)
        if nv is not None and ov > 0 and nv < ov * 0.7:  # >30% drop
            shrunk.append({"chapter": k, "old": ov, "new": nv})
    return {
        "old_sections": old_n, "new_sections": new_n, "delta": new_n - old_n,
        "vanished_chapters": vanished, "appeared_chapters": appeared,
        "shrunk_chapters": shrunk, "note": None,
    }


def classify(diff: dict) -> str:
    """Severity bucket for one committed (prof, state) diff."""
    if diff["vanished_chapters"]:
        return "likely recodification (chapter vanished)"
    if diff["shrunk_chapters"]:
        return "suspicious shrink (chapter dropped >30%)"
    if diff["delta"] > 0 or diff["appeared_chapters"]:
        return "grew"
    if diff["delta"] < 0:
        return "minor delta"
    return "no change"


# Held-back buckets sort first (they need action), then the committed-diff buckets.
_SEVERITY_ORDER = list(HELD_SEVERITY.values()) + [
    "likely recodification (chapter vanished)",
    "suspicious shrink (chapter dropped >30%)",
    "grew",
    "minor delta",
    "no change",
]


def render_diff_report(rows: list[dict], run_id: str) -> str:
    """rows: [{profession, state, diff, severity}]. Markdown grouped by severity."""
    buckets: dict[str, list[dict]] = collections.defaultdict(list)
    for r in rows:
        buckets[r["severity"]].append(r)
    lines = [f"# Refresh diff report — {run_id}", "",
             "Year-over-year comparison of each re-pulled corpus against its "
             "pre-refresh committed version. **Held back** rows were NOT committed "
             "(empty/partial/regression — needs action). **Likely recodification** "
             "rows (a chapter present last year is absent now) need human eyes.", ""]
    for sev in _SEVERITY_ORDER:
        rs = buckets.get(sev)
        if not rs:
            continue
        lines.append(f"## {sev} ({len(rs)})")
        lines.append("")
        for r in sorted(rs, key=lambda x: (x["profession"], x["state"])):
            d = r["diff"]
            lines.append(f"- **{r['profession']}/{r['state']}**: "
                         f"{d['old_sections']} → {d['new_sections']} sections "
                         f"(Δ{d['delta']:+d})")
            if d.get("note"):
                lines.append(f"    - {d['note']}")
            for ch in d["vanished_chapters"]:
                lines.append(f"    - VANISHED chapter: `{ch}`")
            for ch in d["appeared_chapters"]:
                lines.append(f"    - appeared chapter: `{ch}`")
            for sh in d["shrunk_chapters"]:
                lines.append(f"    - shrank: `{sh['chapter']}` {sh['old']} → {sh['new']}")
        lines.append("")
    return "\n".join(lines)


def _held_note(item: dict) -> str | None:
    """A one-line reason for a held-back item, for the diff report."""
    if item.get("reason"):
        return item["reason"]
    if item.get("empty_chapters"):
        return "empty chapters: " + ", ".join(item["empty_chapters"])
    if item.get("url_health"):
        return "url health: " + ", ".join(f"{u} → {v}" for u, v in item["url_health"].items())
    return None


def write_diff_report(status: dict, run_id: str) -> Path:
    """Build docs/reports/refresh_diff_<run_id>.md from a status dict. Committed
    items (OK/NOCHANGE) are diffed prior-vs-current; held-back items (reverted, so
    on-disk == prior) are surfaced from their recorded prev/new counts so they're
    still visible."""
    rows = []
    for _key, item in status.get("items", {}).items():
        prof, state = item["profession"], item["state"]
        result = item.get("result")
        if result in HELD_SEVERITY:
            prev, new = item.get("prev", 0), item.get("new", 0)
            diff = {"old_sections": prev, "new_sections": new, "delta": new - prev,
                    "vanished_chapters": [], "appeared_chapters": [],
                    "shrunk_chapters": [], "note": _held_note(item)}
            rows.append({"profession": prof, "state": state, "diff": diff,
                         "severity": HELD_SEVERITY[result]})
            continue
        cur_path = TEXT_DIR / prof / f"{state}.json"
        if not cur_path.exists():
            continue
        new_corpus = json.loads(cur_path.read_text())
        prior = item.get("prior_snapshot")  # captured BEFORE committing
        diff = diff_one(prior, new_corpus)
        rows.append({"profession": prof, "state": state, "diff": diff,
                     "severity": classify(diff)})
    out = ROOT / "docs" / "reports" / f"refresh_diff_{run_id}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_diff_report(rows, run_id))
    return out


# ---------------------------------------------------------------------------
# Status file
# ---------------------------------------------------------------------------
def _status_path(run_id: str | None) -> Path:
    if run_id:
        return RESULTS_DIR / f"refresh_status_{run_id}.json"
    return RESULTS_DIR / ".refresh_status.json"


def _load_prior_status(status_path: Path) -> dict | None:
    """The status file from a previous run of this run-id, for --resume."""
    if not status_path.exists():
        return None
    try:
        return json.loads(status_path.read_text())
    except json.JSONDecodeError:
        return None


# Results that mean "this cell is done — don't re-fetch it on --resume". A failure
# or held-back result is NOT settled, so a resume re-attempts it (a transient block
# may have cleared, or a mapping was fixed).
_SETTLED = {"OK", "NOCHANGE"}


def _fmt_eta(seconds: float) -> str:
    if seconds < 90:
        return f"~{int(seconds)}s"
    if seconds < 5400:
        return f"~{int(seconds / 60)}m"
    return f"~{seconds / 3600:.1f}h"


def _print_summary(status: dict) -> None:
    """A plain-English end-of-run summary to the terminal — readable without
    opening the markdown report. Printed on every exit path (complete or abort)."""
    items = status.get("items", {})
    by = collections.Counter(i.get("result") for i in items.values())
    held = sorted(k for k, i in items.items() if i.get("result") in HELD_SEVERITY)
    print("\n" + "=" * 64)
    print(f"Refresh summary — run {status.get('run_id') or 'latest'}")
    print(f"  {len(items)} corpora checked")
    print(f"  {by.get('NOCHANGE', 0)} unchanged")
    print(f"  {by.get('OK', 0)} updated (committed)")
    if held:
        print(f"  {len(held)} held back — need your review:")
        for k in held:
            i = items[k]
            detail = i.get("reason") or (
                "empty chapters: " + ", ".join(i["empty_chapters"])
                if i.get("empty_chapters") else "")
            line = f"      {i['profession']}/{i['state']}  [{i['result']}]"
            print(line + (f" — {detail}" if detail else ""))
    if status.get("aborted"):
        print(f"  ABORTED: {status['aborted']}")
        print("  (fix the cause, then re-run the SAME command with --resume to continue)")
    if status.get("diff_report"):
        print(f"  full report: {status['diff_report']}")
    print("=" * 64)


# ---------------------------------------------------------------------------
# Run loop
# ---------------------------------------------------------------------------
def run(professions: list[str], only_states: set[str], *, force: bool, cap: int | None,
        timeout_s: int, breaker: int, run_id: str | None, resume: bool = False,
        chrome_check=justia_reachable) -> dict:
    status: dict = {"started": _now(), "run_id": run_id, "items": {}}
    status_path = _status_path(run_id)

    # --resume: carry forward the prior run's results and skip cells already SETTLED
    # (OK/NOCHANGE) so a long run that aborted (breaker/timeout/Ctrl-C) picks up where
    # it left off. Failures/held-back cells are re-attempted (not in `settled`).
    settled: set[str] = set()
    if resume:
        prior = _load_prior_status(status_path)
        if prior:
            status["items"] = prior.get("items", {})
            settled = {k for k, i in status["items"].items()
                       if i.get("result") in _SETTLED}
            print(f"resume: {len(settled)} cell(s) already done — skipping; "
                  f"re-attempting failures + not-yet-done cells")
        else:
            print(f"resume: no prior status at {status_path} — starting fresh")

    def _save():
        status_path.parent.mkdir(parents=True, exist_ok=True)
        status_path.write_text(json.dumps(status, indent=2))

    def _finalize():
        """Write the diff report and record its path. Called on EVERY exit path
        that attempted work (normal end, breaker, timeout) so committed shrinks and
        held-back items are always surfaced — never lost because the run aborted."""
        status.setdefault("finished", _now())
        _save()
        report = write_diff_report(status, run_id or "latest")
        status["diff_report"] = str(report)
        _save()
        return report

    _save()
    if not chrome_check():
        status["aborted"] = ("source not reachable — a startup Justia fetch failed "
                             "(Scrapling installed? network up?); nothing attempted")
        _save()
        print("ABORT: startup Justia fetch failed — Scrapling not clearing Cloudflare or network down")
        _print_summary(status)
        return status

    work = build_worklist(professions, only_states)
    attempt_total = sum(1 for (p, s, _r) in work if f"{p}:{s}" not in settled)
    attempt_done = 0
    t0 = time.time()
    tally: collections.Counter = collections.Counter()
    consec_fail = 0

    for prof, state, rows in work:
        key = f"{prof}:{state}"
        if key in settled:
            continue  # --resume: already done, don't re-fetch
        # Capture the pre-refresh HEAD snapshot BEFORE the item commits, so the
        # diff report compares against last year's committed corpus.
        prior = prior_committed(TEXT_DIR / prof / f"{state}.json")
        try:
            rec = refresh_item(prof, state, rows, force=force, cap=cap, timeout_s=timeout_s)
        except _ItemTimeout as e:
            # Can't kill the worker thread; abort the whole run cleanly so the orphan
            # can't race the next pull on the shared Scrapling session. The process
            # exits after this returns and the daemon dies with it. Re-run with
            # --resume to continue.
            rec = {"profession": prof, "state": state, "result": "TIMEOUT",
                   "reason": str(e), "prev": 0, "new": 0, "at": _now(),
                   "prior_snapshot": prior}
            status["items"][key] = rec
            status["aborted"] = f"item timeout at {key} — {e}; run aborted (re-run with --resume)"
            print("ABORT: item timeout —", status["aborted"])
            _finalize()
            _print_summary(status)
            return status

        rec["prior_snapshot"] = prior
        status["items"][key] = rec
        _save()

        # Live progress: one line per cell + a rolling tally + rough ETA. Skipped
        # (resumed) cells are near-instant, so ETA is based on cells actually pulled.
        attempt_done += 1
        tally[rec["result"]] += 1
        elapsed = time.time() - t0
        eta = _fmt_eta((elapsed / attempt_done) * (attempt_total - attempt_done))
        held = sum(tally[r] for r in HELD_SEVERITY)
        print(f"[{attempt_done}/{attempt_total}] {key} → {rec['result']}  "
              f"| {tally['NOCHANGE']} unchanged, {tally['OK']} updated, "
              f"{held} held-back · {eta} left")

        if rec["result"] in FETCH_FAILURE:
            consec_fail += 1
        else:
            consec_fail = 0
        if consec_fail >= breaker:
            status["aborted"] = (f"{breaker} consecutive fetch failures ending at {key} "
                                 f"— the fetcher is likely wedged (Cloudflare/Scrapling); aborting")
            print("ABORT: circuit breaker tripped —", status["aborted"])
            _finalize()
            _print_summary(status)
            return status

    _finalize()
    _print_summary(status)
    return status


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--profession", help="Profession key (e.g. 'medicine').")
    ap.add_argument("--all-professions", action="store_true",
                    help="Refresh every profession that has a frozen index.")
    ap.add_argument("--states", default="",
                    help="Comma-separated subset (e.g. CA,IN); empty = all mapped states.")
    ap.add_argument("--force", action="store_true",
                    help="Accept a REGRESSION (a pull with fewer/collapsed sections than the "
                         "committed corpus) — use for a genuine recodification. The per-chapter "
                         "and empty-pull gates still apply.")
    ap.add_argument("--report-only", action="store_true",
                    help="Do NOT fetch. Rebuild the diff report from the last status file.")
    ap.add_argument("--resume", action="store_true",
                    help="Continue a prior run of this --run-id: skip cells already done "
                         "(OK/NOCHANGE), re-attempt failures + not-yet-done cells. Use after "
                         "a breaker/timeout abort or Ctrl-C on a long --all-professions run.")
    ap.add_argument("--run-id", default=None,
                    help="Run id (used in the status filename + diff-report filename). "
                         "Defaults to a UTC timestamp for a real run. Pass a STABLE id "
                         "(e.g. --run-id 2026) so --resume can find the prior status.")
    ap.add_argument("--item-timeout", type=int, default=2400,
                    help="Per-item wall-clock timeout in seconds (default %(default)s).")
    ap.add_argument("--breaker", type=int, default=3,
                    help="Abort after N consecutive FETCH FAILURES (empty/dead) — a wedged "
                         "fetcher, not unchanged corpora (default %(default)s).")
    args = ap.parse_args(argv)

    if args.all_professions:
        professions = all_professions()
    elif args.profession:
        professions = [args.profession.lower()]
    else:
        ap.error("one of --profession or --all-professions is required")

    only_states = {s.strip().upper() for s in args.states.split(",") if s.strip()}

    if args.report_only:
        run_id = args.run_id or "latest"
        status_path = _status_path(args.run_id)
        if not status_path.exists():
            sys.exit(f"--report-only: no status file at {status_path} — run a refresh first")
        status = json.loads(status_path.read_text())
        report = write_diff_report(status, run_id)
        print(f"diff report written: {report}")
        return

    # A fresh run gets a timestamp run-id; a --resume run without an explicit id
    # falls back to the default status file (_status_path(None)) so it finds the
    # prior run instead of minting a new, empty one.
    if args.run_id:
        run_id = args.run_id
    elif args.resume:
        run_id = None
    else:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run(professions, only_states, force=args.force, cap=None,
        timeout_s=args.item_timeout, breaker=args.breaker, run_id=run_id,
        resume=args.resume)


if __name__ == "__main__":
    main()

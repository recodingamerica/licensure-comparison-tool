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
import re
import subprocess
import sys
import threading
import queue
import time
import urllib.parse
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import logging

try:
    from tqdm import tqdm as _tqdm
except ImportError:  # optional — falls back to one line per cell
    _tqdm = None

from pipeline.paths import RESULTS_DIR, PROFESSION_INDEX_DIR, TEXT_DIR, LOGS_DIR
from pipeline import provenance
from pipeline.ingest import pull_text
from pipeline.ingest import nj_flat
from pipeline.ingest import clean_text
from pipeline.config.loaders import all_profession_ids, matched_for

ROOT = Path(__file__).resolve().parents[2]

# The terminal channel for the operator-facing progress/summary lines. Held
# separately from sys.stdout so we can redirect the noisy fetch logs + browser
# teardown tracebacks to a file (see _route_noise_to_log) while progress still
# prints to the real terminal. Reset in main().
_OUT = sys.stdout
_LOG_FH = None  # kept alive for the whole process so atexit-time noise still lands in the log


def _emit(msg: str = "") -> None:
    """Write one operator-facing line to the terminal (bypasses log-file routing)."""
    print(msg, file=_OUT, flush=True)


def _route_noise_to_log(log_path: Path) -> None:
    """Send the verbose per-fetch logs + browser-teardown tracebacks to `log_path`
    and keep the terminal to progress/summary only (via _emit). pull_text installs
    a terminal StreamHandler on the root logger at import, and scrapling/asyncio log
    fetch chatter + greenlet/TargetClosedError teardown noise there — none of which
    an operator needs to see. Effects last for the process so even atexit-time
    session-teardown noise lands in the file, not the terminal. `--verbose` skips
    this entirely."""
    global _LOG_FH
    log_path.parent.mkdir(parents=True, exist_ok=True)
    _LOG_FH = open(log_path, "a", buffering=1)
    handler = logging.StreamHandler(_LOG_FH)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    for h in list(root.handlers):            # drop pull_text's terminal StreamHandler
        root.removeHandler(h)
    root.addHandler(handler)
    scr = logging.getLogger("scrapling")     # scrapling installs its own console handler
    for h in list(scr.handlers):
        scr.removeHandler(h)
    scr.propagate = True                     # route it through root -> the log file
    # Catch direct stdout/stderr writes (scrapling banners, greenlet/atexit tracebacks).
    sys.stdout = _LOG_FH
    sys.stderr = _LOG_FH


class _Progress:
    """Per-cell progress display. On a real terminal (with tqdm) it's a single
    in-place bar with a rolling tally + ETA, and any non-NOCHANGE cell is written
    as a persistent line ABOVE the bar so breaks stay visible. When output isn't a
    terminal (piped / backgrounded, or tqdm missing) it degrades to one clean line
    per cell — good for a log file. `use_bar` is decided in main() (quiet mode +
    a TTY)."""

    def __init__(self, total: int, use_bar: bool):
        self.total = total
        self.done = 0
        self.t0 = time.time()
        self.bar = _tqdm(total=total, unit="cell", file=_OUT, leave=True,
                         dynamic_ncols=True) if (use_bar and _tqdm is not None) else None

    def update(self, key: str, result: str, tally: "collections.Counter", held: int) -> None:
        self.done += 1
        counts = f"{tally['NOCHANGE']} unchanged, {tally['OK']} updated, {held} held"
        if self.bar is not None:
            if result != "NOCHANGE":
                # file=_OUT: tqdm.write defaults to sys.stdout (redirected to the log
                # in quiet mode) — send it to the same stream as the bar (the terminal).
                self.bar.write(f"  {key} → {result}", file=_OUT)   # persists above the bar
            self.bar.set_postfix_str(counts)
            self.bar.update(1)
        else:
            elapsed = time.time() - self.t0
            eta = _fmt_eta((elapsed / self.done) * (self.total - self.done))
            _emit(f"[{self.done}/{self.total}] {key} → {result}  | {counts} · {eta} left")

    def close(self) -> None:
        if self.bar is not None:
            self.bar.close()

# Only a genuine FETCH FAILURE (nothing usable came back) advances the circuit
# breaker — a consecutive run of these means the fetcher is wedged and the rest
# of the worklist would waste time. NOCHANGE (statute unchanged), a committed OK,
# and the held-back PARTIAL/REGRESSION all got a real response, so they RESET the
# breaker. This is why a normal annual refresh — where most states are unchanged
# NOCHANGE — no longer trips the breaker on the 3rd unchanged state.
FETCH_FAILURE = {"EMPTY", "DEAD", "NOFILE", "TIMEOUT"}

# Retry a deficient pull (fetch errors, or fewer error-free sections than the
# committed corpus) this many extra times before believing the shortfall is real —
# absorbs transient Cloudflare flakiness that drops a section or a page mid-run.
PULL_RETRIES = 2

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
    # This precheck fetch created the Scrapling session in THIS (main) thread; tear it
    # down so the pull worker thread opens its own. Otherwise the worker's first fetch
    # inherits a main-thread session and crosses threads, burning a retry to recover
    # (see _PullThread).
    pull_text._reset_scrapling_session()
    return status == 200 and err is None


# ---------------------------------------------------------------------------
# git helpers (per-item commit; never `git add -A`)
# ---------------------------------------------------------------------------
def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def _rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def same_corpus_content(new_d: dict, old_d: dict) -> bool:
    """True iff two corpora carry the same statute CONTENT — the load-bearing
    projection of each section (url/label/citation/text/error), not raw JSON bytes.

    We compare content, not bytes, on purpose: `StateCorpus` gains fields over time
    (e.g. `source_unavailable`), so a corpus last written before a field was added
    re-serializes byte-differently even when the statute is untouched. A raw git
    diff would treat that as "changed" and re-commit thousands of no-op updates on
    the annual run, defeating the NOCHANGE/updated distinction the breaker + resume
    rely on. An untracked cell (old_d empty) has no baseline, so it's never a match."""
    def _proj(d: dict) -> list[tuple]:
        return [
            (s.get("url"), s.get("label"), s.get("citation"), s.get("text"), s.get("error"))
            for s in (d.get("sections") or [])
        ]
    return bool(old_d) and _proj(new_d) == _proj(old_d)


def _cleaned_for_compare(d: dict) -> dict:
    """A shallow corpus copy whose section `text` is run through clean_text's source
    cleaner (nav/version/annotation furniture stripped) and whose char fields are
    recomputed to match — used ONLY for change-detection, never written to disk.

    The raw text/ corpus is always full of source furniture that clean_text strips
    downstream (version-nav year lists, disclaimers, the Colorado annotation
    apparatus). Diffing/guarding on RAW text therefore can't tell a real amendment
    from pure nav churn (Justia adding a "2025" version line) or new template chrome,
    so `_obviously_legit` would auto-commit furniture as if it were statute. Comparing
    CLEANED text makes those non-changes read as NOCHANGE. Found 2026-07-18 when a CO
    re-pull auto-committed annotation-template chrome across 9 cells."""
    if not d:
        return d
    out = dict(d)
    secs = []
    total = 0
    for s in d.get("sections") or []:
        s2 = dict(s)
        if not s2.get("error"):
            txt = clean_text.cleaner_for(s2.get("url") or "")(s2.get("text") or "")
            s2["text"] = txt
            s2["text_len"] = len(txt)
            total += len(txt)
        secs.append(s2)
    out["sections"] = secs
    out["total_chars"] = total
    return out


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


def _stage_pull_stamp(profession: str, state: str) -> None:
    """Right before an OK pull commits its corpus, git-add this cell's pull-provenance stamp
    so the corpus and its freshness stamp land in ONE commit. pull's freshness key is the
    frozen profession-index url-map (not the corpus bytes), so a cell already current needs
    nothing — the guard skips it. Only a first-time or remapped cell records here; the
    one-time `provenance backfill-pull` baselines every pre-existing corpus (and a NOCHANGE
    pull, which by definition already had a committed corpus, is covered by that baseline —
    so only OK pulls stamp)."""
    if provenance.check("pull", profession, state) == "current":
        return
    stamp_path = provenance.record("pull", profession, state)
    _git("add", _rel(stamp_path))


PENDING_DIR = RESULTS_DIR / "pending_review"


def stage_pending(run_id: str | None, profession: str, state: str,
                  new_corpus: dict, rec: dict) -> None:
    """Save a HELD candidate pull for human review instead of discarding it outright.

    Writes results/pending_review/<run-id>/<prof>__<state>.json with the new corpus, the
    hold reason, and the old/new counts, so `refresh_corpus review` can render old-vs-new
    and `refresh_corpus apply` can commit an approved change WITHOUT re-fetching. No-op when
    run_id is unset (an ad-hoc single pull). The committed corpus is never touched here —
    this is a side artifact the run can leave for a person to act on later."""
    if not run_id:
        return
    d = PENDING_DIR / run_id
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{profession}__{state}.json").write_text(json.dumps({
        "profession": profession, "state": state,
        "result": rec.get("result"), "reason": rec.get("reason", ""),
        "prev": rec.get("prev"), "new": rec.get("new"),
        "staged_at": _now(),
        "new_corpus": new_corpus,
    }, indent=2))


def _cite(s: dict) -> str:
    return str(s.get("citation") or s.get("id") or s.get("label") or s.get("url", "?"))


def _chapter_sig(cite: str) -> str:
    """The chapter-level part of a section citation (drop the trailing section number), used
    to tell a same-chapter renumber/amendment from a wrong-chapter swap or whole-title pull.
    '11-110-103'->'11-110'  '43-12-1'->'43-12'  '501.001'->'501'  'NRS 683A.020'->'NRS 683A'."""
    return re.sub(r"[.\-]\d+(?:\.\d+)?\s*$", "", str(cite)).strip() or str(cite)


def _obviously_legit(new_d: dict, old_d: dict) -> bool:
    """True iff a held (REGRESSION-flagged) change is safe to AUTO-ACCEPT without human
    review — a legit amendment/renumbering rather than a bad pull. All four must hold:
      * new has >= the committed error-free section count (didn't SHRINK — a shrink could be
        a partial fetch or a repeal, which we surface for review),
      * new has >= ~the committed char volume (didn't COLLAPSE),
      * new has NO error sections (clean fetch), and
      * the new pull's CHAPTER set == the committed one (no wrong-chapter swap, no
        whole-title over-pull, no dropped chapter).
    money_transmitter/CO (28->47, same article-110, clean) passes; a shrink / chapter-swap /
    collapse / partial does not."""
    new_secs = new_d.get("sections") or []
    old_secs = old_d.get("sections") or []
    new_ok = [s for s in new_secs if not s.get("error")]
    old_ok = [s for s in old_secs if not s.get("error")]
    if not old_ok or len(new_ok) < len(old_ok):
        return False
    if any(s.get("error") for s in new_secs):          # a clean fetch has no error sections
        return False
    # chars from section TEXT directly (not the total_chars field, which may be unset/stale)
    new_chars = sum(len(s.get("text") or "") for s in new_ok)
    old_chars = sum(len(s.get("text") or "") for s in old_ok)
    if new_chars < old_chars * 0.9:                    # text collapsed -> review
        return False
    new_sigs = {_chapter_sig(_cite(s)) for s in new_ok}
    old_sigs = {_chapter_sig(_cite(s)) for s in old_ok}
    return bool(new_sigs) and new_sigs == old_sigs


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
    # NJ (and any flat-layout state) nests sections directly under the title as
    # section-<title>-<token>-…, which does NOT prefix-match its …/chapter-<token>/
    # url. Without this, every flat section is left unattributed and each mapped NJ
    # chapter is falsely flagged empty → the whole multi-chapter cell is held PARTIAL
    # forever though the pull was healthy. Match flat sections by their slug token.
    flat = {u: nj_flat.section_slug_re(k)
            for u in chapter_urls if (k := nj_flat.key_from_chapter_url(u))}
    # Longest chapter path first so a section under a nested chapter is attributed
    # to the deepest matching chapter, not a shallow ancestor.
    ordered = sorted(chapter_urls, key=lambda u: len(canon[u]), reverse=True)
    for sec in sections:
        surl = sec.get("url", "")
        sp = _canon_path(surl)
        slug = sp[-1] if sp else ""
        for u in ordered:
            cp = canon[u]
            if len(sp) >= len(cp) and sp[:len(cp)] == cp:
                counts[u] += 1
                break
            if u in flat and flat[u].match(slug):
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


class _PullThread:
    """One long-lived worker thread that runs EVERY pull_state call, so the thread-
    affine Scrapling/Playwright session is created and reused in a single thread.

    The old design spawned a fresh daemon thread per cell, which cached the session in
    the first cell's thread and then touched it from later cells' threads whose
    predecessor had exited → `greenlet.error: cannot switch to a different thread (which
    happens to have exited)`, crashing (or burning ~75s recreating) on every cell after
    the first. A single worker keeps the session put.

    Timeout is enforced by the caller waiting on the result queue. A timed-out task
    leaves this thread busy — but the run loop aborts the WHOLE run on _ItemTimeout, so
    the process exits and this daemon dies, exactly as the old per-cell daemon did."""

    def __init__(self):
        self._jobs: "queue.Queue" = queue.Queue()
        self._results: "queue.Queue" = queue.Queue()
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while True:
            state, profession, rows, cap = self._jobs.get()
            try:
                self._results.put(("ok", pull_text.pull_state(state, profession, rows, cap)))
            except BaseException as e:  # noqa: BLE001 — surfaced in the caller thread
                self._results.put(("err", e))

    def run(self, state, profession, rows, cap, timeout_s):
        self._jobs.put((state, profession, rows, cap))
        try:
            kind, val = self._results.get(timeout=timeout_s)
        except queue.Empty:
            raise _ItemTimeout(f"pull_state exceeded {timeout_s}s wall clock (genuine hang)")
        if kind == "err":
            raise val
        return val


_PULL_THREAD: _PullThread | None = None


def pull_with_timeout(state: str, profession: str, rows: list[dict],
                      cap: int | None, timeout_s: int):
    """Run pull_text.pull_state under a wall-clock timeout, in a SINGLE persistent worker
    thread so the thread-affine Scrapling session stays in one thread (see _PullThread).
    Raises _ItemTimeout on hang, or the original exception otherwise."""
    global _PULL_THREAD
    if _PULL_THREAD is None:
        _PULL_THREAD = _PullThread()
    try:
        return _PULL_THREAD.run(state, profession, rows, cap, timeout_s)
    except _ItemTimeout:
        # The worker is wedged on the timed-out task (we can't kill it). Orphan it AND its
        # thread-affine Scrapling session — it's a daemon, dies at process exit — so the
        # next call gets a fresh worker + session instead of inheriting the stale result or
        # a cross-thread session. (Production aborts the whole run on timeout anyway; this
        # keeps correctness if it ever doesn't.) Same recycle as the fetch-failure path.
        recycle_pull_worker()
        raise


def recycle_pull_worker() -> None:
    """Orphan the persistent pull worker so the NEXT cell opens a fresh thread + fresh
    Scrapling session.

    A mid-cell session reset (`_reset_scrapling_session` on a retry) in the worker thread
    can leave that thread's Playwright event loop in a state where the next sync fetch
    raises `It looks like you are using Playwright Sync API inside the asyncio loop`.
    That wedged session then turns EVERY subsequent cell EMPTY — a false cascade that
    trips the circuit breaker (observed on KY: a cell that pulls fine in isolation comes
    back EMPTY mid-run). A fresh worker thread starts with clean asyncio state, so
    recycling after a fetch failure lets the run recover instead of aborting. The old
    daemon thread is abandoned and dies at process exit.

    Crucially this also orphans pull_text's module-level `_SCRAPLING_SESSION`: that global
    is created inside the old worker thread, so a fresh worker that reused it would touch a
    thread-affine session from the wrong thread → `greenlet.error: Cannot switch to a
    different thread`. Null it (WITHOUT closing — closing from this thread hits the same
    greenlet error) so the fresh worker opens its own session in its own thread; the old
    session leaks until the abandoned daemon dies at process exit."""
    global _PULL_THREAD
    _PULL_THREAD = None
    pull_text._SCRAPLING_SESSION = None


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
                 force: bool, cap: int | None, timeout_s: int,
                 run_id: str | None = None) -> dict:
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

    # Pull, retrying a DEFICIENT result — a pull with fetch errors, or with fewer
    # error-free sections than the committed corpus — up to PULL_RETRIES times.
    # Transient Cloudflare flakiness can drop a section or a whole page mid-run;
    # a retry usually gets it. Keep the most complete attempt. A clean pull that
    # already meets the committed count stops immediately (no wasted fetches); a
    # genuinely-shrunk corpus just re-confirms across retries, then the content-
    # aware regression gate (below) decides renumbering vs real removal.
    new_d = None
    new_ok = -1
    attempts = 0
    for _attempt in range(PULL_RETRIES + 1):
        attempts += 1
        corpus = pull_with_timeout(state, profession, rows, cap, timeout_s)
        cand = asdict(corpus)
        cand_ok = pull_text._corpus_health(cand)[0]
        if new_d is None or cand_ok > new_ok:
            new_d, new_ok = cand, cand_ok
        errored = sum(1 for s in (cand.get("sections") or []) if s.get("error"))
        # Retry only a BROKEN pull — one with fetch errors, or a totally empty one.
        # A clean, non-empty pull is authoritative: re-fetching returns the same
        # section list, so a shortfall vs the committed corpus is judged by the
        # content-aware regression gate (renumber vs real removal), NOT by burning
        # 2 more full re-pulls. The rare clean-but-truncated transient is recovered
        # by --resume instead. (Retrying clean short pulls made the annual run ~3x
        # slower on every genuine removal — found by the WY whole-state run.)
        if errored == 0 and cand_ok > 0:
            break

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(new_d, indent=2))
    sections = new_d.get("sections") or []
    n = len(sections)

    rec: dict = {"profession": profession, "state": state, "prev": prev_n, "new": n,
                 "prev_ok": prev_ok, "new_ok": new_ok, "attempts": attempts, "at": _now()}

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

    # Change-detection compares CLEANED text (nav/version/annotation furniture
    # stripped), NOT the raw pull — else Justia nav churn (a new version-list year)
    # or the Colorado annotation template reads as a statute change. See
    # _cleaned_for_compare. The RAW new_d is still what gets committed to text/.
    new_cmp = _cleaned_for_compare(new_d)
    old_cmp = _cleaned_for_compare(old_d)

    # 3. Shrink / text-collapse vs the committed corpus → REGRESSION. The SAME gate
    #    the interactive puller uses (pull_text._is_regression). --force accepts it
    #    (a genuine recodification that really did remove sections).
    if not force:
        reason = pull_text._is_regression(new_cmp, old_cmp)
        if reason and not _obviously_legit(new_cmp, old_cmp):
            rec["result"] = "REGRESSION"
            rec["reason"] = reason
            stage_pending(run_id, profession, state, new_d, rec)  # keep the candidate for review
            revert(out_path, has_head)
            return rec
        if reason:
            # A clean, same-chapter, non-shrinking change (amendment / renumbering, e.g.
            # money_transmitter/CO 28->47) — the whole point of the annual refresh is to take
            # these. Auto-accept it instead of parking it for review; the ambiguous cases
            # (shrink / chapter-swap / collapse / partial) still get held above.
            rec["auto_accepted"] = reason

    # 4. Same statute content as HEAD (ignoring serialization / schema drift like a
    #    new null field, AND source furniture churn) → nothing substantive changed.
    #    Discard the rewrite so an unchanged statute isn't re-committed on the annual run.
    if same_corpus_content(new_cmp, old_cmp):
        revert(out_path, has_head)
        rec["result"] = "NOCHANGE"
        return rec

    # 5. Healthy real fetch → commit.
    msg = f"data: refresh {profession}/{state} — {prev_n}->{n} sections"
    if force and new_ok < prev_ok:
        msg += " [--force over regression]"
    elif rec.get("auto_accepted"):
        msg += " [auto-accepted: clean same-chapter change]"
    _stage_pull_stamp(profession, state)   # fold this cell's pull-provenance into the commit
    commit(out_path, msg)
    rec["result"] = "OK"
    rec["per_chapter"] = sections_per_chapter(chapter_urls, sections)
    return rec


# ---------------------------------------------------------------------------
# Worklist assembly (from the frozen profession_index url maps)
# ---------------------------------------------------------------------------
def _rows_for(index: dict, state: str) -> list[dict]:
    rows = []
    for node in matched_for(index, state):
        # A node flagged `source_unavailable` is an ACCEPTED gap: the profession is
        # regulated but its text isn't on Justia/PA (e.g. an admin-code-only regime),
        # so the mapped url is only a general hook that yields 0 fields. Refreshing it
        # re-fetches a page that can't help — and for a big general title (Oklahoma
        # Title 2 for public_weighmaster) the fetch can hang past the item timeout and
        # abort the whole annual run. Skip these; if a state's only nodes are all
        # source_unavailable, _rows_for returns [] and build_worklist drops the cell.
        if node.get("source_unavailable"):
            continue
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
    return all_profession_ids()


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


def _estimate_seconds(work: list) -> float:
    """A rough wall-clock estimate for a worklist: ~2.5s per section fetch + ~4s
    per-cell overhead, from committed section counts (a cell with no committed
    corpus assumes ~20 sections). Deliberately a loose upper-ish guess so the
    operator knows the order of magnitude before starting."""
    sections = 0
    for prof, state, _rows in work:
        try:
            n = len(json.loads((TEXT_DIR / prof / f"{state}.json").read_text()).get("sections") or [])
        except OSError:
            n = 0
        sections += n or 20
    return sections * 2.5 + len(work) * 4


def _print_summary(status: dict) -> None:
    """A plain-English end-of-run summary — shown on the terminal AND written to
    pipeline/logs/refresh_<run_id>_summary.txt so it survives closing the terminal
    (the walk-away-and-come-back case). Printed on every exit path."""
    items = status.get("items", {})
    by = collections.Counter(i.get("result") for i in items.values())
    held = sorted(k for k, i in items.items() if i.get("result") in HELD_SEVERITY)
    lines = ["=" * 64,
             f"Refresh summary — run {status.get('run_id') or 'latest'}",
             f"  {len(items)} corpora checked",
             f"  {by.get('NOCHANGE', 0)} unchanged",
             f"  {by.get('OK', 0)} updated (committed)"]
    if held:
        lines.append(f"  {len(held)} held back — need your review:")
        for k in held:
            i = items[k]
            detail = i.get("reason") or (
                "empty chapters: " + ", ".join(i["empty_chapters"])
                if i.get("empty_chapters") else "")
            lines.append(f"      {i['profession']}/{i['state']}  [{i['result']}]"
                         + (f" — {detail}" if detail else ""))
        lines.append("  (held-back cells were NOT changed — your committed data is untouched. To")
        lines.append("   accept a real recodification, re-run that ONE occupation with --force.)")
    if by.get("OK", 0):
        lines.append(f"  {by['OK']} update(s) are individual git commits — undo any one with "
                     f"`git revert <sha>` (git log pipeline/results/text/).")
    if status.get("aborted"):
        lines.append(f"  ABORTED: {status['aborted']}")
        lines.append("  (fix the cause, then re-run the SAME command with --resume to continue)")
    if status.get("diff_report"):
        lines.append(f"  full report: {status['diff_report']}")
    lines.append("=" * 64)

    _emit("")
    for ln in lines:
        _emit(ln)
    try:
        p = LOGS_DIR / f"refresh_{status.get('run_id') or 'latest'}_summary.txt"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("\n".join(lines) + "\n")
    except OSError:
        pass  # a summary file is a convenience; never fail the run over it


# ---------------------------------------------------------------------------
# Run loop
# ---------------------------------------------------------------------------
def run(professions: list[str], only_states: set[str], *, force: bool, cap: int | None,
        timeout_s: int, breaker: int, run_id: str | None, resume: bool = False,
        skip_held: bool = False,
        progress_bar: bool = False, chrome_check=justia_reachable) -> dict:
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
            skip_results = _SETTLED | set(HELD_SEVERITY) if skip_held else _SETTLED
            settled = {k for k, i in status["items"].items()
                       if i.get("result") in skip_results}
            n_held = sum(1 for i in status["items"].values()
                         if i.get("result") in HELD_SEVERITY)
            extra = (f" (incl. {n_held} previously-held, kept in run-state for review)"
                     if skip_held else "")
            _emit(f"resume: {len(settled)} cell(s) already done — skipping{extra}; "
                  f"re-attempting {'not-yet-done cells' if skip_held else 'failures + not-yet-done cells'}")
        else:
            _emit(f"resume: no prior status at {status_path} — starting fresh")

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
        _emit("ABORT: startup Justia fetch failed — Scrapling not clearing Cloudflare or network down")
        _print_summary(status)
        return status

    work = build_worklist(professions, only_states)
    attempt_total = sum(1 for (p, s, _r) in work if f"{p}:{s}" not in settled)
    _emit(f"Refreshing {attempt_total} cell(s)…")
    tally: collections.Counter = collections.Counter()
    consec_fail = 0
    progress = _Progress(attempt_total, progress_bar)

    for prof, state, rows in work:
        key = f"{prof}:{state}"
        if key in settled:
            continue  # --resume: already done, don't re-fetch
        # Capture the pre-refresh HEAD snapshot BEFORE the item commits, so the
        # diff report compares against last year's committed corpus.
        prior = prior_committed(TEXT_DIR / prof / f"{state}.json")
        try:
            rec = refresh_item(prof, state, rows, force=force, cap=cap, timeout_s=timeout_s,
                               run_id=run_id)
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
            progress.close()
            _emit(f"ABORT: item timeout — {status['aborted']}")
            _finalize()
            _print_summary(status)
            return status

        rec["prior_snapshot"] = prior
        status["items"][key] = rec
        _save()

        # Live progress: a bar on a terminal, else one line per cell. Skipped
        # (resumed) cells are near-instant, so ETA is based on cells actually pulled.
        tally[rec["result"]] += 1
        held = sum(tally[r] for r in HELD_SEVERITY)
        progress.update(key, rec["result"], tally, held)

        if rec["result"] in FETCH_FAILURE:
            consec_fail += 1
            # A fetch failure can mean the worker's Scrapling session is wedged (a
            # Playwright sync/asyncio-loop breakage after a mid-cell reset), which would
            # otherwise turn every following cell EMPTY and trip the breaker on healthy
            # states. Give the next cell a fresh worker+session so a genuinely-empty cell
            # stays empty but a wedged-session cell recovers. See recycle_pull_worker.
            recycle_pull_worker()
        else:
            consec_fail = 0
        if consec_fail >= breaker:
            status["aborted"] = (f"{breaker} consecutive fetch failures ending at {key} "
                                 f"— the fetcher is likely wedged (Cloudflare/Scrapling); aborting")
            progress.close()
            _emit(f"ABORT: circuit breaker tripped — {status['aborted']}")
            _finalize()
            _print_summary(status)
            return status

    progress.close()
    _finalize()
    _print_summary(status)
    return status


def _remaining_to_attempt(status: dict, professions: list[str],
                          only_states: set[str]) -> int:
    """Cells in the worklist not yet settled OK/NOCHANGE or held back — i.e. the
    ones a --skip-held resume would still try. 0 means the run has converged."""
    skip = _SETTLED | set(HELD_SEVERITY)
    done = {k for k, i in status.get("items", {}).items() if i.get("result") in skip}
    work = build_worklist(professions, only_states)
    return sum(1 for p, s, _r in work if f"{p}:{s}" not in done)


def run_until_done(professions: list[str], only_states: set[str], *,
                   timeout_s: int, breaker: int, run_id: str | None,
                   max_passes: int = 120, progress_bar: bool = False) -> dict:
    """Auto-relaunch `run()` (as --resume --skip-held) until the worklist is fully
    settled or a pass makes no progress. A single hung cell hits --item-timeout and
    aborts the whole run by design; each relaunch --skip-held skips that cell (and
    every other already-held one), so the loop advances and converges. This is the
    in-process replacement for the external annual-refresh watchdog: bounded by
    max_passes and progress-guarded so it can't hot-loop."""
    status: dict = {}
    prev_remaining: int | None = None
    for i in range(1, max_passes + 1):
        status = run(professions, only_states, force=False, cap=None,
                     timeout_s=timeout_s, breaker=breaker, run_id=run_id,
                     resume=True, skip_held=True, progress_bar=progress_bar)
        rem = _remaining_to_attempt(status, professions, only_states)
        _emit(f"until-done: pass {i} finished — {rem} cell(s) still to attempt")
        if rem <= 0:
            _emit("until-done: COMPLETE — nothing left to attempt")
            return status
        # No-progress guard: if a full pass settled nothing new, every remaining cell
        # is stuck (re-held or re-failing). Stop rather than relaunch forever.
        if prev_remaining is not None and rem >= prev_remaining:
            _emit(f"until-done: NO PROGRESS ({prev_remaining} -> {rem}) — stopping to avoid a loop")
            return status
        prev_remaining = rem
    _emit(f"until-done: hit max-passes={max_passes} — stopping ({prev_remaining} still to attempt)")
    return status


# ---------------------------------------------------------------------------
# Review + approve of held (candidate) changes
# ---------------------------------------------------------------------------
def _load_pending(run_id: str) -> list[dict]:
    d = PENDING_DIR / run_id
    if not d.exists():
        return []
    out = []
    for f in sorted(d.glob("*__*.json")):
        try:
            out.append(json.loads(f.read_text()))
        except json.JSONDecodeError:
            continue
    return out


def _section_diff(new_corpus: dict, prof: str, state: str) -> dict:
    """old-vs-new citation sets + a few text samples + an action verdict, for the review page.

    The verdict buckets a held candidate on the same citation-overlap signal the gate keys on:
      FETCH_FLAKE — candidate has fetch errors, or shares <30% of the committed citations
                    (wrong page / different article / truncation) → RE-PULL; committed is fine.
      GROWTH      — kept ~all committed citations AND added more: a more complete pull the
                    gate rejected over-conservatively → ACCEPT.
      CHANGE      — high overlap, a few sections dropped: real repeal or transient → re-pull
                    to confirm, accept if the drop is stable.
    """
    old = prior_committed(TEXT_DIR / prof / f"{state}.json") or {}
    old_secs = {_cite(s): s for s in (old.get("sections") or [])}
    new_secs = {_cite(s): s for s in (new_corpus.get("sections") or [])}
    removed = [c for c in old_secs if c not in new_secs]
    added = [c for c in new_secs if c not in old_secs]

    # Verdict on ERROR-FREE citations only (what's actually usable). A committed corpus can
    # carry errored/junk sections that inflate its all-section count and make a CLEANER
    # candidate look like a shrink; comparing usable citations avoids that.
    old_ok = {_cite(s) for s in (old.get("sections") or []) if not s.get("error") and _cite(s)}
    new_ok = {_cite(s) for s in (new_corpus.get("sections") or []) if not s.get("error") and _cite(s)}
    overlap = len(old_ok & new_ok) / len(old_ok) if old_ok else 0.0
    errs = sum(1 for s in (new_corpus.get("sections") or []) if s.get("error"))
    if errs or overlap < 0.30:
        verdict, hint = "FETCH_FLAKE", "re-pull — wrong page/truncated; committed corpus is fine"
    elif overlap >= 0.90 and len(new_ok) > len(old_ok):
        verdict, hint = "GROWTH", "accept — candidate is a more complete pull"
    else:
        verdict, hint = "CHANGE", "re-pull to confirm; accept if the drop is stable"

    return {
        "removed": removed, "added": added, "verdict": verdict, "verdict_hint": hint,
        "removed_samples": [(c, (old_secs[c].get("label") or "")[:70],
                             (old_secs[c].get("text") or "")[:220]) for c in removed[:6]],
        "added_samples": [(c, (new_secs[c].get("label") or "")[:70],
                           (new_secs[c].get("text") or "")[:220]) for c in added[:6]],
    }


def build_review_html(run_id: str) -> Path:
    """Self-contained HTML review page for a run's HELD candidate pulls: per cell it shows
    why it was held, old->new counts, the exact sections added / removed, and text samples,
    with an Accept checkbox. Checking cells live-builds the copy-paste `apply` command. No
    server, no download round-trip — same offline pattern as client/dashboard.py."""
    import html as _html
    pend = _load_pending(run_id)
    out = PENDING_DIR / run_id / "review.html"
    cards = []
    # Compute each held cell's diff+verdict, then group by verdict (GROWTH first — the
    # accept-these — then flakes, then changes) so the reviewer works top-down.
    scored = [(p, _section_diff(p.get("new_corpus") or {}, p["profession"], p["state"])) for p in pend]
    _ORDER = {"GROWTH": 0, "FETCH_FLAKE": 1, "CHANGE": 2}
    scored.sort(key=lambda pd: (_ORDER.get(pd[1]["verdict"], 9), pd[0]["profession"], pd[0]["state"]))
    _VCLASS = {"GROWTH": "v-growth", "FETCH_FLAKE": "v-flake", "CHANGE": "v-change"}
    for p, diff in scored:
        prof, state = p["profession"], p["state"]
        key = f"{prof}:{state}"
        def _samples(rows, cls):
            return "".join(
                f'<div class="s {cls}"><b>{_html.escape(c)}</b> {_html.escape(lab)}'
                f'<div class="t">{_html.escape(txt)}</div></div>' for c, lab, txt in rows) or "<i>none</i>"
        cards.append(f"""
        <div class="card">
          <label class="hd"><input type="checkbox" class="acc" data-key="{_html.escape(key)}">
            <span class="k">{_html.escape(key)}</span>
            <span class="vbadge {_VCLASS[diff['verdict']]}">{diff['verdict']}</span>
            <span class="badge">{_html.escape(str(p.get('result')))}</span>
            <span class="cnt">{p.get('prev')} &rarr; {p.get('new')} sections</span></label>
          <div class="why"><b>{_html.escape(diff['verdict_hint'])}</b> &middot; {_html.escape(str(p.get('reason') or ''))}</div>
          <div class="cols">
            <div><h4>Removed vs committed ({len(diff['removed'])})</h4>{_samples(diff['removed_samples'],'rm')}</div>
            <div><h4>Added in new pull ({len(diff['added'])})</h4>{_samples(diff['added_samples'],'ad')}</div>
          </div>
        </div>""")
    body = "".join(cards) or "<p>No held cells for this run — nothing to review. 🎉</p>"
    page = f"""<!doctype html><meta charset=utf-8><title>Refresh review — {_html.escape(run_id)}</title>
<style>
body{{font:14px/1.5 -apple-system,system-ui,sans-serif;max-width:1000px;margin:24px auto;padding:0 16px;color:#1a1a1a}}
h1{{font-size:20px}} .card{{border:1px solid #ddd;border-radius:8px;padding:12px 14px;margin:12px 0}}
.hd{{display:flex;align-items:center;gap:10px;cursor:pointer;font-weight:600}}
.badge{{background:#fde68a;border-radius:4px;padding:1px 7px;font-size:12px}}
.vbadge{{border-radius:4px;padding:1px 7px;font-size:12px;font-weight:700;color:#fff}}
.v-growth{{background:#16a34a}} .v-flake{{background:#dc2626}} .v-change{{background:#d97706}}
.cnt{{color:#555;font-weight:400}} .why{{color:#666;font-size:13px;margin:4px 0 8px}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
h4{{margin:6px 0;font-size:13px}} .s{{border-left:3px solid #ccc;padding:2px 8px;margin:4px 0;font-size:12px}}
.s.rm{{border-color:#ef4444;background:#fef2f2}} .s.ad{{border-color:#22c55e;background:#f0fdf4}}
.t{{color:#555;margin-top:2px;white-space:pre-wrap}} #bar{{position:sticky;top:0;background:#fff;padding:10px 0;border-bottom:1px solid #eee}}
code{{background:#f4f4f5;padding:8px;display:block;border-radius:6px;white-space:pre-wrap;word-break:break-all}}
</style>
<h1>Annual-refresh review — <code style="display:inline">{_html.escape(run_id)}</code></h1>
<p>Each card is a change the refresh <b>held</b> (did not commit). Check the ones that are legitimate updates,
then copy the command below and run it to accept them. Unchecked cells stay as they are.</p>
<div id=bar><b>To accept the checked changes, run:</b><code id=cmd>(check some boxes)</code></div>
{body}
<script>
function upd(){{
  const ks=[...document.querySelectorAll('.acc:checked')].map(c=>c.dataset.key);
  document.getElementById('cmd').textContent = ks.length
    ? 'pipeline/.venv/bin/python -m pipeline.ingest.refresh_corpus --apply --run-id {_html.escape(run_id)} --accept '+ks.join(',')
    : '(check some boxes)';
}}
document.addEventListener('change',e=>{{if(e.target.classList.contains('acc'))upd();}});
</script>"""
    out.write_text(page)
    return out


def apply_pending(run_id: str, accept: set[str]) -> None:
    """Commit the approved held candidates (no re-fetch): write each staged new_corpus into
    the corpus tree and commit it. Cells not in `accept` are left untouched (still held)."""
    pend = _load_pending(run_id)
    by_key = {f"{p['profession']}:{p['state']}": p for p in pend}
    unknown = accept - set(by_key)
    if unknown:
        _emit(f"WARN: not in this run's held set (ignored): {', '.join(sorted(unknown))}")
    applied = 0
    for key in sorted(accept & set(by_key)):
        p = by_key[key]
        prof, state = p["profession"], p["state"]
        out_path = TEXT_DIR / prof / f"{state}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(p["new_corpus"], indent=2))
        commit(out_path, f"data: accept reviewed refresh {prof}/{state} — "
                         f"{p.get('prev')}->{p.get('new')} sections [reviewed:{run_id}]")
        (PENDING_DIR / run_id / f"{prof}__{state}.json").unlink(missing_ok=True)
        _emit(f"  accepted {key}: {p.get('prev')}->{p.get('new')} sections (committed)")
        applied += 1
    _emit(f"applied {applied} reviewed change(s); {len(by_key) - applied} left held. "
          f"Re-run clean->trim->extract for accepted cells before republishing.")


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
                         "committed corpus) — use for a genuine recodification. Scoped on "
                         "purpose: cannot be combined with --all-professions, so accepting a "
                         "shrink is always a deliberate, one-occupation act. The per-chapter "
                         "and empty-pull gates still apply.")
    ap.add_argument("--report-only", action="store_true",
                    help="Do NOT fetch. Rebuild the diff report from the last status file.")
    ap.add_argument("--review", action="store_true",
                    help="Do NOT fetch. Build an offline HTML page (pending_review/<run-id>/"
                         "review.html) to review the run's HELD candidate changes and pick "
                         "which to accept. Requires --run-id.")
    ap.add_argument("--apply", action="store_true",
                    help="Do NOT fetch. Commit the reviewed candidates named in --accept "
                         "(no re-fetch). Requires --run-id + --accept.")
    ap.add_argument("--accept", default="",
                    help="With --apply: comma-separated prof:STATE keys to accept "
                         "(e.g. money_transmitter:CO,psychology:TX).")
    ap.add_argument("--resume", action="store_true",
                    help="Continue a prior run of this --run-id: skip cells already done "
                         "(OK/NOCHANGE), re-attempt failures + not-yet-done cells. Use after "
                         "a breaker/timeout abort or Ctrl-C on a long --all-professions run.")
    ap.add_argument("--until-done", action="store_true",
                    help="Auto-relaunch (implies --resume --skip-held) after each "
                         "breaker/timeout abort until every cell is settled or a pass "
                         "makes no progress. Bounded by --max-passes. Replaces the "
                         "external annual-refresh watchdog loop.")
    ap.add_argument("--max-passes", type=int, default=120,
                    help="With --until-done: max relaunch passes before giving up (default 120).")
    ap.add_argument("--skip-held", action="store_true",
                    help="With --resume: ALSO skip cells already held back "
                         "(REGRESSION/EMPTY/PARTIAL/DEAD/TIMEOUT/NOFILE) instead of "
                         "re-attempting them, so the run goes straight to not-yet-done "
                         "cells. The held results stay in the run-state for the review pass.")
    ap.add_argument("--run-id", default=None,
                    help="Run id (used in the status filename + diff-report filename). "
                         "Defaults to a UTC timestamp for a real run. Pass a STABLE id "
                         "(e.g. --run-id 2026) so --resume can find the prior status.")
    ap.add_argument("--item-timeout", type=int, default=2400,
                    help="Per-item wall-clock timeout in seconds (default %(default)s).")
    ap.add_argument("--breaker", type=int, default=3,
                    help="Abort after N consecutive FETCH FAILURES (empty/dead) — a wedged "
                         "fetcher, not unchanged corpora (default %(default)s).")
    ap.add_argument("--verbose", action="store_true",
                    help="Show the raw per-fetch logs and browser teardown noise on the "
                         "terminal. Default: only progress + summary show; the detail goes "
                         "to a log file (its path is printed at the end).")
    ap.add_argument("--yes", action="store_true",
                    help="Skip the 'proceed?' confirmation shown before a big "
                         "--all-professions run.")
    args = ap.parse_args(argv)

    # Review / apply modes short-circuit before any fetch (they only touch pending_review).
    if args.review:
        if not args.run_id:
            ap.error("--review requires --run-id (the run whose held cells you want to review)")
        n = len(_load_pending(args.run_id))
        page = build_review_html(args.run_id)
        _emit(f"review page for {n} held cell(s): {page}\n  open it in a browser, check the "
              f"legitimate changes, then run the command it shows.")
        return
    if args.apply:
        if not args.run_id or not args.accept:
            ap.error("--apply requires --run-id and --accept prof:STATE,prof:STATE")
        apply_pending(args.run_id, {k.strip() for k in args.accept.split(",") if k.strip()})
        return

    if args.all_professions:
        professions = all_professions()
    elif args.profession:
        professions = [args.profession.lower()]
    else:
        ap.error("one of --profession or --all-professions is required")

    # Safety: --force overrides the shrink guard, so it can't be a blanket override
    # across a whole annual run. Accepting a recodification must be a deliberate,
    # one-occupation act (git still records each change as a revertible commit).
    if args.force and args.all_professions:
        ap.error("--force cannot be combined with --all-professions — accept a shrink one "
                 "occupation at a time, e.g. --profession X --states Y --force")

    only_states = {s.strip().upper() for s in args.states.split(",") if s.strip()}

    if args.report_only:
        run_id = args.run_id or "latest"
        status_path = _status_path(args.run_id)
        if not status_path.exists():
            sys.exit(f"--report-only: no status file at {status_path} — run a refresh first")
        status = json.loads(status_path.read_text())
        report = write_diff_report(status, run_id)
        _emit(f"diff report written: {report}")
        return

    # A fresh run gets a timestamp run-id; a --resume run without an explicit id
    # falls back to the default status file (_status_path(None)) so it finds the
    # prior run instead of minting a new, empty one.
    if args.run_id:
        run_id = args.run_id
    elif args.resume or args.until_done:
        run_id = None
    else:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # Big annual run: show scope + a rough time estimate and confirm, so a
    # non-expert operator knows the commitment. Interactive + --all-professions
    # only — scoped/scripted runs (refetch.sh, gap_pull.sh) proceed without a prompt.
    if args.all_professions and not args.yes and sys.stdin.isatty():
        work = build_worklist(professions, only_states)
        if not work:
            sys.exit("nothing to refresh for that scope")
        est = _fmt_eta(_estimate_seconds(work))
        resp = input(f"About to refresh {len(work)} cell(s) across {len(professions)} "
                     f"occupations — roughly {est} of live fetching. It's safe to stop "
                     f"and re-run with --resume. Proceed? [y/N] ")
        if resp.strip().lower() not in ("y", "yes"):
            print("Aborted — nothing fetched.")
            return

    # Quiet by default: route the noisy fetch logs + teardown tracebacks to a file
    # and keep the terminal to progress + summary. --verbose leaves them on screen.
    global _OUT
    _OUT = sys.stdout
    # A live progress bar only when the terminal is real AND we're not interleaving
    # raw logs on it (--verbose) — otherwise fall back to one line per cell.
    use_bar = (not args.verbose) and _OUT.isatty() and (_tqdm is not None)
    log_path = LOGS_DIR / f"refresh_{run_id or 'latest'}.log"
    if not args.verbose:
        _route_noise_to_log(log_path)

    if args.until_done:
        run_until_done(professions, only_states, timeout_s=args.item_timeout,
                       breaker=args.breaker, run_id=run_id,
                       max_passes=args.max_passes, progress_bar=use_bar)
    else:
        run(professions, only_states, force=args.force, cap=None,
            timeout_s=args.item_timeout, breaker=args.breaker, run_id=run_id,
            resume=args.resume, skip_held=args.skip_held, progress_bar=use_bar)

    if not args.verbose:
        _emit(f"  detailed fetch log: {log_path}")


if __name__ == "__main__":
    main()

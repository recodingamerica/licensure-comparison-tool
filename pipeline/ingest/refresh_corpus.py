"""Durable annual Justia re-pull — the tested replacement for the throwaway
`.scratch/overnight_repull.py` and the `_cdp_*` batch drivers.

`refresh_corpus` re-pulls the FROZEN url map (results/profession_index/<prof>.json)
for the annual refresh and the Utah handoff. It reuses pull_text's fetching
(`pull_state`) — it does NOT reimplement fetching — and wraps it in the hardening
learned during the 2026-07-02 CDP re-pull (docs/runbooks/cdp_repull_lessons_2026-07-02.md):

  * a Chrome-live precheck over CDP (the endpoint /json/version lies);
  * PER-CHAPTER completeness validation — the no-wipe guard is all-or-nothing, so a
    chapter that came back EMPTY (total>0 but one declared chapter has 0 sections) is
    a partial and must NOT be committed;
  * real-fetch detection via `git diff --quiet` — an unchanged file after a --force
    re-pull means nothing was fetched (Chrome down/wedged), not success;
  * mid-run CDP-death resilience — a pull that raises a connection error re-checks
    Chrome; if it recovered, retry the item ONCE; if still dead, abort loudly;
  * a per-item wall-clock timeout so a genuine hang can't wedge the run forever;
  * a circuit breaker — N consecutive non-productive results aborts the run;
  * per-item commits (never `git add -A`), the message naming prof/state + old→new counts;
  * a year-over-year DIFF REPORT (docs/reports/refresh_diff_<runid>.md) flagging
    vanished chapters (recodification) for human review.

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
import urllib.parse
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from pipeline.paths import RESULTS_DIR, PROFESSION_INDEX_DIR, TEXT_DIR
from pipeline.ingest import pull_text

ROOT = Path(__file__).resolve().parents[2]
CDP_URL = "http://127.0.0.1:9222"
# A genuinely productive result resets the circuit breaker.
FRESH = {"OK"}


# ---------------------------------------------------------------------------
# Chrome liveness (ported from .scratch/overnight_repull.py::_chrome_live)
# ---------------------------------------------------------------------------
def chrome_live(cdp_url: str = CDP_URL) -> bool:
    """Can we open a Justia page over CDP and clear the Cloudflare challenge?

    The /json/version endpoint is unreliable while a pull drives the browser and
    can respond even in a bad post-update state, so probe via a real
    connect_over_cdp + new_page + goto instead."""
    try:
        from playwright.sync_api import sync_playwright
        import time
        with sync_playwright() as pw:
            b = pw.chromium.connect_over_cdp(cdp_url, timeout=8000)
            page = b.contexts[0].new_page()
            page.goto("https://law.justia.com/codes/kansas/", timeout=45000)
            time.sleep(5)
            ok = "moment" not in (page.title() or "").lower()
            page.close()
            return ok
    except Exception:
        return False


# ---------------------------------------------------------------------------
# git helpers (per-item commit; never `git add -A`)
# ---------------------------------------------------------------------------
def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def _rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def file_changed(path: Path) -> bool:
    """True if `path` differs from its committed (HEAD) version. A re-pull of an
    incomplete corpus MUST change the file; unchanged = the pull was a no-op
    (Chrome down -> fetch failed -> no-wipe guard kept the old cache).

    `git diff --quiet` silently ignores UNTRACKED files (exit 0 = "no
    differences" even when the file is packed with brand-new real content) --
    it only compares tracked paths against the index/HEAD. This tool was built
    for re-pulling an ALREADY-COMMITTED corpus (the annual recodification-check
    use case), so that blind spot never mattered until it was pointed at a
    genuinely NEW (profession, state) pair with no prior commit: every real,
    successful fetch got misclassified NOCHANGE and silently discarded (see
    docs/runbooks/cdp_repull_lessons_2026-07-09.md). An untracked file with any
    content IS the change -- there's no baseline for git to diff against.
    """
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


def revert(path: Path) -> None:
    _git("checkout", "--", _rel(path))


def commit(path: Path, msg: str) -> None:
    _git("add", _rel(path))
    _git("commit", "-q", "-m", msg,
         "-m", "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>")


# ---------------------------------------------------------------------------
# Per-chapter completeness (the GAP FIX)
# ---------------------------------------------------------------------------
def _canon_path(url: str) -> tuple[str, ...]:
    """Path segments with Justia year segments stripped, so a section under a
    year-versioned snapshot still maps to its unversioned chapter."""
    segs = [s for s in urllib.parse.urlparse(url).path.split("/") if s]
    return tuple(s for s in segs if not pull_text.YEAR_SEG.match(s))


def sections_per_chapter(chapter_urls: list[str], sections: list[dict]) -> dict[str, int]:
    """Attribute each section to one of the mapped chapters and count.

    Justia sections share the chapter's canonical path prefix, so prefix-match.
    Official-source states rewrite section URLs onto a different host (they won't
    prefix-match the Justia chapter url); when there is exactly one mapped chapter
    every section belongs to it, which covers that case. With multiple chapters
    and non-prefixing urls a section is left unattributed — it still counts toward
    the total but not toward any one chapter, which correctly keeps a genuinely
    empty chapter flagged."""
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


class _CDPDead(Exception):
    """Raised when a pull error looks like Chrome/CDP died mid-run."""


_CDP_ERR_MARKERS = (
    "cdp", "connect_over_cdp", "websocket", "target closed", "browser has been closed",
    "connection closed", "connection refused", "disconnected", "ECONNREFUSED".lower(),
)


def _looks_like_cdp_death(exc: Exception) -> bool:
    s = f"{type(exc).__name__}: {exc}".lower()
    return any(m in s for m in _CDP_ERR_MARKERS)


def pull_with_timeout(state: str, profession: str, rows: list[dict],
                      cap: int | None, timeout_s: int):
    """Run pull_text.pull_state under a wall-clock timeout. Returns the corpus.
    Raises _ItemTimeout on hang, _CDPDead on a CDP/connection error, or the
    original exception otherwise."""
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
        err = result["error"]
        if _looks_like_cdp_death(err):
            raise _CDPDead(str(err)) from err
        raise err
    return result["corpus"]


# ---------------------------------------------------------------------------
# The per-item refresh
# ---------------------------------------------------------------------------
def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _classify_empty(chapter_urls: list[str]) -> dict[str, str]:
    """When a pull comes back with 0 sections, probe each mapped chapter url to
    say WHY it's empty: a dead/stub LINK (go find a new one — the url form is
    wrong) vs a LIVE page that simply had no matching sections (a scoping /
    section_slug_pattern miss). LLM-free; only runs on the rare EMPTY path so it
    adds no cost to the happy path. Turns a silent EMPTY into an actionable one."""
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
                 chrome_check=chrome_live) -> dict:
    """Re-pull one (profession, state), validate, commit iff clean.

    Returns a status record with a `result` in:
      OK           — real fetch, every chapter populated, committed
      PARTIAL      — a mapped chapter came back empty; reverted, NOT committed
      NOCHANGE     — file unchanged after the re-pull (nothing fetched / already complete)
      DEAD         — 0 sections AND a mapped chapter url probes DEAD_404/STUB (the
                     link is wrong — go find a new one); reverted. `url_health`
                     carries the per-url verdict.
      EMPTY        — 0 sections but the chapter urls are LIVE (a scoping / pattern
                     miss, not a dead link); reverted. `url_health` set.
      NOFILE       — the corpus file never appeared
    On mid-run CDP death that doesn't recover, raises _CDPDead (the run loop aborts).
    """
    out_path = TEXT_DIR / profession / f"{state}.json"
    chapter_urls = [r["chapter_url"] for r in rows]
    prior = prior_committed(out_path)
    prev_n = len((prior or {}).get("sections") or [])

    # Attempt the pull; on CDP death, re-check Chrome and retry ONCE.
    try:
        corpus = pull_with_timeout(state, profession, rows, cap, timeout_s)
    except _CDPDead:
        if not chrome_check():
            raise  # Chrome really gone — let the run loop abort loudly
        corpus = pull_with_timeout(state, profession, rows, cap, timeout_s)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(asdict(corpus), indent=2))
    d = json.loads(out_path.read_text())
    sections = d.get("sections") or []
    n = len(sections)

    rec: dict = {"profession": profession, "state": state,
                 "prev": prev_n, "new": n, "at": _now()}

    if n == 0:
        revert(out_path)
        rec["result"] = "EMPTY"
        # Say WHY it's empty: a dead link (find a new url) vs a live page with no
        # matching sections. If any chapter url is a dead/stub link, flag DEAD.
        rec["url_health"] = _classify_empty(chapter_urls)
        if any(v in ("DEAD_404", "STUB") for v in rec["url_health"].values()):
            rec["result"] = "DEAD"
        return rec

    empties = empty_chapters(chapter_urls, sections)
    if empties:
        # Per-chapter partial: total>0 but a declared chapter is empty. The
        # all-or-nothing guard would have committed this — we don't.
        revert(out_path)
        rec["result"] = "PARTIAL"
        rec["empty_chapters"] = empties
        return rec

    if not file_changed(out_path):
        # Non-empty but byte-identical to HEAD => nothing fresh was fetched
        # (Chrome down -> no-wipe guard kept the old cache) OR already complete.
        rec["result"] = "NOCHANGE"
        return rec

    commit(out_path, f"data: refresh {profession}/{state} — {prev_n}->{n} sections")
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
    """(profession, state, rows) for every state that has a committed corpus OR is
    mapped in the index. Uses the FROZEN index as the url source of truth."""
    work: list[tuple[str, str, list[dict]]] = []
    for prof in professions:
        idx_path = PROFESSION_INDEX_DIR / f"{prof}.json"
        if not idx_path.exists():
            continue
        index = json.loads(idx_path.read_text())
        text_dir = TEXT_DIR / prof
        for state in sorted(index.get("by_state", {})):
            if only_states and state not in only_states:
                continue
            rows = _rows_for(index, state)
            if not rows:
                continue
            has_corpus = (text_dir / f"{state}.json").exists()
            # Re-pull anything with an existing corpus or a live mapping.
            if has_corpus or rows:
                work.append((prof, state, rows))
    return work


def all_professions() -> list[str]:
    return sorted(p.stem for p in PROFESSION_INDEX_DIR.glob("*.json"))


# ---------------------------------------------------------------------------
# Year-over-year diff report (recodification detection)
# ---------------------------------------------------------------------------
def _chapter_counts(corpus: dict) -> dict[tuple[str, ...], int]:
    """Section count keyed by canonical CHAPTER path, derived from section urls
    (so it works whether or not chapter_urls is present). A section's chapter is
    its canonical path minus the leaf section segment."""
    c: collections.Counter = collections.Counter()
    for sec in corpus.get("sections") or []:
        cp = _canon_path(sec.get("url", ""))
        # The chapter is the path without the final section segment. Justia
        # chapter urls end at .../chapter-N/ so drop the leaf.
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
        "shrunk_chapters": shrunk,
    }


def classify(diff: dict) -> str:
    """Severity bucket for one (prof, state) diff."""
    if diff["vanished_chapters"]:
        return "likely recodification (chapter vanished)"
    if diff["shrunk_chapters"]:
        return "suspicious shrink (chapter dropped >30%)"
    if diff["delta"] > 0 or diff["appeared_chapters"]:
        return "grew"
    if diff["delta"] < 0:
        return "minor delta"
    return "no change"


_SEVERITY_ORDER = [
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
             "pre-refresh committed version. **Likely recodification** rows "
             "(a chapter present last year is absent now — renumbered/repealed) "
             "need human eyes.", ""]
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
            for ch in d["vanished_chapters"]:
                lines.append(f"    - VANISHED chapter: `{ch}`")
            for ch in d["appeared_chapters"]:
                lines.append(f"    - appeared chapter: `{ch}`")
            for sh in d["shrunk_chapters"]:
                lines.append(f"    - shrank: `{sh['chapter']}` {sh['old']} → {sh['new']}")
        lines.append("")
    return "\n".join(lines)


def write_diff_report(status: dict, run_id: str) -> Path:
    """Build docs/reports/refresh_diff_<run_id>.md from a status dict. For each
    item that recorded a `prior_snapshot` (the pre-commit HEAD corpus) and whose
    corpus now exists, diff prior vs current."""
    rows = []
    for key, item in status.get("items", {}).items():
        prof, state = item["profession"], item["state"]
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


# ---------------------------------------------------------------------------
# Run loop
# ---------------------------------------------------------------------------
def run(professions: list[str], only_states: set[str], *, force: bool, cap: int | None,
        timeout_s: int, breaker: int, run_id: str | None,
        chrome_check=chrome_live) -> dict:
    status: dict = {"started": _now(), "run_id": run_id, "items": {}}
    status_path = _status_path(run_id)

    def _save():
        status_path.parent.mkdir(parents=True, exist_ok=True)
        status_path.write_text(json.dumps(status, indent=2))

    _save()
    if not chrome_check():
        status["aborted"] = "chrome not live/clear at startup — nothing attempted"
        _save()
        print("ABORT: debug Chrome not live on :9222 or Cloudflare-challenged")
        return status

    work = build_worklist(professions, only_states)
    consec_dead = 0
    for prof, state, rows in work:
        key = f"{prof}:{state}"
        # Capture the pre-refresh HEAD snapshot BEFORE the item commits, so the
        # diff report compares against last year's committed corpus.
        prior = prior_committed(TEXT_DIR / prof / f"{state}.json")
        try:
            rec = refresh_item(prof, state, rows, force=force, cap=cap,
                               timeout_s=timeout_s, chrome_check=chrome_check)
        except _CDPDead as e:
            status["aborted"] = (f"CDP death at {key} and Chrome did not recover: {e} "
                                 "— aborting rather than grinding out false results")
            _save()
            print("ABORT:", status["aborted"])
            return status
        rec["prior_snapshot"] = prior
        status["items"][key] = rec
        _save()

        if rec["result"] in FRESH:
            consec_dead = 0
        else:
            consec_dead += 1
        if consec_dead >= breaker:
            status["aborted"] = (f"{breaker} consecutive non-productive results ending "
                                 f"at {key} — Chrome likely died mid-run")
            _save()
            print("ABORT: circuit breaker tripped —", status["aborted"])
            return status

    status["finished"] = _now()
    _save()
    # Post-step: the year-over-year diff report.
    report = write_diff_report(status, run_id or "latest")
    status["diff_report"] = str(report)
    _save()
    print(f"refresh complete — status {status_path}, diff report {report}")
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
                    help="Pass --force semantics to the pull (overwrite the on-disk corpus "
                         "before validation). Validation/commit gates still apply.")
    ap.add_argument("--report-only", action="store_true",
                    help="Do NOT fetch. Rebuild the diff report from the last status file.")
    ap.add_argument("--run-id", default=None,
                    help="Run id (used in the status filename + diff-report filename). "
                         "Defaults to a UTC timestamp for a real run.")
    ap.add_argument("--item-timeout", type=int, default=2400,
                    help="Per-item wall-clock timeout in seconds (default %(default)s).")
    ap.add_argument("--breaker", type=int, default=3,
                    help="Abort after N consecutive non-productive results (default %(default)s).")
    args = ap.parse_args(argv)

    if args.all_professions:
        professions = all_professions()
    elif args.profession:
        professions = [args.profession.lower()]
    else:
        ap.error("one of --profession or --all-professions is required")

    only_states = {s.strip().upper() for s in args.states.split(",") if s.strip()}

    if args.report_only:
        # Pure analysis: reload the last status and regenerate the report.
        run_id = args.run_id or "latest"
        status_path = _status_path(args.run_id)
        if not status_path.exists():
            sys.exit(f"--report-only: no status file at {status_path} — run a refresh first")
        status = json.loads(status_path.read_text())
        report = write_diff_report(status, run_id)
        print(f"diff report written: {report}")
        return

    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run(professions, only_states, force=args.force, cap=None,
        timeout_s=args.item_timeout, breaker=args.breaker, run_id=run_id)


if __name__ == "__main__":
    main()

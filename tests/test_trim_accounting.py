"""Trim must account for every section it was given.

`trim_state` either KEEPS a cleaned section (into `sections`) or DROPS it (into
`dropped`); the apply loop walks `by_cite`, built from the chunk itself, so every input
lands in exactly one of the two. `skipped` is NOT a third bucket — a section with no
model decision, or one in a failed chunk, is recorded there *and* kept, so it is a
subset of `sections` and must not be added again. Hence:

    len(sections) + len(dropped) == len(clean sections)

That invariant did not hold for **69 of 1,456** trimmed cells, from artifacts written by
an older, lossy version of the stage. NV/HVAC recorded 1 kept and 10 dropped against a
162-section corpus: 151 sections gone, with nothing recording them. Re-running the same
input through today's code gives kept=145, dropped=17, skipped=0 — all 162 accounted for.

Nothing caught it, and the shape of the failure is why. Freshness compares each stage's
inputs and recipe hash, so an artifact written by superseded code still reports "current"
unless CODE_VERSION is bumped — and the trims looked fine by every other measure: no
error, no empty file, just a smaller corpus for the model to read. The extractions built
on them were silently working from a fraction of the statute (#118).

This is a conservation check, not a quality one: it says nothing about whether trim kept
the RIGHT sections, only that it didn't lose any without saying so.
"""
import json

import pytest

from pipeline.paths import CLEAN_DIR, TRIMMED_DIR


def _cells():
    """(profession, state, clean_path, trimmed_path) for every trimmed cell that has a
    matching cleaned corpus."""
    if not TRIMMED_DIR.exists():
        return
    for prof_dir in sorted(TRIMMED_DIR.iterdir()):
        if not prof_dir.is_dir():
            continue
        for f in sorted(prof_dir.glob("*.json")):
            if f.name.startswith("_"):
                continue
            clean = CLEAN_DIR / prof_dir.name / f.name
            if clean.exists():
                yield prof_dir.name, f.stem, clean, f


def test_every_cleaned_section_is_accounted_for_after_trim():
    losses = []
    checked = 0
    for prof, state, clean_path, trim_path in _cells():
        try:
            clean = json.loads(clean_path.read_text())
            trimmed = json.loads(trim_path.read_text())
        except (json.JSONDecodeError, OSError):
            continue  # unreadable corpora are a different failure; not this test's job
        n_clean = len(clean.get("sections") or [])
        if not n_clean:
            continue
        # NOT + skipped: those sections are also in `sections` (see module docstring).
        n_accounted = len(trimmed.get("sections") or []) + len(trimmed.get("dropped") or [])
        checked += 1
        if n_accounted != n_clean:
            losses.append((abs(n_clean - n_accounted), prof, state, n_clean, n_accounted))

    assert checked, "no trimmed cells found to check — did the corpus move?"
    losses.sort(reverse=True)
    assert not losses, (
        f"{len(losses)} of {checked} trimmed cells lost sections without recording them "
        f"as dropped or skipped. The model then read a fraction of the statute (#118). "
        f"Re-run `python -m pipeline.ingest.trim_state --profession <p> --states <s>` "
        f"for each, then re-extract.\n  "
        + "\n  ".join(
            f"{prof}/{state}: clean={n_clean} kept+dropped={n_acc} "
            f"({'LOST ' + str(n_clean - n_acc) if n_acc < n_clean else 'EXCESS ' + str(n_acc - n_clean)})"
            for _delta, prof, state, n_clean, n_acc in losses[:15]
        )
        + ("\n  …" if len(losses) > 15 else "")
    )

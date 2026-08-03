"""`--professions` must reject non-professions before spending anything.

2026-08-03: `--professions $PROFS` in zsh passed the whole 13-name list as ONE
argument (zsh does not word-split an unquoted $VAR the way bash does; `$(cat f)`
does split). Nothing validated it, so the run got as far as map_prep and died with
a FileNotFoundError naming a 400-character "profession" — after the fanout stages
had already run. A one-second check at the front replaces that.
"""

from __future__ import annotations

import pytest

import pipeline.publish.refresh_all as ra


def _run(monkeypatch, argv: list[str]):
    monkeypatch.setattr("sys.argv", ["refresh_all", *argv])
    with pytest.raises(SystemExit) as e:
        ra.main()
    return str(e.value)


def test_shell_did_not_split_the_list(monkeypatch):
    """The exact 2026-08-03 failure: one arg containing spaces."""
    msg = _run(monkeypatch, ["--professions", "architecture dentistry hvac", "--dry-run"])
    assert "aren't professions" in msg
    # names the cause, so the reader doesn't go hunting in map_prep
    assert "ONE" in msg and "zsh" in msg


def test_typo_is_rejected(monkeypatch):
    msg = _run(monkeypatch, ["--professions", "dentsitry", "--dry-run"])
    assert "dentsitry" in msg
    # a plain typo should NOT claim the shell mis-split anything
    assert "zsh" not in msg


def test_valid_professions_pass_the_guard(monkeypatch):
    """A real profession must reach the normal --dry-run path, which returns
    rather than exiting — i.e. the guard let it through."""
    known = ra.core_professions()
    monkeypatch.setattr("sys.argv", ["refresh_all", "--professions", known[0], "--dry-run"])
    ra.main()   # no SystemExit

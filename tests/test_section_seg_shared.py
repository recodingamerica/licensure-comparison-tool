"""SECTION_SEG has a single source of truth (_section_patterns), imported by both
the scraping stack (pull_text) and the LLM-free scope walker (_scope_rules) — so the
two can never drift, and the walker still doesn't pull in the scraping deps."""

import subprocess
import sys


def test_pull_text_and_scope_rules_share_the_same_object():
    from pipeline.ingest._section_patterns import SECTION_SEG
    from pipeline.ingest.pull_text import SECTION_SEG as ps
    from pipeline.scope._scope_rules import LEAF_SECTION_SEG as ls
    assert ps is SECTION_SEG          # same object — cannot drift
    assert ls is SECTION_SEG


def test_importing_scope_rules_does_not_drag_in_the_scraping_stack():
    # A fresh interpreter: importing _scope_rules must NOT import curl_cffi/bs4 —
    # that's the whole reason the pattern lives in a dependency-free module.
    code = (
        "import sys; import pipeline.scope._scope_rules; "
        "heavy=[m for m in ('curl_cffi','bs4') if m in sys.modules]; "
        "print('HEAVY:'+','.join(heavy))"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert "HEAVY:" in out.stdout, out.stderr
    assert out.stdout.strip() == "HEAVY:", f"scope walker pulled in scraping deps: {out.stdout}"

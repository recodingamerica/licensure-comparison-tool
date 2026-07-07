"""Source-purity audit — LLM-free, offline, and config-INDEPENDENT.

The bug this catches (2026-07-07): `state_structure.yaml`'s `source:` key is
supposed to be "the single source of truth for which source each state uses,"
but 8 states (CT/ID/ME/RI/SD/VA/VT/WA) kept an active `source: X_official` tag
long after a `chapter_url_template retired 2026-07-01 (Justia-only decision)`
comment noted the actual routing had already moved to Justia. `corpus_drift`
trusts that key to decide which states to skip checking — so it silently
skipped real drift-checks on all 8. A doc-writing pass caught it by hand,
checking actual corpus hosts instead of the config.

This audit is the automated version of that hand-check: it does NOT read
`state_structure.yaml` or any profession_index at all. It just walks every
committed corpus and asserts the one thing this project has decided must
always be true (CLAUDE.md: "everything-except-PA on Justia") — so it can never
be fooled by a stale config, no matter how the config drifts.

ALLOWED_NON_JUSTIA is a short, hand-maintained allowlist (NOT derived from any
config file) — the opposite of the sprawling, easily-stale `source:` keys.
Changing it should be rare and deliberate.

Usage:
  python -m pipeline.eval.source_purity            # scan everything, exit 1 on violation
  python -m pipeline.eval.source_purity --quiet     # print only on violation
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from urllib.parse import urlparse

from pipeline.paths import TEXT_DIR

# Hand-maintained. A state appearing here means "we have deliberately decided
# this state is not on Justia" — verified against CLAUDE.md's own directive,
# not inferred from state_structure.yaml (that's exactly what went stale).
ALLOWED_NON_JUSTIA: dict[str, set[str]] = {
    "PA": {"www.legis.state.pa.us"},
}

JUSTIA_HOST = "law.justia.com"


def scan() -> dict[str, dict[str, Counter]]:
    """(state -> profession -> Counter[unexpected_host]) for every corpus file
    under TEXT_DIR whose sections come from a host other than Justia and not
    covered by ALLOWED_NON_JUSTIA for that state."""
    violations: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
    for f in sorted(TEXT_DIR.glob("*/*.json")):
        prof, stem = f.parent.name, f.stem
        if stem.startswith("_"):
            continue
        st = stem
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        secs = d if isinstance(d, list) else d.get("sections", [])
        allowed = ALLOWED_NON_JUSTIA.get(st, set())
        for sec in secs:
            url = sec.get("url", "") if isinstance(sec, dict) else ""
            if "://" not in url:
                continue
            host = urlparse(url).netloc
            if host != JUSTIA_HOST and host not in allowed:
                violations[st][prof][host] += 1
    return {st: dict(profs) for st, profs in violations.items()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quiet", action="store_true", help="only print on violation")
    args = ap.parse_args()

    violations = scan()
    if not violations:
        if not args.quiet:
            print("source-purity: clean — every corpus except the allowlisted "
                  f"exceptions ({', '.join(ALLOWED_NON_JUSTIA)}) is on Justia.")
        return 0

    print(f"source-purity: {len(violations)} state(s) with unexpected non-Justia sections:")
    for st in sorted(violations):
        for prof, hosts in sorted(violations[st].items()):
            print(f"  {st}/{prof}: {dict(hosts)}")
    print("\nEach of these is either a genuinely new non-Justia source (update "
          "ALLOWED_NON_JUSTIA deliberately) or a re-pull that regressed onto an "
          "old official-source path (re-pull from Justia).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

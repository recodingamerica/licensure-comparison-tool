"""Trim audit: scan dropped sections across all professions/states for any
whose LABELS contain licensure-relevant keywords. Flags potential false drops
that warrant a human (or LLM) second look.

The trim_state output already records each dropped section with its label
and reason. This script doesn't need to re-fetch anything.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TRIMMED_DIR = REPO_ROOT / "pipeline" / "results" / "trimmed"

# Patterns that strongly suggest a section IS substantive licensure / scope
# content, not administrative. Each pattern is a regex matched case-insensitively
# against the section label only. The keyword scan from v1 was too noisy —
# "license" appears in "Notice of Hearing Before Revocation of License", which
# is procedural. Tighter patterns target the substance: "license required",
# "scope of practice", "continuing education", etc.
import re as _re

_SUBSTANTIVE_PATTERNS = [
    _re.compile(p, _re.IGNORECASE) for p in [
        r"\bscope of (practice|the profession)\b",
        r"\b(licens(e|ure))\s+(required|necessary|without|prohibit|exemption|prerequisite)\b",
        r"\bpractic(e|ing)\s+(without|requires?|prohibit|defined?|defined? as)\b",
        r"\bunauthorized\s+practice\b",
        r"\bunlicensed\s+practice\b",
        r"\b(qualifications?|requirements?)\s+(for|to)\s+(licens|practic|examin|registrat)\b",
        r"\bexamination(s)?\s*(required|subjects|content|topics)?\s*$",
        r"\b(continuing|professional)\s+education\b",
        r"\breciprocity\b",
        r"\bendorsement\b",
        r"\beducation(al)?\s+(requirements?|qualifications?|standards?)\b",
        r"\b(residency|internship|post.?graduate)\s+(required|requirements?|training)\b",
        r"\brenewal\s+(of\s+)?(licens|certif|registrat)",
        r"\b(title|name)\s+(protection|restricted|may.?not\s+be\s+used)",
        r"\bgrounds?\s+for\s+discipline\b",
        r"\bdefinitions?\s*$",  # the chapter's definitions section
        r"\bage\s+(requirement|minimum)\b",
        r"\bmoral\s+character\b",
        r"\bfee\s+(structure|amount|of|payment)",  # not "fee schedule" which is admin
    ]
]

# Patterns that should NEVER be flagged as suspicious — strongly administrative
_ADMIN_PATTERNS = [
    _re.compile(p, _re.IGNORECASE) for p in [
        r"\bnotice of hearing\b",
        r"\brecords? to be kept\b",
        r"\bfee schedule\b",
        r"\bappointment\s+and\s+qualifications\b",  # board members
        r"\bmember(s)?\s*[-—–:]?\s*qualifications?\b",
        r"\bcompensation\s+of\s+members\b",
        r"\bshort\s+title\b",
        r"\boath\s+of\s+(office|board)\b",
        r"\bministerial\b",
        r"\blegislative\s+findings?\b",
        r"\beffective\s+date\b",
        r"\b(repealed|reserved)\b",
        r"\bcaption(s)?\b",
        r"\bseverability\b",
    ]
]


def classify(label: str) -> tuple[bool, list[str]]:
    """Return (is_substantive, matched_pattern_descriptions)."""
    # Hard exclusions first
    for p in _ADMIN_PATTERNS:
        if p.search(label):
            return False, []
    matched = [p.pattern for p in _SUBSTANTIVE_PATTERNS if p.search(label)]
    return bool(matched), matched


def is_suspicious(label: str) -> list[str]:
    sus, matched = classify(label)
    return matched if sus else []


def main() -> None:
    rows: list[dict] = []
    for prof_dir in sorted(TRIMMED_DIR.iterdir()):
        if not prof_dir.is_dir():
            continue
        for f in sorted(prof_dir.glob("*.json")):
            if f.name.startswith("_"):
                continue
            d = json.loads(f.read_text())
            state = d.get("state", "?")
            for sec in d.get("dropped", []):
                kws = is_suspicious(sec.get("label", ""))
                if kws:
                    rows.append({
                        "profession": prof_dir.name,
                        "state": state,
                        "citation": sec.get("citation", ""),
                        "label": sec.get("label", "")[:140],
                        "reason": sec.get("reason", "")[:140],
                        "matched_keywords": kws,
                    })

    # Group by profession
    by_prof: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_prof[r["profession"]].append(r)

    print(f"# Trim audit — sections dropped whose LABEL mentions licensure-relevant words\n")
    print(f"Total suspicious drops across all professions: {len(rows)}\n")
    for prof, items in sorted(by_prof.items()):
        print(f"## {prof} — {len(items)} suspicious drops")
        # Cluster within profession by state
        by_state: dict[str, list[dict]] = defaultdict(list)
        for r in items:
            by_state[r["state"]].append(r)
        for state in sorted(by_state):
            print(f"### {state}")
            for r in by_state[state]:
                print(f"- **{r['citation']}** {r['label']}")
                print(f"  - dropped because: _{r['reason']}_")
                print(f"  - matched: {', '.join(r['matched_keywords'])}")
            print()
        print()


if __name__ == "__main__":
    main()

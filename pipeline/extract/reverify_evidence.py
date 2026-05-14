"""Re-run the regex quote check against every Evidence in existing structured
records. Lets us tighten or loosen the matcher without paying for a full
Sonnet re-extraction.

For each state's structured record:
  1. Walk every Evidence-shaped node.
  2. Re-check `quote` against the corresponding state's trimmed corpus
     using the current `quote_in_corpus` implementation.
  3. Set / clear the `unverified` flag accordingly.
  4. Write back in place.

Usage:
  python -m pipeline.extract.reverify_evidence --profession podiatry
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from extract_state import _normalize_for_match, quote_in_corpus, annotate_evidence, load_umbrella_text  # noqa: E402
from paths import STRUCTURED_DIR, TRIMMED_DIR  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    args = ap.parse_args()

    profession = args.profession.lower()
    structured_dir = STRUCTURED_DIR / profession
    trimmed_dir = TRIMMED_DIR / profession

    if not structured_dir.exists():
        sys.exit(f"missing {structured_dir}")

    overall_v = overall_u = 0
    states_changed = 0
    for path in sorted(structured_dir.glob("*.json")):
        if path.stem.startswith("_"):
            continue
        record = json.loads(path.read_text())
        trim_path = trimmed_dir / f"{path.stem}.json"
        if not trim_path.exists():
            continue
        trim = json.loads(trim_path.read_text())
        text = "\n".join(s.get("text", "") for s in trim.get("sections", []))
        # Include the state's umbrella context if cached — extract_state
        # injects umbrella text at extraction time, so quotes pulled from
        # umbrella sections need to be verified against it too.
        umbrella = load_umbrella_text(path.stem)
        if umbrella:
            text = text + "\n" + umbrella
        normalized = _normalize_for_match(text)

        # Strip stale unverified flags so we re-evaluate from scratch
        def strip_flags(node):
            if isinstance(node, dict):
                if {"value", "quote", "citation"}.issubset(node.keys()):
                    node.pop("unverified", None)
                for v in node.values():
                    strip_flags(v)
            elif isinstance(node, list):
                for v in node:
                    strip_flags(v)

        strip_flags(record)

        prev_unverified = sum(1 for _ in _walk(record) if False)  # placeholder
        v, u = annotate_evidence(record, normalized)
        path.write_text(json.dumps(record, indent=2))
        overall_v += v
        overall_u += u
        states_changed += 1
        print(f"  [{path.stem}] verified={v} unverified={u}")

    total = overall_v + overall_u
    pct = (100 * overall_v / total) if total else 0.0
    print(f"\n{profession}: {overall_v}/{total} verified ({pct:.1f}%) across {states_changed} states")


def _walk(node):
    if isinstance(node, dict):
        if {"value", "quote", "citation"}.issubset(node.keys()):
            yield node
        for v in node.values():
            yield from _walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk(v)


if __name__ == "__main__":
    main()

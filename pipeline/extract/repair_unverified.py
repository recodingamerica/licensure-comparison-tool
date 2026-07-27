"""Re-ask the LLM to repair quotes flagged `unverified`.

For each Evidence node carrying `unverified: true`, locate the cited
section's text and re-prompt the LLM with the source + the current claim.
Ask for a verbatim quote from the section that supports the claim, or
None if no support exists.

Validate every returned quote with `quote_in_corpus` against the section
text BEFORE accepting it — the LLM can still paraphrase. Only mutate the
structured record when we get a quote that actually verifies. Otherwise
the original quote (and the unverified flag) stays.

We use Haiku because repairs are tiny one-shot tasks; no benefit from
Sonnet's longer reasoning here. Falls back to flagging unchanged when
the LLM can't find a verbatim substring.

Usage:
  python -m pipeline.extract.repair_unverified --profession podiatry
  python -m pipeline.extract.repair_unverified --profession podiatry --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pydantic import BaseModel

from pipeline._llm import call_structured
from pipeline._records import record_files
from pipeline.extract.extract_state import load_umbrella_text  # noqa: E402
from pipeline.extract.locate_quote import normalize_for_match, quote_in_corpus  # noqa: E402
from pipeline.paths import LOGS_DIR, STRUCTURED_DIR, TRIMMED_DIR
from pipeline.extract.model_helpers import iter_quote_carriers, iter_evidence  # noqa: E402
from pipeline.config.loaders import model_for


LOG_PATH = LOGS_DIR / "repair_unverified.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("repair_unverified")

DEFAULT_MODEL = model_for("repair_unverified")


SYSTEM_PROMPT = """You verify legal statute quotations.

Given the verbatim text of a statute section and a previously-extracted
claim about that section, return the EXACT substring of the section text
that supports the claim — character for character, including any list
markers, capitalization, punctuation, and intervening context.

If no contiguous verbatim substring supports the claim, you may use "..."
(three dots) to elide non-supporting text between supporting chunks — BUT
every chunk you emit between ellipses must appear verbatim in the section
text. Do not paraphrase or correct grammar.

If nothing in the section supports the claim, return quote: null.

Output only the JSON object — no commentary, no markdown fences.
"""


class RepairResult(BaseModel):
    quote: str | None


def find_section_text(prof: str, state: str, citation: str) -> tuple[str, str]:
    """Return (best_match_text, source_label) for the citation.

    Tries exact citation match in trimmed sections first, then substring
    match. Falls back to the combined trimmed corpus when no single
    section matches — the quote may straddle sections.
    """
    trim_path = TRIMMED_DIR / prof / f"{state}.json"
    if not trim_path.exists():
        return "", "no_trim_file"
    trim = json.loads(trim_path.read_text())
    cite_clean = citation.strip("[]").strip().rstrip(".").strip()
    sections = trim.get("sections", [])

    # Exact citation match
    for s in sections:
        sc = (s.get("citation", "") or "").strip().rstrip(".").strip()
        if sc and cite_clean == sc:
            return s.get("text", ""), "exact_cite"

    # Substring match (handles "[311.400]" vs "311.400" etc.)
    for s in sections:
        sc = (s.get("citation", "") or "").strip().rstrip(".").strip()
        if sc and (cite_clean in sc or sc in cite_clean):
            return s.get("text", ""), "substring_cite"

    # Fallback: combined trimmed + umbrella. The LLM gets a much bigger
    # haystack, but that's better than nothing for chapter-blob states.
    combined = "\n".join(s.get("text", "") for s in sections)
    umbrella = load_umbrella_text(state)
    return (combined + "\n" + umbrella), "combined_fallback"


def repair_one(node: dict, prof: str, state: str, model: str) -> tuple[bool, str]:
    """Attempt to repair a single Evidence node. Returns (repaired, reason)."""
    citation = node.get("citation", "")
    value = node.get("value")
    old_quote = node.get("quote", "")

    section_text, source = find_section_text(prof, state, citation)
    if not section_text:
        return False, f"no_section_text:{source}"

    user_msg = (
        f"Section [{citation}]:\n{section_text}\n\n"
        f"Claim:\n"
        f'  value = {json.dumps(value)}\n'
        f'  previous_quote = {json.dumps(old_quote)}\n\n'
        f"Return JSON: {{\"quote\": \"...verbatim substring or null...\"}}"
    )

    result = call_structured(
        model=model,
        system=SYSTEM_PROMPT,
        user=user_msg,
        schema_cls=RepairResult,
        log_prefix=f"[{state}/{citation}]",
        max_tokens=2000,
    )
    if result is None:
        return False, "llm_failed"
    new_quote = result.quote
    if not new_quote:
        return False, "llm_returned_null"

    # Validate the new quote against the section text we sent.
    normalized = normalize_for_match(section_text)
    if not quote_in_corpus(new_quote, normalized):
        return False, "new_quote_still_unverified"

    node["quote"] = new_quote
    node.pop("unverified", None)
    return True, f"repaired_from_{source}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the LLM but don't write changes back to structured/.",
    )
    ap.add_argument(
        "--states",
        default="",
        help="Comma-separated subset (e.g. 'KY,ND'); empty = all.",
    )
    args = ap.parse_args()

    prof = args.profession.lower()
    structured_dir = STRUCTURED_DIR / prof
    if not structured_dir.exists():
        sys.exit(f"missing {structured_dir}")

    only_states = {s.strip().upper() for s in args.states.split(",") if s.strip()}

    from collections import Counter
    reasons = Counter()
    total_unverified = 0
    total_repaired = 0
    for path in record_files(structured_dir):
        if only_states and path.stem not in only_states:
            continue
        record = json.loads(path.read_text())

        to_repair: list[dict] = [
            # Quote carriers: grounds and exams can be unverified now, and a repair
            # pass that can't see them would leave them broken forever.
            n for _, n in iter_quote_carriers(record) if n.get("unverified")
        ]
        if not to_repair:
            continue

        state_repaired = 0
        for node in to_repair:
            total_unverified += 1
            ok, reason = repair_one(node, prof, path.stem, args.model)
            reasons[reason] += 1
            if ok:
                state_repaired += 1
                total_repaired += 1

        if state_repaired and not args.dry_run:
            path.write_text(json.dumps(record, indent=2))
        log.info(
            "[%s] %d unverified, repaired %d",
            path.stem, len(to_repair), state_repaired,
        )

    log.info(
        "%s: repaired %d/%d unverified Evidence nodes",
        prof, total_repaired, total_unverified,
    )
    log.info("Outcomes: %s", dict(reasons))


if __name__ == "__main__":
    main()

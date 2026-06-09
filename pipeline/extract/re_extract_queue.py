"""Run the full re-extract queue end-to-end with cost tracking.

For each profession in the queue, runs:
  1. pipeline.ingest.pull_text   (free — HTTP only)
  2. pipeline.ingest.clean_text  (free — regex)
  3. pipeline.ingest.trim_state  (Haiku 4.5; cost recorded by _llm._USAGE)

Then submits the queued (state, profession) pairs as one Anthropic batch
via extract_state_batch, and polls until done. Final summary lists Haiku
spend (trim stage) + Sonnet batch spend (extract stage).

Usage:
  python -m pipeline.extract.re_extract_queue
  python -m pipeline.extract.re_extract_queue --queue myqueue.json
  python -m pipeline.extract.re_extract_queue --skip-pull-trim  # just submit batch
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
from pathlib import Path

_PIPELINE_DIR = Path(__file__).resolve().parent.parent
if str(_PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(_PIPELINE_DIR))

from extract.extract_state_batch import DEFAULT_QUEUE, submit, poll  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("re_extract_queue")


def _run(cmd: list[str]) -> int:
    log.info(">>> %s", " ".join(cmd))
    return subprocess.call(cmd)


def run_upstream(queue: dict[str, list[str]]) -> tuple[int, float]:
    """Run pull → clean → trim for each (profession, states) group.
    Returns (total_haiku_calls, total_haiku_cost_usd) summed across all
    trim_state invocations (each invocation overwrites trim_state.log, so
    we have to capture per-profession)."""
    py = sys.executable
    total_calls = 0
    total_cost = 0.0
    for profession, states in queue.items():
        states_str = ",".join(states)
        log.info("--- %s × %d states: %s ---", profession, len(states), states_str)
        _run([py, "-m", "pipeline.ingest.pull_text",  "--profession", profession, "--states", states_str])
        _run([py, "-m", "pipeline.ingest.clean_text", "--profession", profession])
        _run([py, "-m", "pipeline.ingest.trim_state", "--profession", profession, "--states", states_str])
        # trim_state.log just got overwritten with this profession's usage; capture before next.
        calls, _, cost = haiku_trim_cost_from_log()
        total_calls += calls
        total_cost += cost
        log.info("  cumulative Haiku trim: %d calls, $%.4f", total_calls, total_cost)
    return total_calls, total_cost


def haiku_trim_cost_from_log() -> tuple[int, int, float]:
    """Read the trim_state.log file's most-recent === LLM usage === block.
    Returns (calls, in_tokens, cost_usd). The log is overwritten per run so
    the last block reflects the most recent profession's trim only — we
    accumulate by reading after each profession too if needed."""
    p = _PIPELINE_DIR / "logs" / "trim_state.log"
    if not p.exists():
        return 0, 0, 0.0
    text = p.read_text()
    # Format: "claude-haiku-4-5-20251001: N calls, X in / Y out tokens, $Z.ZZZZ"
    matches = re.findall(r"claude-haiku-4-5[\w-]*:\s*(\d+) calls,\s*(\d+) in / (\d+) out tokens,\s*\$([\d.]+)",
                         text)
    if not matches:
        return 0, 0, 0.0
    # Sum across all matches in the log (covers multiple profession runs)
    total_calls = sum(int(m[0]) for m in matches)
    total_in = sum(int(m[1]) for m in matches)
    total_cost = sum(float(m[3]) for m in matches)
    return total_calls, total_in, total_cost


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", help="Path to a JSON file: {profession: [states]}")
    ap.add_argument("--skip-pull-trim", action="store_true",
                    help="Skip upstream stages (use when trimmed files are already current)")
    args = ap.parse_args()

    if args.queue:
        queue = json.loads(Path(args.queue).read_text())
    else:
        queue = DEFAULT_QUEUE

    n_pairs = sum(len(s) for s in queue.values())
    log.info("queue: %d (state, profession) pairs across %d professions", n_pairs, len(queue))

    if args.skip_pull_trim:
        haiku_calls, haiku_cost = 0, 0.0
    else:
        haiku_calls, haiku_cost = run_upstream(queue)
    log.info("=== upstream done. Haiku (trim) total: $%.4f across %d calls ===",
             haiku_cost, haiku_calls)

    # Submit the batch
    log.info("submitting Sonnet batch ...")
    metadata = submit(queue)
    batch_id = metadata["batch_id"]
    log.info("batch submitted: %s", batch_id)

    # Poll and write results (also prints batch cost summary)
    poll(batch_id, wait=True)

    # Final combined summary
    log.info("=== FINAL re-extract summary ===")
    log.info("  Haiku (trim):  $%.4f  (%d calls)", haiku_cost, haiku_calls)
    final_meta = json.loads((_PIPELINE_DIR / "results" / "batches" / f"{batch_id}.json").read_text())
    sonnet_cost = final_meta.get("usage", {}).get("cost_usd", 0)
    sonnet_baseline = final_meta.get("usage", {}).get("baseline_usd", 0)
    log.info("  Sonnet batch:  $%.4f  (vs ~$%.4f sync-no-cache, saved %d%%)",
             sonnet_cost, sonnet_baseline,
             100 * (sonnet_baseline - sonnet_cost) / max(sonnet_baseline, 0.0001))
    log.info("  TOTAL:         $%.4f", haiku_cost + sonnet_cost)


if __name__ == "__main__":
    main()

"""Run the pipeline for a set of occupations the client picked — the smallest
number of commands, with every paid step held separate from the free ones.

Pick occupations by name and run, in order, exactly three commands — no file to
download or pass around, no per-state selection to make by hand:

    python -m pipeline.client.run clean   --professions podiatry,dentistry   # FREE
    python -m pipeline.client.run trim    --professions podiatry,dentistry   # ~$0.05/cell — asks first
    python -m pipeline.client.run extract --professions podiatry,dentistry   # ~$0.15/cell — asks first

Every state for each named profession is included automatically — the tool looks up
live status (pipeline.client.status) and includes exactly the states that actually have
work to do (a corpus on disk that hasn't been fully processed, or a done cell that's
gone stale). States with no corpus yet, no schema, or already up to date are silently
skipped — nobody needs to know or care which states those are ahead of time.

Why three commands and not one: `clean` is deterministic and free, so it never needs a
confirmation. `trim` and `extract` each call an LLM and cost real money, so each is its
own command and each prints its estimate and waits for a typed "yes" before spending.
Bundling them would hide the cost; that's the one thing we don't want.

Fetching (`pull_text`) is deliberately NOT here — it needs the CDP setup and everything
in a handed-off repo is already fetched. See docs/runbooks for re-fetching a state later.

DRY: this only orchestrates. `clean`/`trim` shell out to the existing stage modules (same
CLI the pipeline already exposes); `extract` calls extract_state_batch.submit/poll directly.
Prices AND which states are runnable both come from pipeline.client.status — one source
of truth, so this can't drift out of sync with what the dashboard shows.
"""
from __future__ import annotations

import argparse
import subprocess
import sys

from pipeline import provenance
from pipeline.client.status import COST_TRIM, COST_EXTRACT, build as build_status


def _queue_for_professions(names: list[str]) -> dict[str, list[str]]:
    """{profession: [states]} for every state status.build() flags as runnable
    (cell["run"] is True) — a corpus that hasn't been fully processed, or a done
    cell that's gone stale. Same filter the dashboard uses to color/count cells,
    computed live instead of baked into a downloaded file."""
    data = build_status()
    queue: dict[str, list[str]] = {}
    for prof in names:
        info = data["professions"].get(prof)
        if info is None:
            sys.exit(f"unknown profession: {prof!r} (check pipeline/config/professions.yaml)")
        states = [st for st, cell in info["states"].items() if cell.get("run")]
        if states:
            queue[prof] = states
        else:
            print(f"note: {prof} has nothing runnable right now (nothing ready, "
                  f"nothing stale) — skipping")
    if not queue:
        sys.exit("nothing to do for the given profession(s) — run the dashboard "
                  "(python -m pipeline.client.dashboard) to see what's ready.")
    return queue


def _cells(queue: dict[str, list[str]]) -> int:
    return sum(len(s) for s in queue.values())


def _drop_current(stage: str, queue: dict[str, list[str]]
                  ) -> tuple[dict[str, list[str]], list[tuple[str, str]]]:
    """Drop cells that are already CURRENT for this paid stage, so a re-run after a
    partial failure doesn't re-charge for cells that already succeeded. "current" (per
    provenance) means the output exists AND was produced by today's corpus + recipe, so
    re-running would spend money to reproduce an identical file. Stale/unstamped/missing
    cells are kept (they genuinely need the work). Returns (kept_queue, skipped_cells)."""
    kept: dict[str, list[str]] = {}
    skipped: list[tuple[str, str]] = []
    for prof, states in queue.items():
        keep = []
        for st in states:
            if provenance.check(stage, prof, st) == "current":
                skipped.append((prof, st))
            else:
                keep.append(st)
        if keep:
            kept[prof] = keep
    return kept, skipped


def _announce_skipped(skipped: list[tuple[str, str]]) -> None:
    if skipped:
        cells = ", ".join(f"{p}/{s}" for p, s in skipped)
        print(f"\nskipping {len(skipped)} state(s) already up to date — no charge: {cells}")


def _confirm(step: str, queue: dict[str, list[str]], per_cell: float, model: str, yes: bool) -> None:
    """Gate a paid step behind an explicit typed confirmation (skip with --yes).

    The per-cell price is tied to `model` — it's an Anthropic API price for that
    specific model, not a fixed cost of the step. Swap the model (a single constant
    in the stage module, or its --model flag) and this number moves; it isn't
    hand-maintained anywhere, so it can't silently go stale."""
    n = _cells(queue)
    est = n * per_cell
    print(f"\n{step}: {n} cell(s) across {len(queue)} occupation(s)  ·  "
          f"estimated cost ~${est:.2f}  (${per_cell:.2f}/cell, using {model} at today's price — "
          f"changes if the model changes)")
    if yes:
        print("  --yes given, proceeding without prompt.")
        return
    reply = input('  Type "yes" to run this paid step: ').strip().lower()
    if reply != "yes":
        sys.exit("  aborted — no charge incurred.")


def _run_cmd(cmd: list[str], fail_msg: str) -> None:
    """Echo and run one subprocess, exiting with a friendly message on failure."""
    print(f"\n$ {' '.join(cmd)}", flush=True)
    if subprocess.run(cmd).returncode != 0:
        sys.exit(fail_msg)


def _run_per_profession(module: str, queue: dict[str, list[str]], extra: list[str]) -> None:
    """Shell out to an existing stage module once per profession (its CLI takes
    --profession + --states). Reuses the pipeline's own entry point — no reimplementation."""
    py = sys.executable
    for prof, states in queue.items():
        cmd = [py, "-m", module, "--profession", prof, "--states", ",".join(states), *extra]
        _run_cmd(cmd, f"step failed for {prof} — fix the error above and re-run this command "
                      f"(states already up to date are skipped, so it's safe to re-run).")


def cmd_clean(queue: dict[str, list[str]], args) -> None:
    # Free + deterministic: no confirmation. Turns raw fetched text into clean sections.
    _run_per_profession("pipeline.ingest.clean_text", queue, [])
    profs = ",".join(queue)
    print("\nclean done. Next (this one costs money): "
          f"python -m pipeline.client.run trim --professions {profs}")


def cmd_trim(queue: dict[str, list[str]], args) -> None:
    from pipeline.ingest.trim_state import DEFAULT_MODEL as TRIM_MODEL
    if not args.redo:
        queue, skipped = _drop_current("trim", queue)
        _announce_skipped(skipped)
    if not queue:
        print("\nnothing to trim — every selected state is already up to date. (Use --redo to force.)")
        return
    _confirm("trim (drops irrelevant sections)", queue, COST_TRIM, TRIM_MODEL, args.yes)
    extra = ["--strict"] if args.strict else []
    _run_per_profession("pipeline.ingest.trim_state", queue, extra)
    profs = ",".join(queue)
    print("\ntrim done. Next (this one costs money): "
          f"python -m pipeline.client.run extract --professions {profs}")


def cmd_extract(queue: dict[str, list[str]], args) -> None:
    # Import here so `clean`/`trim` don't pay the anthropic-client import cost.
    from pipeline.extract.extract_state_batch import submit, poll, DEFAULT_MODEL as EXTRACT_MODEL
    if not args.redo:
        queue, skipped = _drop_current("extract", queue)
        _announce_skipped(skipped)
    if not queue:
        print("\nnothing to extract — every selected state is already up to date. (Use --redo to force.)")
        return
    _confirm("extract (structures the law, batched)", queue, COST_EXTRACT, EXTRACT_MODEL, args.yes)
    requested = _cells(queue)
    meta = submit(queue, force=args.force)
    print(f"\nsubmitted batch {meta['batch_id']} — waiting for results "
          f"(safe to Ctrl-C; re-poll later with: "
          f"python -m pipeline.extract.extract_state_batch poll {meta['batch_id']})")
    result = poll(meta["batch_id"], wait=True)
    _report_extract(requested, result, meta["batch_id"])


def _report_extract(requested: int, result: dict | None, batch_id: str) -> None:
    """Report what the batch ACTUALLY did — never a blanket 'done'. A batch can partially
    fail (some cells error), and the preflight can drop cells before submission, so we
    reconcile requested vs written vs errored and tell the client exactly what to retry."""
    if not result:
        print(f"\nextract: batch {batch_id} not finished yet — re-poll later with "
              f"python -m pipeline.extract.extract_state_batch poll {batch_id}")
        return
    written = result.get("written") or []
    errored = result.get("errored") or []
    print(f"\nextract done: {len(written)} of {requested} state(s) written to "
          f"pipeline/results/structured/.")
    if errored:
        ids = ", ".join(sorted(str(e.get("custom_id", "?")) for e in errored))
        print(f"  {len(errored)} failed (re-run this command to retry them): {ids}")
    not_submitted = requested - len(written) - len(errored)
    if not_submitted > 0:
        print(f"  {not_submitted} state(s) were not submitted (blocked by the extract "
              f"preflight — check the log, or re-run with --force to override).")


def cmd_publish(args) -> None:
    # Rebuilding the payload + blob upload is the normal, free publish step. `--deploy`
    # additionally pushes the PUBLIC live site — an outward-facing action, so it gets the
    # same typed-yes gate as the paid steps (one-time Vercel setup: docs/runbooks/client_deploy.md).
    profs = [p.strip() for p in args.professions.split(",") if p.strip()]
    if not profs:
        sys.exit("no professions given — pass --professions a,b,c")
    if args.deploy and not args.yes:
        print(f"\n--deploy will rebuild the PUBLIC live site (utah-licensing.vercel.app) "
              f"with: {', '.join(profs)}")
        print("  Needs one-time Vercel setup first — see docs/runbooks/client_deploy.md.")
        if input('  Type "yes" to push the site live: ').strip().lower() != "yes":
            sys.exit("  aborted — nothing deployed (payloads not rebuilt either).")
    extra = ["--deploy"] if args.deploy else []
    for prof in profs:
        cmd = [sys.executable, "-m", "pipeline.publish.build_frontend", "--profession", prof, *extra]
        _run_cmd(cmd, f"publish failed for {prof} — see the error above.")
    print("\npublish done." + ("" if args.deploy else
          "  (add --deploy to also push it live to the website.)"))


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the pipeline for client-picked occupations.")
    sub = ap.add_subparsers(dest="step", required=True)
    for name, help_ in [
        ("clean", "FREE — clean fetched text"),
        ("trim", f"~${COST_TRIM:.2f}/cell at today's model+price (asks first) — drop irrelevant sections"),
        ("extract", f"~${COST_EXTRACT:.2f}/cell at today's model+price (asks first) — structure the law"),
    ]:
        sp = sub.add_parser(name, help=help_)
        sp.add_argument("--professions", required=True,
                        help="Comma-separated occupation names (e.g. podiatry,dentistry). "
                             "Every state with work to do for each is included automatically.")
        sp.add_argument("--yes", action="store_true", help="Skip the cost confirmation prompt")
        if name in ("trim", "extract"):
            sp.add_argument("--redo", action="store_true",
                            help="Reprocess (and re-charge for) states that are already up to date")
        if name == "trim":
            sp.add_argument("--strict", action="store_true",
                            help="Fail loudly on any LLM error instead of skipping")
        if name == "extract":
            sp.add_argument("--force", action="store_true",
                            help="Submit even if the preflight gate finds blockers")
    # publish is per-occupation, not per-cell — its own interface.
    sp = sub.add_parser("publish", help="FREE — build the web payload so it shows on the site")
    sp.add_argument("--professions", required=True, help="Comma-separated occupations to publish")
    sp.add_argument("--deploy", action="store_true", help="Also push it live to the website (asks first)")
    sp.add_argument("--yes", action="store_true", help="Skip the --deploy confirmation prompt")

    args = ap.parse_args()

    if args.step == "publish":
        cmd_publish(args)
        return
    names = [p.strip() for p in args.professions.split(",") if p.strip()]
    if not names:
        sys.exit("no professions given — pass --professions a,b,c")
    queue = _queue_for_professions(names)
    {"clean": cmd_clean, "trim": cmd_trim, "extract": cmd_extract}[args.step](queue, args)


if __name__ == "__main__":
    main()

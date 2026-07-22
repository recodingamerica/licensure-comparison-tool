"""Run the pipeline for a set of occupations the client picked — the smallest
number of commands, with every paid step held separate from the free ones.

Pick occupations by name and run, in order — no file to download or pass around,
no per-state selection to make by hand:

    python -m pipeline.client.run clean   --professions podiatry,dentistry   # FREE
    python -m pipeline.client.run schema  --professions podiatry,dentistry   # ~$1.00/occupation, one-time — asks first
    python -m pipeline.client.run trim    --professions podiatry,dentistry   # ~$0.05/cell — asks first
    python -m pipeline.client.run extract --professions podiatry,dentistry   # ~$0.15/cell — asks first

Every state for each named profession is included automatically — the tool looks up
live status (pipeline.client.status) and includes exactly the states that actually have
work to do (a corpus on disk that hasn't been fully processed, or a done cell that's
gone stale). States with no corpus yet, no schema, or already up to date are silently
skipped — nobody needs to know or care which states those are ahead of time.

`schema` is different from the other three: it's ONE call per occupation (not per
state) that a NEW occupation needs exactly once before `extract` can run for any of
its states. Skip it for an occupation that already has one — `run.py` checks and
tells you if there's nothing to do.

Why separate commands and not one: `clean` is deterministic and free, so it never
needs a confirmation. `schema`, `trim`, and `extract` each call an LLM and cost real
money, so each is its own command and each prints its estimate — including the exact
model it's priced against — and waits for a typed "yes" before spending. Bundling
them would hide the cost; that's the one thing we don't want.

Fetching (`pull_text`) is deliberately NOT here — it needs internet access and everything
in a handed-off repo is already fetched. See docs/runbooks for re-fetching a state later.

DRY: this only orchestrates. `clean`/`schema`/`trim` shell out to the existing stage
modules (same CLI the pipeline already exposes); `extract` calls
extract_state_batch.submit/poll directly. Prices AND which states/occupations are
runnable both come from pipeline.client.status — one source of truth, so this can't
drift out of sync with what the dashboard shows.
"""
from __future__ import annotations

import argparse
import sys

from pipeline.pipeline_stages import run_to, drop_current, confirm_if_paid, _sh, REPO_ROOT
from pipeline.client.status import COST_TRIM, COST_EXTRACT, COST_SCHEMA, build as build_status


def _queue_for_professions(names: list[str]) -> dict[str, list[str]]:
    """{profession: [states]} for every state status.build() flags as runnable
    (cell["run"] is True) — a corpus that hasn't been fully processed AND has a
    schema, or a done cell that's gone stale. Same filter the dashboard uses to
    color/count cells. Use this for `extract`, which genuinely can't run without a
    schema. For `clean`/`trim` (neither of which touches the schema at all — a
    profession can be cleaned and trimmed long before anyone designs its schema),
    use `_queue_by_stage` instead so a schema-less occupation isn't stuck unable to
    even reach the point where discover_schema has trimmed text to read."""
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


def _queue_by_stage(names: list[str], stages: set[str]) -> dict[str, list[str]]:
    """{profession: [states]} for every state currently at one of `stages`,
    independent of schema — a "done, stale" cell also counts (it needs the whole
    chain re-run). Re-cleaning/re-trimming a state already past that stage is
    harmless (each stage writes its own directory), so this is intentionally
    inclusive rather than exact-stage-only."""
    data = build_status()
    queue: dict[str, list[str]] = {}
    for prof in names:
        info = data["professions"].get(prof)
        if info is None:
            sys.exit(f"unknown profession: {prof!r} (check pipeline/config/professions.yaml)")
        states = [st for st, cell in info["states"].items()
                  if cell["stage"] in stages or cell.get("fresh") == "stale"]
        if states:
            queue[prof] = states
        else:
            print(f"note: {prof} has nothing at this stage right now — skipping")
    if not queue:
        sys.exit("nothing to do for the given profession(s) — run the dashboard "
                  "(python -m pipeline.client.dashboard) to see what's ready.")
    return queue


def _professions_needing_schema(names: list[str]) -> list[str]:
    """Occupation-level, not cell-level: which of the named professions actually have
    corpus on disk waiting on a one-time schema (status.py's cost_schema > 0). An
    occupation that already has a schema, or has no corpus pulled yet at all, is
    dropped with a note rather than treated as an error — same spirit as
    _queue_for_professions skipping a profession with nothing runnable."""
    data = build_status()
    needed: list[str] = []
    for prof in names:
        info = data["professions"].get(prof)
        if info is None:
            sys.exit(f"unknown profession: {prof!r} (check pipeline/config/professions.yaml)")
        if info["summary"]["cost_schema"] > 0:
            needed.append(prof)
        elif info["summary"]["has_schema"]:
            print(f"note: {prof} already has a schema — skipping")
        else:
            print(f"note: {prof} has no corpus pulled yet, so there's nothing for "
                  f"discover_schema to read — skipping")
    if not needed:
        sys.exit("nothing to do — none of the given profession(s) need a schema right now.")
    return needed


def _cells(queue: dict[str, list[str]]) -> int:
    return sum(len(s) for s in queue.values())


def _announce_skipped(skipped: list[tuple[str, str]]) -> None:
    if skipped:
        cells = ", ".join(f"{p}/{s}" for p, s in skipped)
        print(f"\nskipping {len(skipped)} state(s) already up to date — no charge: {cells}")


def _run_stage(stage: str, queue: dict[str, list[str]], opts: dict | None = None) -> None:
    """Run ONE stage over the queue via the shared runner (start=stage → only that stage;
    force=True → run exactly the states we selected; yes=True → the cost gate already fired
    once at the command level). Exits with a friendly, safe-to-re-run message on failure."""
    for prof, states in queue.items():
        res = run_to(stage, prof, states, start=stage, force=True, yes=True, opts=opts or {})
        if not res["ok"]:
            sys.exit(f"{stage} failed for {prof} — fix the error above and re-run this command "
                     f"(states already up to date are skipped, so it's safe to re-run).")


def cmd_clean(queue: dict[str, list[str]], args) -> None:
    # Free + deterministic: no confirmation. Turns raw fetched text into clean sections.
    _run_stage("clean", queue)
    profs = ",".join(queue)
    print("\nclean done. Next (this one costs money): "
          f"python -m pipeline.client.run trim --professions {profs}")


def cmd_schema(names: list[str], args) -> None:
    """One-time, per-occupation (not per-cell): design the data template a new
    occupation needs before extract can run for any of its states."""
    needed = _professions_needing_schema(names)
    confirm_if_paid("schema", len(needed), args.yes)   # ~$1/occupation, names the model
    _run_stage("schema", {p: [] for p in needed})
    profs = ",".join(needed)
    print("\nschema done. Next (this one costs money): "
          f"python -m pipeline.client.run trim --professions {profs}")


def cmd_trim(queue: dict[str, list[str]], args) -> None:
    if not args.redo:
        queue, skipped = drop_current("trim", queue)   # drop CURRENT cells BEFORE charging
        _announce_skipped(skipped)
    if not queue:
        print("\nnothing to trim — every selected state is already up to date. (Use --redo to force.)")
        return
    confirm_if_paid("trim", _cells(queue), args.yes)   # one prompt for the whole queue
    _run_stage("trim", queue, {"strict": args.strict})
    profs = ",".join(queue)
    print("\ntrim done. Next (this one costs money): "
          f"python -m pipeline.client.run extract --professions {profs}")


def cmd_extract(queue: dict[str, list[str]], args) -> None:
    # Import here so `clean`/`trim` don't pay the anthropic-client import cost.
    from pipeline.extract.extract_state_batch import submit, poll, run_litellm, DEFAULT_MODEL as EXTRACT_MODEL
    backend = getattr(args, "backend", "claude")
    model = getattr(args, "model", None) or EXTRACT_MODEL
    if not args.redo:
        queue, skipped = drop_current("extract", queue)   # drop CURRENT cells BEFORE charging
        _announce_skipped(skipped)
    if not queue:
        print("\nnothing to extract — every selected state is already up to date. (Use --redo to force.)")
        return
    requested = _cells(queue)

    if backend == "litellm":
        # Vendor-neutral path (any provider LiteLLM supports). No 50% batch discount and no
        # prompt-cache reuse, so budget ~2× the claude-batch per-cell figure — and the real
        # price depends on the vendor. This price differs from the shared confirm_if_paid
        # (which quotes the claude-batch cost), so it keeps its own honest estimate.
        n, est = _cells(queue), _cells(queue) * COST_EXTRACT * 2
        print(f"\nextract via LiteLLM — {model}, NO batch discount: {n} cell(s) "
              f"~${est:.2f} (~${COST_EXTRACT * 2:.2f}/cell est; real price depends on vendor)")
        if not args.yes and input('  Type "yes" to run this paid step: ').strip().lower() != "yes":
            sys.exit("  aborted — no charge incurred.")
        result = run_litellm(queue, model=model, force=args.force)
        _report_extract(requested, result, result.get("batch_id", "litellm"))
        return

    # Default: Anthropic Message Batches (50% off + prompt caching; Claude only). All of the
    # queue goes in ONE batch, so confirm once here rather than per profession via run_to.
    confirm_if_paid("extract", requested, args.yes)
    meta = submit(queue, model=model, force=args.force)
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
    # same typed-yes gate as the paid steps (one-time Vercel setup: CLIENT_GUIDE.md).
    if getattr(args, "all", False):
        from pipeline.client.handoff_doc import _published
        profs = _published()  # every profession with a built payload in public/data/
        if not profs:
            sys.exit("--all: no built payloads found in public/data/")
    else:
        profs = [p.strip() for p in (args.professions or "").split(",") if p.strip()]
        if not profs:
            sys.exit("no professions given — pass --professions a,b,c (or --all)")
    if args.deploy and not args.yes:
        print(f"\n--deploy will rebuild the PUBLIC live site (utah-licensing.vercel.app) "
              f"with {len(profs)} occupation(s): {', '.join(profs)}")
        print("  Needs one-time Vercel setup first — see CLIENT_GUIDE.md.")
        if input('  Type "yes" to push the site live: ').strip().lower() != "yes":
            sys.exit("  aborted — nothing deployed (payloads not rebuilt either).")
    # Build every payload FIRST (via the publish adapter: consistency gate + build_frontend +
    # provenance stamp), then deploy ONCE at the end — deploying per-profession would rebuild
    # the site N times.
    for prof in profs:
        if not run_to("publish", prof, start="publish", force=True, yes=True)["ok"]:
            sys.exit(f"publish failed for {prof} — see the error above.")
    if args.deploy:
        web_dir = REPO_ROOT / "pipeline" / "publish" / "web"
        print(f"\ndeploying once via vercel --prod from {web_dir} …")
        if not _sh(["npx", "vercel", "--prod", "--yes"], "vercel deploy", cwd=str(web_dir)):
            sys.exit("vercel deploy failed — see above.")
        print("deployed — the live site now shows the rebuilt payloads.")
    else:
        print("\npublish done.  (add --deploy to also push it live to the website.)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the pipeline for client-picked occupations.")
    sub = ap.add_subparsers(dest="step", required=True)
    for name, help_ in [
        ("clean", "FREE — clean fetched text"),
        ("schema", f"~${COST_SCHEMA:.2f}/occupation, ONE-TIME (asks first) — design a new occupation's data template"),
        ("trim", f"~${COST_TRIM:.2f}/cell at today's model+price (asks first) — drop irrelevant sections"),
        ("extract", f"~${COST_EXTRACT:.2f}/cell at today's model+price (asks first) — structure the law"),
    ]:
        sp = sub.add_parser(name, help=help_)
        profs_help = ("Comma-separated occupation names (e.g. podiatry,dentistry) that need one."
                      if name == "schema" else
                      "Comma-separated occupation names (e.g. podiatry,dentistry). "
                      "Every state with work to do for each is included automatically.")
        sp.add_argument("--professions", required=True, help=profs_help)
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
            sp.add_argument("--backend", choices=["claude", "litellm"], default="claude",
                            help="claude (default): Anthropic Message Batches, 50%% cheaper, "
                                 "Claude only. litellm: any vendor (e.g. --model gpt-5), no "
                                 "batch discount.")
            sp.add_argument("--model", default=None,
                            help="Model to extract with (default: the pipeline's Sonnet). "
                                 "With --backend litellm, any LiteLLM model name works.")
    # publish is per-occupation, not per-cell — its own interface.
    sp = sub.add_parser("publish", help="FREE — build the web payload so it shows on the site")
    sp.add_argument("--professions", help="Comma-separated occupations to publish (or use --all)")
    sp.add_argument("--all", action="store_true",
                    help="Publish every occupation that already has a payload (auto-derived)")
    sp.add_argument("--deploy", action="store_true",
                    help="After building, push it live to the website ONCE (asks first)")
    sp.add_argument("--yes", action="store_true", help="Skip the --deploy confirmation prompt")

    args = ap.parse_args()

    if args.step == "publish":
        cmd_publish(args)
        return
    names = [p.strip() for p in args.professions.split(",") if p.strip()]
    if not names:
        sys.exit("no professions given — pass --professions a,b,c")
    if args.step == "schema":
        # Occupation-level, not per-state — no states-queue to build.
        cmd_schema(names, args)
        return
    if args.step in ("clean", "trim"):
        # Neither touches the schema — a schema-less occupation must still be able
        # to reach "trimmed" so discover_schema has something to read.
        queue = _queue_by_stage(names, {"pulled", "cleaned", "trimmed"})
    else:
        queue = _queue_for_professions(names)
    {"clean": cmd_clean, "trim": cmd_trim, "extract": cmd_extract}[args.step](queue, args)


if __name__ == "__main__":
    main()

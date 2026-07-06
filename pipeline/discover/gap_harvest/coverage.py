"""Coverage report — what the gap harvest is adding. Turns "we pulled a lot" into numbers:
overall (profession, state) coverage, how much the harvest contributed, top gainers, and
the confirmed-absence tally. Writes a markdown report and prints a summary.

  python -m pipeline.discover.gap_harvest.coverage
"""
from __future__ import annotations
import json, glob, os

from pipeline.paths import TEXT_DIR
from pipeline.config.loaders import load_professions
from pipeline.discover.gap_harvest import _common as C

REPORT = "docs/reports/gap_harvest_coverage.md"


def _has_corpus(prof: str, state: str) -> bool:
    f = TEXT_DIR / prof / f"{state}.json"
    if not f.exists():
        return False
    try:
        d = json.loads(f.read_text())
    except Exception:
        return False
    s = d if isinstance(d, list) else d.get("sections", [])
    return len(s) > 0


def main():
    profs = [k for k in load_professions() if not k.startswith("_")]
    results = C.load_json("locator_results.json", {})

    # harvest tallies from the located results
    located = recovered = absent = 0
    gained_by_prof: dict[str, int] = {}
    for p in results:
        for st, r in results[p].items():
            url = r.get("url")
            if url in (None, "null"):
                absent += 1
            elif r.get("via") == "null_recovery":
                recovered += 1
            else:
                located += 1
            if url and url != "null" and _has_corpus(p, st):
                gained_by_prof[p] = gained_by_prof.get(p, 0) + 1

    # overall coverage across the whole taxonomy
    total_cells = sum(1 for p in profs for f in glob.glob(str(TEXT_DIR / p / "*.json"))
                      if not os.path.basename(f).startswith("_"))
    profs_with_corpus = sum(1 for p in profs if glob.glob(str(TEXT_DIR / p / "*.json")))
    harvest_landed = sum(gained_by_prof.values())

    lines = ["# Gap-harvest coverage", "",
             f"- Professions in taxonomy: **{len(profs)}**",
             f"- Professions with ≥1 corpus: **{profs_with_corpus}**",
             f"- Total (profession, state) corpora: **{total_cells}**",
             "",
             "## Gap harvest contribution",
             f"- Located (primary): **{located}**  ·  recovered from nulls: **{recovered}**  "
             f"·  confirmed absent: **{absent}**",
             f"- Cells landed so far (corpus now present): **{harvest_landed}**",
             "",
             "## Top professions by cells gained", "",
             "| Profession | cells gained |", "|---|---|"]
    for p in sorted(gained_by_prof, key=lambda x: -gained_by_prof[x])[:25]:
        lines.append(f"| {p} | {gained_by_prof[p]} |")
    report = "\n".join(lines) + "\n"

    os.makedirs("docs/reports", exist_ok=True)
    open(REPORT, "w").write(report)
    print(report)
    print(f"wrote {REPORT}")


if __name__ == "__main__":
    main()

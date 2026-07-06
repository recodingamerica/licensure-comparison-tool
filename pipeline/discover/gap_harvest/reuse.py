"""Reuse existing corpora before pulling. Many located chapters were ALREADY fetched for
another profession in that state (osteopathic_medicine -> the medical-practice act we hold
under 'medicine'). Copy the sections that fall under the located chapter instead of
re-fetching — LLM-free, instant. Writes the reused corpora and the remaining pull worklist.

  python -m pipeline.discover.gap_harvest.reuse

Reads gap_harvest/locator_results.json; writes text/<prof>/<state>.json for reused cells,
gap_harvest/pull_worklist.json (what still needs a CDP pull), gap_harvest/reused.json.
"""
from __future__ import annotations
import json, glob, os

from pipeline.paths import TEXT_DIR
from pipeline.discover.gap_harvest import _common as C


def _sections(path: str) -> list:
    try:
        d = json.load(open(path))
    except Exception:
        return []
    return d if isinstance(d, list) else d.get("sections", [])


def _index_existing_by_state() -> dict[str, list[tuple[str, dict, str]]]:
    """{state: [(section_url, section, source_profession)]} across all existing corpora."""
    by_state: dict[str, list] = {}
    for f in glob.glob(str(TEXT_DIR / "*" / "*.json")):
        prof, st = f.split("/")[-2], os.path.basename(f)[:-5]
        if st.startswith("_"):
            continue
        for sec in _sections(f):
            if sec.get("url"):
                by_state.setdefault(st, []).append((sec["url"], sec, prof))
    return by_state


def main():
    results = C.load_json("locator_results.json", {})
    by_state = _index_existing_by_state()
    reused: dict[str, list[str]] = {}
    still_pull: dict[str, list[str]] = {}
    reuse_cells = reuse_secs = 0

    for prof in results:
        for st, r in results[prof].items():
            url = r.get("url")
            if not url or url == "null" or r.get("via") == "null_recovery":
                continue
            if (TEXT_DIR / prof / f"{st}.json").exists():
                continue  # already have it
            base = url.rstrip("/")
            matched = {u: sec for u, sec, src in by_state.get(st, [])
                       if src != prof and (u.rstrip("/") == base or u.startswith(base + "/"))}
            if matched:
                (TEXT_DIR / prof).mkdir(parents=True, exist_ok=True)
                (TEXT_DIR / prof / f"{st}.json").write_text(json.dumps(
                    {"sections": list(matched.values()),
                     "source": "reused_from_existing_corpus", "reused_chapter": url}, indent=1))
                reused.setdefault(prof, []).append(st)
                reuse_cells += 1
                reuse_secs += len(matched)
            else:
                still_pull.setdefault(prof, []).append(st)

    C.save_json("pull_worklist.json", still_pull)
    C.save_json("reused.json", reused)
    print(f"reused {reuse_cells} cells ({reuse_secs} sections) — no fetch")
    print(f"still to pull: {sum(len(v) for v in still_pull.values())} cells "
          f"across {len(still_pull)} professions → gap_harvest/pull_worklist.json")


if __name__ == "__main__":
    main()

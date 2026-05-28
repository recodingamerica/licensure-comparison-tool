"""Per-state umbrella browse data — the data backing /umbrella/<STATE>.

For every state that has an umbrella_scope (walker + Pass 3 merged), emit a
self-contained file:

  pipeline/publish/web/public/data/umbrella/<STATE>.json

shape:
  {
    state, section_count, coverage: {universal, enumerated, undetermined},
    chapters: [
      {slug, label, sections: [
        {url, label, audience, applies_to, text}
      ]}
    ],
    all_professions: [...]   # every profession id assigned anywhere in the state
  }

Each section's `audience` is one of:
  "universal"     -> applies to all licensed professions in the state
                    (applies_to: null)
  "enumerated"    -> applies_to is the explicit list
  "undetermined"  -> the pipeline couldn't auto-scope it; honest residual

Unlike `build_state_browse`, this does NOT filter to a 6-profession subset and
does NOT need the trimmed/structured corpus — it works for every state with
umbrella data (43 today). Pure umbrella view.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import RESULTS_DIR  # noqa: E402
from scope_sources import is_universal, is_enumeration  # noqa: E402
from merged_scope import load_merged_scope  # noqa: E402
from discover._profession_reverse_index import build_reverse_index  # noqa: E402

UMBRELLA_TEXT_DIR = RESULTS_DIR / "umbrella_text"
OUT_DIR = Path(__file__).resolve().parent / "web" / "public" / "data" / "umbrella"

# Length of section text kept inline for the browse view. Full text is in
# umbrella_text — UI can fetch on demand if it needs more.
TEXT_SNIPPET_CHARS = 600

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("build_umbrella_browse")


def _classify(scope_source: str | None) -> str:
    if is_universal(scope_source):
        return "universal"
    if is_enumeration(scope_source):
        return "enumerated"
    return "undetermined"


def build_state_umbrella(state: str) -> dict | None:
    """Assemble the umbrella browse payload for one state, or None if the
    state has no umbrella_scope (no walker output and no skeleton)."""
    merged = load_merged_scope(state)
    if merged is None:
        return None
    text_path = UMBRELLA_TEXT_DIR / f"{state}.json"
    text_by_url: dict[str, dict] = {}
    if text_path.exists():
        for s in json.loads(text_path.read_text()).get("sections", []):
            text_by_url[s.get("url")] = s

    chap_label: dict[str, str] = {}
    chap_sections: dict[str, list[dict]] = defaultdict(list)
    coverage = {"universal": 0, "enumerated": 0, "undetermined": 0}
    all_profs: set[str] = set()

    for s in merged.get("sections", []):
        url = s.get("url") or ""
        chap = s.get("umbrella_chapter_slug") or ""
        if not url or not chap:
            continue
        audience = _classify(s.get("scope_source"))
        coverage[audience] += 1
        applies = s.get("applies_to_professions")
        if audience == "enumerated":
            all_profs.update(applies or [])
            applies_out: list[str] | None = sorted(set(applies or []))
        elif audience == "universal":
            applies_out = None
        else:
            applies_out = None  # undetermined

        ts = text_by_url.get(url, {})
        if not chap_label.get(chap):
            chap_label[chap] = (ts.get("umbrella_chapter_label") or chap).strip()
        full_text = (ts.get("text") or "").strip()
        snippet = full_text[:TEXT_SNIPPET_CHARS] + ("…" if len(full_text) > TEXT_SNIPPET_CHARS else "")
        chap_sections[chap].append({
            "url": url,
            "label": s.get("label") or "(unlabeled section)",
            "audience": audience,
            "applies_to": applies_out,
            "text": snippet,
        })

    chapters_out = [
        {"slug": slug, "label": chap_label.get(slug, slug),
         "sections": chap_sections[slug]}
        for slug in sorted(chap_sections, key=lambda k: chap_label.get(k, k))
    ]
    return {
        "state": state,
        "section_count": sum(coverage.values()),
        "coverage": coverage,
        "all_professions": sorted(all_profs),
        "chapters": chapters_out,
    }


def _states_with_scope() -> list[str]:
    scope_dir = RESULTS_DIR / "umbrella_scope"
    return sorted(p.stem for p in scope_dir.glob("*.json") if not p.stem.startswith("_"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", help="single state (default: every state with umbrella_scope)")
    args = ap.parse_args()

    states = [args.state.upper()] if args.state else _states_with_scope()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    index_states: list[dict] = []
    all_profession_ids: set[str] = set()
    # (state, profession) -> count of umbrella sections that apply
    matrix: dict[str, dict[str, int]] = {}
    written = 0
    for st in states:
        payload = build_state_umbrella(st)
        if payload is None:
            log.info("[%s] no umbrella_scope — skipped", st)
            continue
        (OUT_DIR / f"{st}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False))
        written += 1

        # Per-(state, profession) section count: a universal section counts for
        # every profession the state regulates (per its reverse_index); an
        # enumerated section counts only for the professions it lists.
        state_profs = set(p for ids in build_reverse_index(st).values() for p in ids)
        all_profession_ids.update(state_profs)
        n_universal = payload["coverage"]["universal"]
        per_prof: dict[str, int] = {p: n_universal for p in state_profs}
        for ch in payload["chapters"]:
            for sec in ch["sections"]:
                if sec["audience"] == "enumerated":
                    for p in (sec["applies_to"] or []):
                        per_prof[p] = per_prof.get(p, 0) + 1
        matrix[st] = {p: n for p, n in per_prof.items() if n > 0}

        index_states.append({
            "state": st,
            "section_count": payload["section_count"],
            "coverage": payload["coverage"],
            "profession_count": len(payload["all_professions"]),
            "state_regulates": sorted(state_profs),
        })

    index = {
        "states": index_states,
        "professions": sorted(all_profession_ids),
        "matrix": matrix,   # {state: {profession: count}}
    }
    (OUT_DIR / "_index.json").write_text(json.dumps(index, indent=2))
    log.info("wrote %d per-state umbrella files + _index.json (matrix across %d states × %d professions) to %s",
             written, len(index_states), len(all_profession_ids), OUT_DIR)


if __name__ == "__main__":
    main()

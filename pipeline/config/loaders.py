"""Single read path for the five operator-maintained config files.

Every module that needs professions / state_structure / mapping_overrides /
corpus_overrides / verified_absences imports from here instead of reading YAML
ad-hoc. Write paths (register_occupation writes professions.yaml,
_mapping_overrides.write_mapping_overrides, add_occupation._apply_candidates, …)
stay in their owning modules.

Loader semantics:
  load_professions()      — raw professions.yaml dict (includes _families key)
  registry_professions()  — same dict minus underscore keys (the public profession set)
  load_state_structure()  — state_structure.yaml via safe_load_unique; {} if missing
  load_mapping_overrides()— re-exported from pipeline.discover._mapping_overrides
  load_corpus_overrides() — corpus_overrides.yaml; {} if missing; raises on malformed
  load_verified_absences()— verified_absences.yaml; {} handling as noted on the fn
  load_limits()           — limits.yaml; every data-shaping number in one place

Every YAML file here is read through safe_load_unique (config/yaml_loader.py), so a
duplicate mapping key fails loud with the offending key + line instead of being
silently dropped last-wins (the WA/VA/NV state_structure data-loss failure mode).
"""

from __future__ import annotations

import functools
import logging
from pathlib import Path

import yaml

log = logging.getLogger(__name__)

from pipeline.paths import CONFIG_DIR, TEXT_DIR
from pipeline.config.yaml_loader import safe_load_unique

# Re-export so callers can do `from pipeline.config.loaders import load_mapping_overrides`
# without importing from _mapping_overrides directly.  The _mapping_overrides module
# remains the read/write owner.
from pipeline.discover._mapping_overrides import load_mapping_overrides  # noqa: F401


def load_professions() -> dict:
    """Raw professions.yaml (includes _families and other underscore keys).

    safe_load_unique (not plain yaml.safe_load): a duplicate profession key would
    otherwise be silently dropped last-wins — the same failure mode that lost a
    state_structure block. professions.yaml is append-structured (one key per
    profession), so a dup is a real editing mistake worth failing on.
    """
    path = CONFIG_DIR / "professions.yaml"
    return safe_load_unique(path.read_text()) or {}


def registry_professions() -> dict:
    """professions.yaml minus underscore keys (_families etc.) — the public profession set."""
    return {k: v for k, v in load_professions().items() if not k.startswith("_")}


def load_state_structure() -> dict:
    """Load config/state_structure.yaml. Returns {} if missing.

    Uses safe_load_unique (not yaml.safe_load): a duplicate top-level state key
    would otherwise be silently dropped last-wins, taking its overrides with it.
    See config/yaml_loader.py — this bit us with WA/VA/NV in state_structure.yaml.
    """
    path = CONFIG_DIR / "state_structure.yaml"
    if not path.exists():
        return {}
    return safe_load_unique(path.read_text()) or {}


def load_corpus_overrides(profession: str | None = None) -> dict:
    """Load config/corpus_overrides.yaml.

    Shape: {profession: {STATE: sibling_profession}}

    - Returns {} when the file is missing (legitimately unconfigured).
    - Raises RuntimeError when the file exists but is malformed/unreadable —
      a malformed file would SILENTLY disable every sibling-corpus borrow,
      producing false gaps across the whole run.  Fail loud.  This matches the
      exact semantics of clean_text.corpus_from_overrides() before this refactor.
    - If profession is given, returns only {STATE: sibling} for that profession
      (the clean_text.corpus_from_overrides() shape).  If None, returns the full dict.
    """
    ov_path = CONFIG_DIR / "corpus_overrides.yaml"
    try:
        # safe_load_unique: a duplicate profession- or STATE-key would otherwise
        # silently drop a sibling-corpus override. Its dup error is a yaml.YAMLError
        # subclass, so the fail-loud branch below already covers it.
        raw = safe_load_unique(ov_path.read_text()) or {}
    except FileNotFoundError:
        return {}
    except (OSError, yaml.YAMLError) as e:
        raise RuntimeError(f"corpus_overrides.yaml unreadable: {e}") from e

    if profession is None:
        return raw
    # Per-profession shape: {STATE: sibling} with state keys upper-cased
    return {str(s).upper(): sib for s, sib in (raw.get(profession) or {}).items() if sib}


def corpus_profession_for(profession: str) -> str:
    """The profession whose harvested text/<X>/ this profession's clean stage reads.
    Normally itself; for a nested occupation declared `parent_corpus: <parent>` in
    professions.yaml it's the parent (so e.g. dental_hygienist cleans from dentistry's
    corpus with no new pull). Mirrors clean_text.corpus_profession_for()."""
    try:
        conf = load_professions()
    except (OSError, yaml.YAMLError) as e:
        # A malformed professions.yaml would otherwise SILENTLY disable every
        # parent_corpus redirect — a nested occupation then cleans from its own
        # (nonexistent) corpus and produces empty results that look like real gaps.
        # Keep the safe fallback, but make the failure VISIBLE.
        log.warning("professions.yaml unreadable (%s) — parent_corpus redirect disabled "
                    "for %s; using its own corpus", e, profession)
        return profession
    return (conf.get(profession, {}) or {}).get("parent_corpus") or profession


def clean_source_profession(profession: str, state: str, base_dir: Path = TEXT_DIR) -> str:
    """Which corpus dir-name under base_dir clean_text reads for this (profession, state):
    a per-state corpus_from sibling when that sibling's file exists under base_dir,
    otherwise the profession's own name (or its parent_corpus). Matches clean_text's
    per-state pick exactly. base_dir is a parameter so provenance can pass its own
    (test-patchable) text root instead of the module-level TEXT_DIR."""
    sib = load_corpus_overrides(profession=profession).get(state.upper())
    if sib and (base_dir / sib / f"{state}.json").exists():
        return sib
    return corpus_profession_for(profession)


def resolve_clean_source(profession: str, state: str, base_dir: Path = TEXT_DIR) -> Path:
    """The exact text/<...>/<STATE>.json that clean_text reads for this (profession,
    state) — the single source of truth for 'what corpus does clean consume', shared by
    clean_text (to read) and provenance (to hash for freshness).

    Because a nested/override profession has NO text/<profession>/ dir of its own, hashing
    that hardcoded path would always be None==None and the cell could never go stale —
    resolving to the real parent/sibling corpus closes that hole."""
    return base_dir / clean_source_profession(profession, state, base_dir) / f"{state}.json"


def load_verified_absences() -> dict:
    """Load config/verified_absences.yaml.

    Shape: {profession: {STATE: {basis, note, citation, ...}}}

    safe_load_unique (not plain yaml.safe_load): a duplicate profession- or
    STATE-key would otherwise be silently dropped last-wins, losing an asserted
    absence without a trace. Raises FileNotFoundError if the file is missing,
    yaml.YAMLError (incl. the duplicate-key error) if it's malformed.
    """
    path = CONFIG_DIR / "verified_absences.yaml"
    return safe_load_unique(path.read_text()) or {}


@functools.lru_cache(maxsize=1)
def load_models() -> dict:
    """Load config/models.yaml — the AI model each paid stage uses.

    Shape: {stage: model_name} for stages 'trim', 'extract', 'schema'.
    Returns {} if the file is missing (each stage then keeps its built-in
    default). Read individual values via model_for(stage, default) so a missing
    file or key falls back cleanly instead of raising.
    """
    path = CONFIG_DIR / "models.yaml"
    if not path.exists():
        return {}
    return safe_load_unique(path.read_text()) or {}


def model_for(stage: str, default: str) -> str:
    """The configured model for a stage (from models.yaml), or `default` if the
    file or key is absent. Lets each stage module keep its historical model name
    as the fallback while making the model a config-file edit, not a code change."""
    return load_models().get(stage) or default


@functools.lru_cache(maxsize=1)
def load_limits() -> dict:
    """Load config/limits.yaml — every data-shaping number in one place.

    Returns the full nested dict.  Callers read individual values with e.g.:
        load_limits()["trim"]["section_text_cap"]

    Cached: the file is read once per process.  The cache is transparent to
    callers; module-level constants in each module stay as the canonical names
    (they just default to the value from load_limits() at import time).
    """
    path = CONFIG_DIR / "limits.yaml"
    return safe_load_unique(path.read_text()) or {}

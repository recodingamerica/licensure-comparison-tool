"""YAML loading that fails loud on duplicate mapping keys.

`yaml.safe_load` silently keeps the LAST of two same-named keys (last-wins),
so a config file with two `WA:` blocks loads with the first one silently
dropped — taking its overrides with it. That bit us with WA/VA/NV in
state_structure.yaml (a whole disciplinary-umbrella block vanished without a
trace). This loader raises instead, turning a silent data loss into a build
failure that points at the offending key and line.
"""

from __future__ import annotations

from pathlib import Path

import yaml


class _DuplicateKeyError(yaml.constructor.ConstructorError):
    pass


class UniqueKeySafeLoader(yaml.SafeLoader):
    """SafeLoader that raises on duplicate keys within any mapping."""


def _construct_mapping(loader: UniqueKeySafeLoader, node, deep=False):
    mapping: dict = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise _DuplicateKeyError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)


def safe_load_unique(text: str):
    """Like yaml.safe_load, but raises on any duplicate mapping key."""
    return yaml.load(text, Loader=UniqueKeySafeLoader)


def load_yaml_file(path: str | Path):
    """Load a YAML file with duplicate-key detection. Returns {} if missing."""
    p = Path(path)
    if not p.exists():
        return {}
    return safe_load_unique(p.read_text()) or {}

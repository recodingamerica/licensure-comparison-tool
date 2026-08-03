# Plan — pin the 8 cells a `match_profession` rebuild breaks (#130)

Self-contained. Everything below was verified on 2026-08-03; nothing is assumed.
Working tree is clean at `70381efd` and the suite is green (954), so start from `main`-clean.

---

## Why this is a plan and not a patch

The obvious move — "pin the committed index values as overrides" — is **wrong for at
least two of the eight cells**, which is why it wasn't done inline. Two cells already
have overrides, and in one of them the override is the thing that's wrong. Read the
per-cell table before editing anything.

The file is `pipeline/config/mapping_overrides.yaml`, ~10,000 lines, and it drives every
corpus mapping in the repo. A bad splice is a bad pull for every profession.

---

## Verified facts you can build on

**1. NJ Justia is FLAT — chapter URLs are not real pages.** Probed:

| url | verdict | `<title>` |
|---|---|---|
| `new-jersey/title-45/chapter-1/` | LIVE | New Jersey Revised Statutes Title 45 (2025) - Profession… |
| `new-jersey/title-45/chapter-6/` | LIVE | *(identical)* |
| `new-jersey/title-45/` | LIVE | *(identical)* |

All three serve the **same title page**. A NJ "chapter" URL 301s to its title. This
matches `pull_text`'s `nj_flat` handling and the CLAUDE.md note.

So a NJ mapping only works if something narrows the title down to one chapter's
sections. There are two mechanisms and BOTH are legitimate:

- **chapter-URL form** — `url: .../title-45/chapter-6/`. `pull_text` derives the chapter
  token via `nj_flat.key_from_chapter_url()` and keeps only `section-45-6-*`. This is
  what the committed indexes use.
- **explicit-pattern form** — `url: .../title-45/` plus
  `section_slug_pattern: "^section-45-5aaa-"`. This is what `construction_trades/NJ`'s
  existing override uses.

**What a rebuild produces is neither**: a bare `title-45/` with **no** pattern, which
pulls all ~2,500 sections of the title unfiltered. That is the bug.

**2. `public_adjuster/OR`'s existing override points at a DEAD url.** Probed:

| url | verdict |
|---|---|
| `oregon/chapter-744/` (the override) | **ERROR** |
| `oregon/volume-18/chapter-744/` (the committed index) | **LIVE** — "Oregon Revised Statutes Chapter 744 (2025) - Insurance Producers" |

Justia's Oregon is volume-scoped. The override is wrong and the index is right — so here
you FIX AN EXISTING ENTRY rather than adding an exclude.

---

## Per-cell prescription

Current override state (checked 2026-08-03):

| cell | override today | action |
|---|---|---|
| `construction_trades/NJ` | `title-45/` + `section_slug_pattern: ^section-45-5aaa-`, via `section_scope` | **LEAVE ALONE.** This is the explicit-pattern form working as designed. The rebuild reproduces it. Not a regression — my #130 table listed it wrongly. |
| `public_adjuster/OR` | `oregon/chapter-744/`, via `gap_locator` | **EDIT IN PLACE**: change the url to `https://law.justia.com/codes/oregon/volume-18/chapter-744/`. Do not add an exclude — there is only one node and it is simply wrong. |
| `dentistry/NJ` | none (profession key exists, no NJ block) | add block: exclude bare `title-45/`, add `chapter-1/` + `chapter-6/` |
| `dietetics/NJ` | none (key exists) | exclude bare `title-45/`, add `chapter-1/` + `chapter-16b/` |
| `public_accountancy/NJ` | none (key exists) | exclude bare `title-45/`, add `chapter-1/` + `chapter-2b/` |
| `electrician/NJ` | none (key exists) | exclude the 6 `section-45-5a-*` urls, add `chapter-5a/` |
| `plumbing/NJ` | none (key exists) | exclude the 2 `section-45-14c-*` urls, add `chapter-14c/` |
| `podiatry/NJ` | **no top-level `podiatry:` key at all** | create the profession key, then the NJ block: exclude bare `title-45/`, add `chapter-1/` + `chapter-5/` |

### The exact URLs

Correct values (these are what the committed indexes hold — verified by reading
`results/profession_index/<prof>.json` at `70381efd`):

```
dentistry/NJ           .../new-jersey/title-45/chapter-1/   .../new-jersey/title-45/chapter-6/
dietetics/NJ           .../new-jersey/title-45/chapter-1/   .../new-jersey/title-45/chapter-16b/
podiatry/NJ            .../new-jersey/title-45/chapter-1/   .../new-jersey/title-45/chapter-5/
public_accountancy/NJ  .../new-jersey/title-45/chapter-1/   .../new-jersey/title-45/chapter-2b/
electrician/NJ         .../new-jersey/title-45/chapter-5a/
plumbing/NJ            .../new-jersey/title-45/chapter-14c/
public_adjuster/OR     .../oregon/volume-18/chapter-744/
```

What to EXCLUDE (what a rebuild produces instead):

```
the 5 whole-title cells:  https://law.justia.com/codes/new-jersey/title-45/
electrician/NJ:           section-45-5a-9/ -9-1/ -11-1/ -11-2/ -13-1/ -55/     (full urls under title-45/)
plumbing/NJ:              section-45-14c-3/ section-45-14c-18-1/               (full urls under title-45/)
```

> Careful: `exclude` matches on exact url string. The rebuild emits ABSOLUTE urls
> (`https://law.justia.com/...`) since `70381efd` normalized them, so write absolute.

### Block shape

Copy the shape already in the file (`professional_engineering/NJ`, added 2026-08-03):

```yaml
  NJ:
    # why this exists, in one or two lines
    exclude:
    - https://law.justia.com/codes/new-jersey/title-45/
    add:
    - url: https://law.justia.com/codes/new-jersey/title-45/chapter-6/
      label: "NJ Title 45 ch. 6 — dentistry (pinned; a rebuild collapses this to the whole title)"
      slug: chapter-6
      via: pinned_2026-08-03
      note: ''
```

---

## Editing method — do NOT round-trip the YAML

`yaml.safe_load` → `yaml.safe_dump` **reformats all ~10,000 lines** (tried it on
2026-08-03: a 7-line change became a 649-line diff, and it silently dropped an existing
`WY` entry). Two safe options:

1. **Hand-edit in the editor.** Seven blocks. Slowest to type, zero tooling risk.
2. **Targeted text insertion** — read the file as text, find the `^<profession>:$` line,
   insert the block immediately after it. Assert the anchor appears exactly once first.
   `podiatry` has no key, so append a new top-level `podiatry:` block at the end instead.

Either way: **one profession per step, `git diff` after each.** The diff should be only
the lines you added.

Profession key line numbers at `70381efd` (they shift as you insert — re-grep each time):

```
construction_trades 1819   dentistry 2574   dietetics 2816   electrician 3010
plumbing 8865   public_accountancy 9922   public_adjuster 10032   podiatry ABSENT
```

---

## Verification — the part that actually proves it

After each edit:

```bash
pipeline/.venv/bin/python -c "import yaml; yaml.safe_load(open('pipeline/config/mapping_overrides.yaml'))"
git diff --stat pipeline/config/mapping_overrides.yaml   # only your lines
```

Then the real test — a rebuild must be a no-op for the published professions:

```bash
SNAP=/tmp/idx_snap; mkdir -p $SNAP; cp pipeline/results/profession_index/*.json $SNAP/
pipeline/.venv/bin/python -m pipeline.discover.match_profession
pipeline/.venv/bin/python - <<'EOF'
import json
from pathlib import Path
from pipeline.paths import published_professions
snap=Path("/tmp/idx_snap"); pub=set(published_professions())
key=lambda n:(str(n.get("url") or ""), str(n.get("via") or ""))
bad=[]
for f in sorted(Path("pipeline/results/profession_index").glob("*.json")):
    if f.stem.startswith("_") or f.stem not in pub or not (snap/f.name).exists(): continue
    b=json.loads((snap/f.name).read_text()); c=json.loads(f.read_text())
    for s in sorted(set(b["by_state"])|set(c["by_state"])):
        nb=sorted(key(n) for n in (b["by_state"].get(s,{}).get("matched") or []))
        nc=sorted(key(n) for n in (c["by_state"].get(s,{}).get("matched") or []))
        if nb!=nc: bad.append((f.stem,s,nb,nc))
print("published cells changed by a rebuild:", len(bad))
for p,s,nb,nc in bad: print(" ",p,s,"\n   was",nb,"\n   now",nc)
EOF
```

**Success = 0 published cells changed.** Until then you are not done.

Note the rebuild also creates ~8 index files for professions in the taxonomy that have
none yet (`asbestos_abatement`, `boxer`, `hawker_peddler`, `managing_general_agent`,
`meat_inspector`, `outfitter_guide`, `pest_control`, `septage_pumper`). They are
untracked and harmless; delete them or leave them, but do not mistake them for churn.

Finally:

```bash
pipeline/.venv/bin/python -m pytest -q          # expect 954+
```

---

## Then, optionally: the guard that makes this permanent

Add a test asserting a rebuild is a no-op for published professions — turn "a rebuild
silently breaks mappings" into a red test. Sketch:

```python
def test_rebuilding_the_index_does_not_change_published_mappings():
    """A generated artifact that changes on a no-op rebuild hides the changes you
    actually made — and on 2026-08-03 a rebuild silently collapsed five NJ cells to
    the whole of Title 45 (~2500 sections). #130."""
    from pipeline.discover.match_profession import rebuild_index
    for prof in published_professions():
        on_disk = json.loads((PROFESSION_INDEX_DIR / f"{prof}.json").read_text())
        rebuilt = rebuild_index(prof)          # in memory; writes nothing
        assert _urls(rebuilt) == _urls(on_disk), prof
```

`rebuild_index(profession)` already exists (`match_profession.py:266`) and does not
write, so the test is cheap and side-effect-free.

---

## Scope discipline

Do **not** re-pull anything as part of this. The committed corpora are correct; this is
purely about making the mapping config survive a rebuild. Pulling is a separate decision
with a separate cost.

Do **not** run `match_profession` and commit the result until the verification above
passes — that is exactly how the 8 cells would get broken for real.

"""Tests for pipeline.discover.match_profession.label_matches.

The label matcher is the load-bearing piece of every (state, profession) pair
that doesn't have a hand-curated override. Locks in:
  - pattern matching is case-insensitive
  - excludes always beat patterns (per-profession excludes)
  - the universal `(Repealed.)` filter applies to every profession (added
    after NM CPA hit Articles 28 + 28A repealed alongside the live 28B)
"""

from pipeline.discover.match_profession import (
    label_matches,
    _umbrella_nodes_for,
    _official_url,
)


CPA_PATTERNS = ["accountant", "accountancy", "public accounting", "certified public account"]
PODIATRY_PATTERNS = ["podiatry", "podiatric", "chiropodist"]


class TestPatternBasics:
    def test_pattern_substring_matches(self):
        assert label_matches("Chapter 12 - ACCOUNTANTS", CPA_PATTERNS, [])

    def test_case_insensitive(self):
        assert label_matches("chapter 1 - ACCOUNTANTS", CPA_PATTERNS, [])
        assert label_matches("CHAPTER 1 - accountants", CPA_PATTERNS, [])

    def test_no_pattern_match(self):
        assert not label_matches("Chapter 99 - Money of Account and Interest", PODIATRY_PATTERNS, [])

    def test_empty_label(self):
        assert not label_matches("", CPA_PATTERNS, [])


class TestExcludes:
    def test_exclude_beats_pattern(self):
        assert not label_matches(
            "Article 99 - Public Health Accounting",
            CPA_PATTERNS,
            excludes=["public health"],
        )

    def test_exclude_is_case_insensitive(self):
        assert not label_matches(
            "Article 99 - PUBLIC HEALTH Accounting",
            CPA_PATTERNS,
            excludes=["public health"],
        )

    def test_no_excludes_no_effect(self):
        assert label_matches("Chapter 1 - Accountants", CPA_PATTERNS, excludes=[])


class TestRepealedUniversalExclude:
    """`(Repealed.)` and variants must filter out for ALL professions.

    Locked in 2026-05-12 after NM CPA returned 3 matches (Articles 28, 28A,
    28B) where two were repealed but the live one was the third — extract
    choked on the empty repealed-text trims.
    """

    def test_repealed_with_period(self):
        # NM-style: "Article 28 - Public Accountants (Repealed.)"
        assert not label_matches("Article 28 - Public Accountants (Repealed.)", CPA_PATTERNS, [])

    def test_repealed_no_period(self):
        assert not label_matches("Chapter 12 - Accountants (Repealed)", CPA_PATTERNS, [])

    def test_repealed_brackets(self):
        assert not label_matches("Chapter 12 - Accountants [Repealed]", CPA_PATTERNS, [])

    def test_repealed_case_insensitive(self):
        assert not label_matches("Article 28 - PODIATRISTS (REPEALED.)", PODIATRY_PATTERNS, [])

    def test_live_version_still_matches(self):
        """The whole point: the active sibling shouldn't be filtered."""
        assert label_matches("Article 28B - 1999 Public Accountancy Act", CPA_PATTERNS, [])

    def test_repealed_applies_even_with_no_pattern_excludes(self):
        # Even if the profession has no `excludes`, repealed still drops
        assert not label_matches("Chapter 30-11 - Podiatry (Repealed.)", PODIATRY_PATTERNS, excludes=[])


class TestUmbrellaNodes:
    """State-level additive umbrella chapters (e.g. WA Ch 18.130 for every WA
    health profession). See the _umbrella_nodes_for docstring in match_profession.py."""

    WA_UMBRELLA = {
        "umbrella": {
            "professions": ["medicine", "nursing", "podiatry"],
            "chapters": [{
                "url": "https://law.justia.com/codes/washington/title-18/chapter-18-130/",
                "label": "WA Ch 18.130 — Uniform Disciplinary Act",
            }],
        }
    }
    WA_TEMPLATE = "https://app.leg.wa.gov/RCW/default.aspx?cite={chapter_dot}&full=true"

    def test_in_scope_profession_gets_node(self):
        nodes = _umbrella_nodes_for(self.WA_UMBRELLA, "medicine", existing_urls=set())
        assert len(nodes) == 1
        assert "18-130" in nodes[0]["url"]
        assert nodes[0]["via"] == "state_structure_umbrella"

    def test_out_of_scope_profession_gets_nothing(self):
        assert _umbrella_nodes_for(self.WA_UMBRELLA, "architecture", set()) == []

    def test_no_umbrella_block(self):
        assert _umbrella_nodes_for({"source": "wa_official"}, "medicine", set()) == []

    def test_already_matched_url_skipped(self):
        url = "https://law.justia.com/codes/washington/title-18/chapter-18-130/"
        assert _umbrella_nodes_for(self.WA_UMBRELLA, "medicine", existing_urls={url}) == []

    def test_template_rewrites_umbrella_to_official_source(self):
        # The umbrella node carries a Justia chapter url; the WA template must
        # rewrite it to the official cite= url (so it's fetched from wa.gov, not
        # Cloudflare-blocked Justia).
        node = _umbrella_nodes_for(self.WA_UMBRELLA, "nursing", set())[0]
        official = _official_url(self.WA_TEMPLATE, node["url"])
        assert official == "https://app.leg.wa.gov/RCW/default.aspx?cite=18.130&full=true"


class TestOfficialUrl:
    """_official_url fills a state's chapter_url_template from a Justia chapter
    url. Load-bearing for every official-source state (WA/VA/SD/NV/CT/NY…)."""

    def test_wa_cite_dot_form(self):
        out = _official_url(
            "https://app.leg.wa.gov/RCW/default.aspx?cite={chapter_dot}&full=true",
            "https://law.justia.com/codes/washington/title-19/chapter-19-28/",
        )
        assert out == "https://app.leg.wa.gov/RCW/default.aspx?cite=19.28&full=true"

    def test_va_title_dot_form(self):
        # VA: title-54-1 → title_dot 54.1
        out = _official_url(
            "https://law.lis.virginia.gov/vacodefull/title{title_dot}/chapter{chapter}/",
            "https://law.justia.com/codes/virginia/title-54-1/chapter-29/",
        )
        assert out == "https://law.lis.virginia.gov/vacodefull/title54.1/chapter29/"

    def test_letter_suffix_uppercased(self):
        # SD-style: chapter-06a → strip zero-pad, upper letter → 6A
        out = _official_url(
            "https://example.gov/{title}-{chapter}",
            "https://law.justia.com/codes/south-dakota/title-36/chapter-06a/",
        )
        assert out == "https://example.gov/36-6A"

    def test_letter_suffix_lowercase_form(self):
        # CT-style template uses the _lc form
        out = _official_url(
            "https://www.cga.ct.gov/current/pub/chap_{chapter_lc}.htm",
            "https://law.justia.com/codes/connecticut/title-20/chapter-393b/",
        )
        assert out == "https://www.cga.ct.gov/current/pub/chap_393b.htm"

    def test_missing_placeholder_returns_none(self):
        # Template needs {section} but the Justia url has no section segment.
        out = _official_url(
            "https://example.gov/{title}/{chapter}/{section}",
            "https://law.justia.com/codes/washington/title-18/chapter-18-130/",
        )
        assert out is None

    def test_zero_padding_stripped(self):
        out = _official_url(
            "{chapter}",
            "https://law.justia.com/codes/x/title-1/chapter-007/",
        )
        assert out == "7"


class TestRebuildIsANoOp:
    """A rebuild must not change which SECTIONS a published cell maps to.

    profession_index/*.json is generated, so a hand repair written straight into it is
    silently discarded the next time anyone runs match_profession -- and because a
    rebuild also rewrites unrelated cells, the loss hides in the noise. On 2026-08-03
    that had already happened: electrician/NJ fell from chapter-5A's 71 sections to 6
    loose ones, plumbing/NJ from 37 to 2, and public_adjuster/OR lost the "volume-18"
    segment Justia requires. The repairs now live in config (#130); this keeps them there.

    Compares resolved section SETS, not node urls -- the same chapter is legitimately
    expressible as a chapter url or as a title url plus a section_slug_pattern (NJ is
    flat, so both forms are in use), and url form alone is not a mapping change.
    """

    def _resolve(self, state, node, hierarchy_urls):
        """The set of section urls a node actually pulls, per the committed hierarchy."""
        import re

        from pipeline.ingest import nj_flat

        slug = lambda u: u.rstrip("/").rsplit("/", 1)[-1]  # noqa: E731
        pattern = node.get("section_slug_pattern")
        if pattern:
            rx = re.compile(pattern)
            return frozenset(u for u in hierarchy_urls if slug(u) and rx.match(slug(u)))
        url = (node.get("url") or "").rstrip("/")
        key = nj_flat.key_from_chapter_url(url) if state == "NJ" else None
        if key:
            rx = nj_flat.section_slug_re(key)
            return frozenset(u for u in hierarchy_urls if rx.match(slug(u)))
        # An ordinary nested node: compare the url itself, minus the scheme/host and
        # year segments that f49c11bc normalized (committed indexes predate it).
        year = re.compile(r"^(19|20)\d\d$")
        bare = re.sub(r"^https?://[^/]+", "", url)
        return frozenset([tuple(s for s in bare.split("/") if s and not year.match(s))])

    def test_rebuilding_does_not_change_published_mappings(self):
        import json

        from pipeline.discover.match_profession import rebuild_index
        from pipeline.paths import (
            HIERARCHY_DIR,
            PROFESSION_INDEX_DIR,
            published_professions,
        )

        hierarchies = {}
        for path in HIERARCHY_DIR.glob("*.json"):
            data = json.loads(path.read_text())
            hierarchies[data.get("state")] = [
                c.get("url") or "" for c in (data.get("chapters") or [])
            ]

        changed = []
        for profession in sorted(published_professions()):
            index_path = PROFESSION_INDEX_DIR / f"{profession}.json"
            if not index_path.exists():
                continue
            committed = json.loads(index_path.read_text())
            rebuilt = rebuild_index(profession)  # in memory; writes nothing
            states = set(committed["by_state"]) | set(rebuilt["by_state"])
            for state in sorted(states):
                urls = hierarchies.get(state) or []
                sets = []
                for index in (committed, rebuilt):
                    nodes = (index["by_state"].get(state) or {}).get("matched") or []
                    sets.append(frozenset().union(
                        *[self._resolve(state, n, urls) for n in nodes]) if nodes
                        else frozenset())
                if sets[0] != sets[1]:
                    changed.append(f"{profession}/{state}: "
                                   f"{len(sets[0])} -> {len(sets[1])} sections")

        assert not changed, (
            "a rebuild would change these published cells' mappings; the fix belongs in "
            "config/state_structure.yaml or config/mapping_overrides.yaml, NOT in the "
            "generated profession_index:\n  " + "\n  ".join(changed))

    def test_nj_corpus_matches_what_the_index_maps(self):
        """Every NJ cell's committed corpus is exactly what its mapping resolves to.

        The rebuild guard above compares the index to a rebuild, so it cannot see a cell
        where BOTH agree on the wrong answer. That is how architecture/NJ and hvac/NJ hid:
        their indexes held loose section nodes (15 and 4) while the committed corpora held
        whole chapters (148 and 42), and the corpus was the only witness. A re-pull would
        have silently collapsed them.

        SCOPED TO NJ ON PURPOSE. NJ is flat -- the mapping is a title url plus a
        section_slug_pattern, and results/hierarchy/NJ.json is the complete flat list of
        title-45 sections, so the pattern alone resolves exactly. In a nested state a
        pattern is relative to its node's chapter, and matching it against a whole state's
        hierarchy both over-matches (MA repeats section-43 in many chapters of a title) and
        under-matches (OR's hierarchy is chapter-level, so no section slug appears at all).
        Generalizing this needs container-scoped resolution; it is not that the other
        states are broken.
        """
        import json
        import re

        from pipeline.paths import (
            HIERARCHY_DIR,
            PROFESSION_INDEX_DIR,
            TEXT_DIR,
            published_professions,
        )

        hierarchy = json.loads((HIERARCHY_DIR / "NJ.json").read_text())
        all_slugs = [
            (c.get("url") or "").rstrip("/").rsplit("/", 1)[-1]
            for c in (hierarchy.get("chapters") or [])
        ]

        mismatched, checked = [], 0
        for profession in sorted(published_professions()):
            index_path = PROFESSION_INDEX_DIR / f"{profession}.json"
            corpus_path = TEXT_DIR / profession / "NJ.json"
            if not index_path.exists() or not corpus_path.exists():
                continue
            index = json.loads(index_path.read_text())
            nodes = ((index.get("by_state") or {}).get("NJ") or {}).get("matched") or []
            patterns = [n["section_slug_pattern"] for n in nodes
                        if n.get("section_slug_pattern")]
            if not patterns:
                continue  # e.g. public_adjuster/NJ maps into title-17, not flat title-45
            checked += 1
            resolved = {s for s in all_slugs
                        if any(re.match(p, s) for p in patterns)}
            corpus = {(s.get("url") or "").rstrip("/").rsplit("/", 1)[-1]
                      for s in (json.loads(corpus_path.read_text()).get("sections") or [])}
            if resolved != corpus:
                mismatched.append(
                    f"{profession}/NJ: corpus {len(corpus)} vs mapping {len(resolved)} "
                    f"(corpus-only {len(corpus - resolved)}, mapping-only "
                    f"{len(resolved - corpus)})")

        assert checked >= 12, f"expected the NJ title-45 cells, only checked {checked}"
        assert not mismatched, (
            "these NJ cells' committed corpus is not what their mapping would pull, so a "
            "re-pull would change the data underneath them:\n  " + "\n  ".join(mismatched))

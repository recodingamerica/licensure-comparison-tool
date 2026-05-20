"""Single source of truth for "where in the original source text does this
verbatim quote live?".

The verifier (extract_state.py / reverify_evidence.py) calls
`quote_in_corpus(quote, normalized_combined_corpus)` to decide whether the
LLM hallucinated a quote — that's a boolean.

The frontend's yellow-highlight feature needs the same answer, but with
character offsets, against a SINGLE section's text — call
`locate_quote_in_section(quote, section_text)` and it returns a list of
(start, end) spans that index back into `section_text` exactly, so the
UI can do `text.slice(start, end)` without re-deriving the matcher.

Keeping both behind one normalizer (`normalize_with_mapping`) is the whole
point: when the matcher accepts a quote, it accepts the same text the
frontend will highlight. See STATUS.md "Two implementations of the same
matcher" for the parity problem this replaces.
"""

from __future__ import annotations

import re


# Smart typography -> ASCII. Same set as the TS SMART_MAP in
# pipeline/publish/web/src/lib/format.ts; mostly 1-to-1 except the ellipsis
# char which expands to three dots.
_SMART_MAP: dict[str, str] = {
    # curly single quotes
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    # curly double quotes
    "“": '"', "”": '"', "„": '"', "‟": '"',
    # dashes
    "–": "-", "—": "-", "−": "-",
    # NBSP and other "odd" spaces -> regular space
    " ": " ", " ": " ", " ": " ", " ": " ",
    # ellipsis
    "…": "...",
}

# Parenthesized list markers — (1) (a) (iv) (IV). Stripped BEFORE the
# non-alnum pass so they don't degrade into bare "1"/"a"/"i" tokens that
# would either spuriously match prose-quoted lists or tempt us to strip all
# bare single letters (which causes real false positives — see
# test_article_swap_a_vs_the).
#
# We intentionally do NOT also strip bare-form markers (e.g. `1.` `A.` at
# line start). Statute drafters often render those inline when prosed
# together (`as prescribed by this chapter: 1. Practices dentistry…`), and
# the LLM routinely quotes the inline form verbatim. Stripping bare markers
# from the corpus is asymmetric — the quote keeps the `1` (mid-stream, not
# at line start), the corpus loses it, and the substring search fails. We
# measured: corpus-side bare stripping fixes ~26 LLM-elided quotes across
# professions but newly breaks ~74 LLM-kept-inline ones. Net loss. LLM-
# elided list-marker quotes remain `unverified` — that's the verifier
# correctly flagging a tiny paraphrase.
_LIST_MARKER_AT_START_RE = re.compile(
    r"^\(\s*(?:\d{1,3}|[a-z]|[ivxIVX]+)\s*\)",
    re.IGNORECASE,
)

# List markers are short; bound the lookahead so the regex stays cheap.
_LIST_MARKER_PROBE_LEN = 12

_ALNUM_OR_SPACE_RE = re.compile(r"[a-z0-9 ]")

# Ellipsis splitter for the quote side. Matches "..." (with optional spaces
# between dots) or a single ellipsis char. Same regex as Python's old
# _ELLIPSIS_SPLIT and the TS ELLIPSIS_SPLIT_RE.
_ELLIPSIS_SPLIT_RE = re.compile(r"\s*(?:\.\s*\.\s*\.|…)\s*")

# Below this many normalized characters, a substring match isn't strong
# enough to count as verification (or to safely highlight). Mirrors the TS
# threshold so both sides agree on which segments count.
_MIN_SEGMENT_LEN = 8


def normalize_with_mapping(text: str) -> tuple[str, list[int]]:
    """Normalize text AND return a per-character map back to the source.

    Returns (normalized, src_index) where:
      * normalized — lowercased / list-marker-stripped / non-alnum→space /
        whitespace-collapsed
      * src_index[i] = the index in the ORIGINAL text that normalized[i]
        came from; len(src_index) == len(normalized)

    Callers can locate a substring in `normalized`, then translate the
    match boundaries back to original-text offsets via src_index — without
    re-implementing any of the normalization rules.

    Mirrors `normalizeWithMapping` in pipeline/publish/web/src/lib/format.ts;
    when build_frontend.py emits quote_spans, that TS code goes away and
    this function becomes the lone matcher.
    """
    # Stage 1: walk char by char. Skip list markers wholesale (no
    # placeholder), expand smart-quote chars (some map to multiple output
    # chars — e.g. … -> ...), remember the ORIGINAL index each emitted
    # char came from.
    stage1_chars: list[str] = []
    stage1_src: list[int] = []
    i = 0
    n = len(text)
    while i < n:
        probe = text[i : i + _LIST_MARKER_PROBE_LEN]
        m = _LIST_MARKER_AT_START_RE.match(probe)
        if m:
            i += m.end()
            continue
        ch = text[i]
        mapped = _SMART_MAP.get(ch, ch)
        for k in range(len(mapped)):
            stage1_chars.append(mapped[k])
            stage1_src.append(i)
        i += 1

    # Stage 2: lowercase; replace non-[a-z0-9 ] with space; collapse runs
    # of spaces; trim leading/trailing. src_index stays aligned at every
    # step.
    out_chars: list[str] = []
    out_src: list[int] = []
    last_was_space = True  # suppresses leading space
    for ch, src in zip(stage1_chars, stage1_src):
        c = ch.lower()
        if not _ALNUM_OR_SPACE_RE.match(c):
            c = " "
        if c == " ":
            if last_was_space:
                continue
            last_was_space = True
        else:
            last_was_space = False
        out_chars.append(c)
        out_src.append(src)
    while out_chars and out_chars[-1] == " ":
        out_chars.pop()
        out_src.pop()
    return "".join(out_chars), out_src


def normalize_for_match(text: str) -> str:
    """Convenience: just the normalized string with no index map. Output
    matches the legacy `_normalize_for_match` in extract_state.py for all
    non-degenerate inputs (the one edge case is a list marker glued
    directly to alphanumerics with no surrounding whitespace — the legacy
    path inserts a space at the seam, this path doesn't; the TS side never
    inserted one either, so this is the behavior we want)."""
    return normalize_with_mapping(text)[0]


def _split_quote_to_segments(quote: str) -> list[str]:
    """Split a quote on ellipsis, normalize each part, drop parts whose
    normalized form is shorter than _MIN_SEGMENT_LEN. Returned segments
    are the NORMALIZED forms, in source order."""
    segments: list[str] = []
    for raw in _ELLIPSIS_SPLIT_RE.split(quote):
        raw = raw.strip()
        if not raw:
            continue
        nq = normalize_for_match(raw)
        if len(nq) >= _MIN_SEGMENT_LEN:
            segments.append(nq)
    return segments


def locate_quote_in_section(
    quote: str, section_text: str
) -> list[tuple[int, int]] | None:
    """Locate each ellipsis-split segment of `quote` inside `section_text`
    and return spans (start, end) that index into the ORIGINAL section_text.

    Returns None if the quote is empty, if no segment is long enough to
    verify, or if any segment can't be found in order after the previous
    segment's end. A None result means: don't ship a highlight; the
    verifier may still pass against the combined corpus.

    Use these spans on the frontend as `section_text.slice(start, end)` to
    paint the yellow mark.
    """
    if not quote:
        return None
    segments = _split_quote_to_segments(quote)
    if not segments:
        return None

    norm_section, src_index = normalize_with_mapping(section_text)

    spans: list[tuple[int, int]] = []
    cursor = 0
    for nq in segments:
        idx = norm_section.find(nq, cursor)
        if idx < 0:
            return None
        src_start = src_index[idx]
        src_end = src_index[idx + len(nq) - 1] + 1
        spans.append((src_start, src_end))
        cursor = idx + len(nq)
    return spans


def quote_in_corpus(quote: str, normalized_corpus: str) -> bool:
    """Bool form: True iff each ellipsis-split segment of `quote` appears
    in order in `normalized_corpus` (already normalized via
    normalize_for_match).

    Kept alongside locate_quote_in_section because the verifier still
    needs the looser "match anywhere in the combined chapter+umbrella
    corpus" check — see STATUS.md's corpus-boundary edge case: a quote
    can span the seam between sections and verify against the combined
    text without belonging cleanly to any single section."""
    if not quote:
        return False
    segments = _split_quote_to_segments(quote)
    if not segments:
        return False
    cursor = 0
    for nq in segments:
        idx = normalized_corpus.find(nq, cursor)
        if idx < 0:
            return False
        cursor = idx + len(nq)
    return True

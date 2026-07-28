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
frontend will highlight. See docs/STATUS.md "Two implementations of the same
matcher" for the parity problem this replaces.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher


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

# Quote-side segment splitter. When the LLM supports a claim it routinely
# stitches together NON-ADJACENT source passages, and it marks the seam in one
# of a few recurring ways: an explicit ellipsis, an em/en-dash join (" — "), a
# semicolon between enumerated clauses, or a plain sentence boundary (". ").
# We split on all of them, then require each resulting segment to appear
# verbatim AND in source order (see quote_in_corpus / locate_quote_in_section).
#
# Why this is safe to broaden: splitting can only ever let us accept MORE real
# text. A reordered or fabricated segment still fails the in-order substring
# search, so a paraphrase never passes (see test_paraphrase_returns_false /
# test_*_out_of_order_returns_false). Crucially, unlike corpus-side list-marker
# stripping (see _LIST_MARKER_AT_START_RE) this touches NO normalization — it
# only chooses where to cut the quote — so it carries none of that asymmetry
# risk. The ellipsis branch is listed first so "..." is consumed whole before
# the bare-sentence-boundary branch can fire inside it.
#
# Measured impact (2026-06): flips 28 genuinely-verbatim-but-pieced quotes from
# unverified→verified across the published professions (e.g. a state's
# semicolon-delimited scope list, or two verbatim definitions the model joined
# with a period), while every quote with a real character-level discrepancy
# stays flagged.
_SEGMENT_SPLIT_RE = re.compile(
    r"\s*(?:\.\s*\.\s*\.|…)\s*"  # ellipsis: "..." (spaces ok) or "…"
    r"|\s+[-–—−]\s+"            # spaced dash join: " — "
    r"|;\s+"                     # semicolon between clauses
    r"|\.\s+"                    # sentence boundary: ". "
)

# The original, narrower splitter — ellipsis only. We still try this FIRST so
# that broadening is purely ADDITIVE: any quote that verified as one contiguous
# (or ellipsis-elided) span keeps verifying exactly as before. Finer splitting
# can otherwise regress a quote — a short early segment may match at an earlier,
# wrong position and overshoot the in-order cursor — so we only fall through to
# the broadened split when the narrow one doesn't already succeed.
_ELLIPSIS_SPLIT_RE = re.compile(r"\s*(?:\.\s*\.\s*\.|…)\s*")

# Below this many normalized characters, a substring match isn't strong
# enough to count as verification (or to safely highlight). Mirrors the TS
# threshold so both sides agree on which segments count.
_MIN_SEGMENT_LEN = 8


# Inline legislative-history annotations the LLM naturally elides when it
# pulls a quote. We strip them by replacing each match with same-length
# spaces so `src_index` continues to map normalized → original positions.
# Patterns are conservative — anchored by a year + chapter token so we
# don't accidentally swallow substantive text.
_ANNOTATION_PATTERNS = [
    # Maine bracketed history: "[PL 1997, c. 265, §1 (AMD).]"
    # Often a whole line containing one or more PL/P.L. references inside [ ].
    re.compile(
        r"\[\s*P\.?\s*L\.?\s+\d{4}[^\]]{0,300}\]",
        re.IGNORECASE,
    ),
    # Bare "PL 1997, c. 265, §1 (AMD)" at end of sentence/paragraph (no brackets).
    re.compile(
        r"\bP\.?\s*L\.?\s+\d{4}\s*,\s*c\.?\s*\d+[^.)\]\n]{0,80}(?:\([A-Z]+\)\.?)?",
        re.IGNORECASE,
    ),
    # Nevada-style "(Added to NRS by 1987, 1524; A 1991, 790; 2013, 2071)"
    re.compile(
        r"\(\s*(?:Added\s+to\s+|Amended\s+by\s+)?NRS\s+by[^)]{0,300}\)",
        re.IGNORECASE,
    ),
    # Bracketed year+chapter: "[2020, c. 5, §1.]" / "[1999, c. 245, §1 (NEW).]"
    re.compile(
        r"\[\s*\d{4}\s*,\s*c\.?\s*\d+[^\]]{0,80}\]",
    ),
    # "(L. 1995, S.B. 1014)" / "L. 1995, c. 12, §3" — generic acts-of citation
    re.compile(
        r"\bL\.\s*\d{4}\s*,\s*(?:c\.?\s*\d+|S\.?B\.?\s*\d+|H\.?B\.?\s*\d+)[^.)]{0,80}",
    ),
]


def _strip_annotations(text: str) -> str:
    """Replace annotation runs with same-length spaces. Length-preserving so
    downstream src_index mapping stays aligned with the original text."""
    out = text
    for pat in _ANNOTATION_PATTERNS:
        out = pat.sub(lambda m: " " * len(m.group(0)), out)
    return out


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
    # Stage 0: strip embedded legislative annotations (length-preserving
    # so src_index still maps to original-text positions).
    text = _strip_annotations(text)

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


def _split_quote_to_segments(
    quote: str, split_re: re.Pattern[str] = _SEGMENT_SPLIT_RE
) -> list[str]:
    """Split a quote on any seam the LLM uses to join non-adjacent passages
    (by default ellipsis, dash join, semicolon, sentence boundary — see
    _SEGMENT_SPLIT_RE), normalize each part, and drop parts whose normalized
    form is shorter than _MIN_SEGMENT_LEN. Pass `split_re=_ELLIPSIS_SPLIT_RE`
    for the original ellipsis-only behavior. Returned segments are the
    NORMALIZED forms, in source order."""
    segments: list[str] = []
    for raw in split_re.split(quote):
        raw = raw.strip()
        if not raw:
            continue
        nq = normalize_for_match(raw)
        if len(nq) >= _MIN_SEGMENT_LEN:
            segments.append(nq)
    return segments


def _segments_found_in_order(segments: list[str], normalized_corpus: str) -> bool:
    """True iff every segment appears in `normalized_corpus`, each at or after
    the end of the previous segment's match."""
    return _place_segments(segments, normalized_corpus) is not None


# --- unmarked elision -------------------------------------------------------------
#
# The seam-splitting above only works when the model LEFT a seam: an ellipsis, a dash, a
# semicolon. It often doesn't. DE § 307 reads
#
#   "The Board shall adopt accreditation decisions of the NAAB and shall adopt
#    regulations governing education ..."
#
# and the quote came back as "The Board shall adopt regulations governing education ...",
# silently dropping the middle clause. Every word is genuinely in the statute, but no
# contiguous run contains the whole quote and there is no punctuation to split on, so the
# seam strategies find nothing. Measured across all 13 professions: 633 quotes cite a
# section we DO have but can't be located in it, and ~340 of those are >=95% coverable as
# <=3 contiguous runs -- i.e. real quotes with interior elisions.
#
# So the last resort segments by CONTENT rather than punctuation: take difflib's matching
# blocks (already monotonic in both sequences, which is exactly the in-order requirement),
# keep the substantial ones, and accept only if they cover nearly all of the quote in a
# few pieces. Thresholds are deliberately strict -- a quote that needs many small pieces
# is a paraphrase, and highlighting scattered words would misrepresent it as a quotation.
_ELISION_MIN_RUN = 20        # normalized chars; shorter "runs" are coincidental word hits
_ELISION_MAX_RUNS = 3        # more pieces than this is a paraphrase, not an elided quote
_ELISION_MIN_COVERAGE = 0.95 # the quote must be almost entirely present, just discontiguous
_ELISION_ANCHOR = 24         # cheap pre-check before the O(n*m) block diff


def _segments_by_elision(normalized_quote: str, normalized_corpus: str) -> list[str]:
    """Segment a quote by CONTENT for the unmarked-elision case. [] if it doesn't qualify.

    Guarded by an anchor probe first: the quote's opening must appear at all, which is a
    cheap `find` and skips the expensive diff for the overwhelmingly common case of a
    quote that simply isn't in this section (build_state_browse tests every quote against
    every section, so that path must stay fast).
    """
    if len(normalized_quote) < _ELISION_MIN_RUN:
        return []
    # Probe a few positions, not just the head: the elision can fall INSIDE the opening
    # window (DE § 307 drops a clause four words in, so the first 24 chars of the quote
    # are not contiguous anywhere), and anchoring only at the start missed exactly the
    # case this exists to catch. Any one probe hitting is enough to justify the diff.
    n = len(normalized_quote)
    probes = {
        normalized_quote[:_ELISION_ANCHOR],
        normalized_quote[max(0, n // 2 - _ELISION_ANCHOR // 2):][:_ELISION_ANCHOR],
        normalized_quote[-_ELISION_ANCHOR:],
    }
    if not any(p and p in normalized_corpus for p in probes):
        return []
    # Greedy longest-prefix walk, not difflib's matching blocks. difflib optimises for the
    # single longest common run, which here matched the SECOND "shall adopt" in the
    # section and orphaned the quote's opening "The Board" as an 8-char fragment -- so the
    # highlight began mid-word at "d shall adopt". Taking the longest prefix of what's
    # left, repeatedly, instead ends each run exactly where the texts diverge, which is a
    # word boundary, and yields the two pieces a reader expects.
    segments: list[str] = []
    i = cursor = covered = 0
    n = len(normalized_quote)
    while i < n:
        while i < n and normalized_quote[i] == " ":
            i += 1
        if i >= n:
            break
        # Longest L with quote[i:i+L] present at/after cursor. Monotonic (if a prefix of
        # length L is present, so is one of L-1), so binary search rather than scan.
        lo, hi, best = _ELISION_MIN_RUN, n - i, 0
        while lo <= hi:
            mid = (lo + hi) // 2
            if normalized_corpus.find(normalized_quote[i : i + mid], cursor) >= 0:
                best, lo = mid, mid + 1
            else:
                hi = mid - 1
        if best < _ELISION_MIN_RUN:
            return []
        piece = normalized_quote[i : i + best]
        cursor = normalized_corpus.find(piece, cursor) + best
        segments.append(piece)
        covered += best
        i += best
        if len(segments) > _ELISION_MAX_RUNS:
            return []
    if not segments or covered / n < _ELISION_MIN_COVERAGE:
        return []
    return segments


def _place_segments(
    segments: list[str], norm_section: str, src_index: list[int] | None = None
) -> list[tuple[int, int]] | None:
    """Find every segment in order, each at or after the previous one's end.

    THE one placement loop. Returns spans into the original text when `src_index` is
    given, otherwise an empty-but-not-None list on success — so callers that only need a
    yes/no check share this code instead of keeping their own copy of the walk.
    """
    if not segments:
        return None
    spans: list[tuple[int, int]] = []
    cursor = 0
    for nq in segments:
        idx = norm_section.find(nq, cursor)
        if idx < 0:
            return None
        if src_index is not None:
            spans.append((src_index[idx], src_index[idx + len(nq) - 1] + 1))
        cursor = idx + len(nq)
    return spans


def _locate(
    quote: str,
    norm_section: str,
    src_index: list[int] | None,
    segments_narrow: list[str] | None = None,
    segments_broad: list[str] | None = None,
    normalized_quote: str | None = None,
) -> list[tuple[int, int]] | None:
    """THE strategy ladder, in one place: narrow seams, then broad seams, then unmarked
    elision. Narrow-first keeps every previously-working highlight byte-for-byte
    identical, so each new rung is purely additive -- it can only place a quote that
    placed nowhere before, never move one that already placed.

    Callers that match one quote against many sections pass precomputed segment lists to
    skip re-normalizing the quote per section.
    """
    if not quote:
        return None
    if segments_narrow is None:
        segments_narrow = _split_quote_to_segments(quote, _ELLIPSIS_SPLIT_RE)
    if segments_broad is None:
        segments_broad = _split_quote_to_segments(quote, _SEGMENT_SPLIT_RE)
    for segments in (segments_narrow, segments_broad):
        placed = _place_segments(segments, norm_section, src_index)
        if placed is not None:
            return placed
    # Last resort: the quote is verbatim but discontiguous, with no seam to split on.
    # Normalizing the whole quote is the expensive char-walk, so callers matching one
    # quote against MANY sections pass it in precomputed; otherwise do it here, and only
    # here -- the seam rungs above never need it.
    whole = normalized_quote if normalized_quote is not None else normalize_for_match(quote)
    return _place_segments(
        _segments_by_elision(whole, norm_section), norm_section, src_index
    )


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

    norm_section, src_index = normalize_with_mapping(section_text)
    return locate_quote_in_normalized(quote, norm_section, src_index)


def locate_quote_in_normalized(
    quote: str, norm_section: str, src_index: list[int]
) -> list[tuple[int, int]] | None:
    """Same as `locate_quote_in_section`, but takes the section already
    normalized via `normalize_with_mapping`. Lets a caller that matches MANY
    quotes against ONE section normalize it a single time instead of per quote
    — the normalization is the expensive part (char-by-char walk), so this is
    the hot path for build_state_browse's cross-profession evidence aggregation.
    Behavior is byte-for-byte identical to the inline version it replaced.
    """
    return _locate(quote, norm_section, src_index)


def split_quote_segments(quote: str) -> tuple[list[str], list[str]]:
    """Precompute a quote's (narrow, broad) normalized segment lists ONCE, so a
    caller matching the same quote against MANY sections doesn't re-normalize
    the quote per section (the dominant cost in build_state_browse). Narrow =
    ellipsis-only split, broad = full seam split — same two passes, same order,
    as locate_quote_in_section."""
    return (
        _split_quote_to_segments(quote, _ELLIPSIS_SPLIT_RE),
        _split_quote_to_segments(quote, _SEGMENT_SPLIT_RE),
    )


def locate_segments_in_normalized(
    segments_narrow: list[str], segments_broad: list[str],
    norm_section: str, src_index: list[int],
    normalized_quote: str = "",
) -> list[tuple[int, int]] | None:
    """Like locate_quote_in_normalized, but takes the quote already split into
    normalized segments via split_quote_segments — so BOTH the section and the
    quote are normalized once and reused. Same ladder, same result."""
    return _locate(normalized_quote, norm_section, src_index,
                   segments_narrow=segments_narrow, segments_broad=segments_broad,
                   normalized_quote=normalized_quote)


def quote_fuzzy_match(
    quote: str, normalized_corpus: str, *, min_ratio: float = 0.7
) -> dict | None:
    """Fuzzy fallback when `quote_in_corpus` returns False.

    Returns {"ratio": float, "matched_normalized": str} when the LONGEST
    contiguous matching block between the normalized quote and the
    normalized corpus covers at least `min_ratio` of the quote's
    normalized length.

    `ratio` here = longest_block_size / len(normalized_quote). We
    deliberately ignore smaller scattered matches because the sum of
    short fragments can artificially inflate to 1.0 when every common
    word appears separately — that flagged paraphrases as perfect
    matches in early testing. Longest-block is a conservative anchor:
    "the LLM verbatim-quoted at least this much of the source."

    Only called on entries that already failed strict verification.
    """
    import difflib

    nq = normalize_for_match(quote)
    if not nq or len(nq) < _MIN_SEGMENT_LEN:
        return None
    sm = difflib.SequenceMatcher(None, nq, normalized_corpus, autojunk=False)
    longest = sm.find_longest_match(0, len(nq), 0, len(normalized_corpus))
    if longest.size < _MIN_SEGMENT_LEN:
        return None
    ratio = longest.size / len(nq)
    if ratio < min_ratio:
        return None
    matched = normalized_corpus[longest.b : longest.b + longest.size]
    return {"ratio": round(ratio, 3), "matched_normalized": matched}


def quote_in_corpus(quote: str, normalized_corpus: str) -> bool:
    """Bool form: True iff the quote's segments appear in order in
    `normalized_corpus` (already normalized via normalize_for_match).

    We try the narrow ellipsis-only segmentation first, then the broadened
    one (dash/semicolon/sentence joins). Narrow-first makes the broadening
    purely ADDITIVE: anything that verified as one contiguous/ellipsis span
    still verifies, and the broadened split can only ADD passes for genuinely
    pieced-but-verbatim quotes — never flip a prior pass to a fail.

    Kept alongside locate_quote_in_section because the verifier still
    needs the looser "match anywhere in the combined chapter+umbrella
    corpus" check — see docs/STATUS.md's corpus-boundary edge case: a quote
    can span the seam between sections and verify against the combined
    text without belonging cleanly to any single section."""
    if not quote:
        return False
    # Same ladder the highlighter uses -- so "verified" and "highlightable" can never
    # mean different things. Passing src_index=None makes it a pure yes/no.
    return _locate(quote, normalized_corpus, None) is not None

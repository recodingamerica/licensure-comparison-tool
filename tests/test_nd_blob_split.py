"""ND chapter pages are one inline blob (no per-section links); split_nd_blob splits
them on line-anchored "title-chapter-section." markers. The title may be dotted
(26.1 Insurance, 4.1 Agriculture) — the original regex only handled plain-integer
titles, so those chapters silently never split (0 markers → stayed a blob)."""

from pipeline.ingest.pull_text import split_nd_blob, looks_like_nd_blob

URL = "https://law.justia.com/codes/north-dakota/title-26-1/chapter-26-1-26/"

DOTTED = (
    "Go to Previous Versions\n2025 North Dakota Century Code\nCHAPTER 26.1-26\n"
    "26.1-26-01. Scope.\nThis chapter applies to producers.\n"
    "26.1-26-02. Definitions.\nAs used in this chapter...\n"
    "26.1-26-03. License required.\nA person may not act without a license.\n"
)
PLAIN = (
    "CHAPTER 43-09\n"
    "43-09-01. Definitions.\nAs used...\n"
    "43-09-02. License.\nRequired.\n"
    "43-09-03. Renewal.\nAnnual.\n"
)


def test_dotted_title_splits():
    secs = split_nd_blob(DOTTED, URL)
    assert [s.citation for s in secs] == ["26.1-26-01", "26.1-26-02", "26.1-26-03"]
    assert secs[0].label.startswith("26.1-26-01. Scope")
    assert "producers" in secs[0].text
    # nav chrome before the first marker is dropped
    assert "Previous Versions" not in " ".join(s.text for s in secs)


def test_plain_integer_title_still_splits():
    secs = split_nd_blob(PLAIN, "https://law.justia.com/codes/north-dakota/title-43/chapter-43-09/")
    assert [s.citation for s in secs] == ["43-09-01", "43-09-02", "43-09-03"]


def test_looks_like_nd_blob_needs_three_markers_and_nd_url():
    assert looks_like_nd_blob(DOTTED, URL) is True
    one = "26.1-26-01. Only one.\nbody\n"
    assert looks_like_nd_blob(one, URL) is False          # <3 markers → not a splittable blob
    assert looks_like_nd_blob(DOTTED, "https://law.justia.com/codes/utah/x/") is False  # non-ND


def test_fewer_than_three_markers_returns_empty():
    assert split_nd_blob("26.1-26-01. Only one.\nbody\n", URL) == []

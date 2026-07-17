"""resplit_blobs: a LOCAL transform that splits a committed single-section ND/IL
inline-act blob into per-section records (reusing pull_text's split_nd_blob /
split_il_inline), and leaves everything else untouched."""

from pipeline.ingest.resplit_blobs import resplit_corpus

ND_URL = "https://law.justia.com/codes/north-dakota/title-26-1/chapter-26-1-26/"
BLOB = (
    "nav chrome\n"
    "26.1-26-01. Scope.\nbody one\n"
    "26.1-26-02. Definitions.\nbody two\n"
    "26.1-26-03. License.\nbody three\n"
)


def test_splits_a_committed_nd_blob():
    d = {"sections": [{"url": ND_URL, "label": "Chapter 26.1-26", "citation": "26.1-26",
                       "text": BLOB, "text_len": len(BLOB), "error": None}],
         "total_chars": len(BLOB)}
    out = resplit_corpus(d)
    assert out is not None
    assert [s["citation"] for s in out["sections"]] == ["26.1-26-01", "26.1-26-02", "26.1-26-03"]
    assert out["total_chars"] == sum(s["text_len"] for s in out["sections"])
    assert "nav chrome" not in " ".join(s["text"] for s in out["sections"])


def test_non_blob_corpus_untouched():
    d = {"sections": [{"url": "https://law.justia.com/codes/x/title-1/section-1/", "citation": "1",
                       "text": "real section", "text_len": 12, "error": None},
                      {"url": "https://law.justia.com/codes/x/title-1/section-2/", "citation": "2",
                       "text": "another", "text_len": 7, "error": None}]}
    assert resplit_corpus(d) is None          # already multi-section — nothing to split


def test_single_marker_chapter_untouched():
    one = {"sections": [{"url": ND_URL, "citation": "26.1-26", "text": "26.1-26-01. Only.\nbody\n",
                         "text_len": 22, "error": None}]}
    assert resplit_corpus(one) is None        # <2 sections → left as-is


def test_errored_blob_untouched():
    d = {"sections": [{"url": ND_URL, "citation": "26.1-26", "text": BLOB, "text_len": len(BLOB),
                       "error": "soft-404"}]}
    assert resplit_corpus(d) is None

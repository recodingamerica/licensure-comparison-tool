"""_null_out_invalid_paths recovers a record by nulling the smallest subtree around
a drifted-enum leaf — including leaves inside lists, which previously couldn't be
reached and dropped the ENTIRE state as an extraction gap."""

from pipeline.extract.extract_state import _null_out_invalid_paths


def test_field_inside_a_list_element_is_nulled_not_whole_state():
    # The regression: a bad enum in exams[1].degree_level. The offending field is
    # nulled; its sibling element and its own siblings are untouched.
    data = {"profession_specific": {"exams": [
        {"name": "written", "degree_level": "bachelors"},
        {"name": "practical", "degree_level": "NOT_A_LEVEL"},
    ]}}
    errs = [{"loc": ("profession_specific", "exams", 1, "degree_level")}]
    assert _null_out_invalid_paths(data, errs) == 1
    exams = data["profession_specific"]["exams"]
    assert exams[1]["degree_level"] is None      # offending leaf nulled
    assert exams[1]["name"] == "practical"       # rest of the element intact
    assert exams[0]["degree_level"] == "bachelors"  # sibling element untouched


def test_bad_list_element_nulls_the_whole_list():
    # A bad element of a list[Literal] field can't be nulled in place -> drop the list.
    data = {"licensure": {"tags": ["ok", "BAD_TAG"]}}
    errs = [{"loc": ("licensure", "tags", 1)}]
    assert _null_out_invalid_paths(data, errs) == 1
    assert data["licensure"]["tags"] is None


def test_evidence_wrapper_value_nulls_the_wrapper():
    data = {"licensure": {"credential_type": {"value": None, "quote": "q", "citation": "c"}}}
    errs = [{"loc": ("licensure", "credential_type", "value")}]
    assert _null_out_invalid_paths(data, errs) == 1
    assert data["licensure"]["credential_type"] is None


def test_plain_optional_field_nulled():
    data = {"licensure": {"regulatory_model": "BAD_RUNG"}}
    errs = [{"loc": ("licensure", "regulatory_model")}]
    assert _null_out_invalid_paths(data, errs) == 1
    assert data["licensure"]["regulatory_model"] is None


def test_unknown_path_is_skipped_not_crashed():
    data = {"licensure": {}}
    errs = [{"loc": ("licensure", "does_not_exist")}]
    assert _null_out_invalid_paths(data, errs) == 0  # nothing to null, no crash

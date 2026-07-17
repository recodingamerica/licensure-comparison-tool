"""Test that pipeline.client.dashboard fully renders — every placeholder replaced and
the status data embedded intact. A leftover __PLACEHOLDER__ would ship a broken page."""

import json

from pipeline.client import dashboard


def test_dashboard_replaces_all_placeholders(tmp_path, monkeypatch):
    canned = {
        "cost_model": {"trim": 0.05, "extract": 0.15},
        "totals": {"professions": 1, "cells_done": 0, "cells_ready": 1,
                   "cells_needs_fetch": 0, "cost_to_finish_ready": 0.2},
        "professions": {"court_reporter": {
            "states": {"UT": {"stage": "pulled", "cost": 0.2}},
            "summary": {"done": 0, "ready": 1, "needs_fetch": 0, "absent": 0,
                        "unknown": 0, "cost_to_finish_ready": 0.2, "cost_to_finish_all": 0.2},
        }},
    }
    monkeypatch.setattr(dashboard, "build", lambda: canned)
    monkeypatch.setattr(dashboard, "HTML_OUT", tmp_path / "dashboard.html")
    # main() ALSO mirrors to WEB_PUBLIC_DIR/dashboard/index.html — redirect it too, or
    # every test run overwrites the committed web dashboard with this 1-profession fixture.
    monkeypatch.setattr(dashboard, "WEB_PUBLIC_DIR", tmp_path / "web_public")

    dashboard.main()
    html = (tmp_path / "dashboard.html").read_text()

    for ph in ("__DATA__", "__PY__", "__TRIM__", "__EXTRACT__"):
        assert ph not in html, f"unreplaced placeholder {ph}"
    # the full status object is embedded verbatim
    assert json.dumps(canned) in html
    # the venv python path and the profession made it into the page
    assert dashboard.PY in html
    assert "court_reporter" in html

"""Pre-generate the download workbooks and upload them to Blob, plus a small
`downloads_index.json` the Downloads page reads to build its links.

For every published occupation → `data/downloads/occupation/<prof>.xlsx`, and every state
that has a browse blob → `data/downloads/state/<ST>.xlsx` (each a 3-tab workbook via
pipeline.client.export_data). The index maps each to its public Blob URL. Runs in the
publish fanout so downloads regenerate whenever data changes; uploads are content-hash
skipped, so unchanged workbooks cost nothing.

  python -m pipeline.publish.build_downloads
"""

from __future__ import annotations

import json

from pipeline.client.export_data import (
    export_occupation, export_state, _published_professions, EXPORT_DIR, DATA_DIR,
)
from pipeline.publish.blob_upload import upload_bytes, upload_json

XLSX_CT = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
STATE_NAMES = json.loads((DATA_DIR.parent / "public" / "states.json").read_text()) \
    if (DATA_DIR.parent / "public" / "states.json").exists() else None


def _states_with_data() -> list[str]:
    d = DATA_DIR / "state"
    return sorted(f.stem for f in d.glob("*.json")) if d.exists() else []


def build_and_upload() -> dict:
    occupations = []
    for prof in _published_professions():
        out = EXPORT_DIR / f"{prof}.xlsx"
        export_occupation(prof, out)
        url, _ = upload_bytes(f"data/downloads/occupation/{prof}.xlsx", out.read_bytes(), XLSX_CT)
        display = json.loads((DATA_DIR / f"{prof}.json").read_text()).get("display", prof)
        occupations.append({"id": prof, "display": display, "url": url})

    states = []
    for code in _states_with_data():
        out = EXPORT_DIR / f"state_{code}.xlsx"
        export_state(code, out)
        url, _ = upload_bytes(f"data/downloads/state/{code}.xlsx", out.read_bytes(), XLSX_CT)
        states.append({"code": code, "url": url})

    index = {"occupations": occupations, "states": states}
    upload_json("data/downloads_index.json", json.dumps(index, indent=2))
    return index


def main() -> None:
    idx = build_and_upload()
    print(f"downloads: {len(idx['occupations'])} occupations + {len(idx['states'])} states "
          f"uploaded to Blob + downloads_index.json")


if __name__ == "__main__":
    main()

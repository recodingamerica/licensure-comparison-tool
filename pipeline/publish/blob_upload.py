"""Upload JSON payloads to Vercel Blob via the @vercel/blob SDK.

We shell out to a tiny Node helper (web/scripts/upload-blob.mjs) so the
official SDK does the work — handles auth, content-types, overwrite
semantics — instead of re-implementing the HTTP API in Python.

Reads BLOB_READ_WRITE_TOKEN from web/.env.local, pulled there by
`vercel env pull`.

CONTENT-HASH SKIP: every upload is content-addressed against a local manifest
(`results/.upload_manifest.json`, pathname → {hash, url}). If a pathname's body
hashes the same as what was last uploaded, the upload is SKIPPED and the cached
URL returned. This makes every uploader (build_frontend's ~50 browse files per
profession, state_browse, umbrella_browse, tag_sheet, scorecard) incremental
for free — only genuinely-changed files spawn a node process + hit the network.
Safe because the live site fetches Blob by listing, so an unchanged file just
stays as-is. Set BLOB_FORCE_UPLOAD=1 to re-upload everything (e.g. if the Blob
store was wiped); `refresh_all --force` sets it.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess

from pipeline.paths import PIPELINE_ROOT, RESULTS_DIR

WEB_DIR = PIPELINE_ROOT / "publish" / "web"
ENV_FILE = WEB_DIR / ".env.local"
UPLOAD_SCRIPT = WEB_DIR / "scripts" / "upload-blob.mjs"
_MANIFEST_PATH = RESULTS_DIR / ".upload_manifest.json"

# Loaded once per process, persisted to disk whenever an entry changes (so the
# skip survives across the separate build_frontend/… subprocess invocations a
# refresh_all run spawns).
_manifest_cache: dict[str, dict] | None = None


def _manifest() -> dict[str, dict]:
    global _manifest_cache
    if _manifest_cache is None:
        try:
            _manifest_cache = json.loads(_MANIFEST_PATH.read_text())
        except Exception:
            _manifest_cache = {}
    return _manifest_cache


def _force_upload() -> bool:
    return os.environ.get("BLOB_FORCE_UPLOAD", "").lower() in ("1", "true", "yes")


def upload_json(pathname: str, body: str) -> tuple[str, bool]:
    """Upload a JSON string to Blob at the given pathname.

    Returns (public_url, skipped). `skipped` is True when `body` is
    byte-identical to the last upload for this pathname and the network call was
    avoided (unless BLOB_FORCE_UPLOAD is set) — so callers can log honestly."""
    if not ENV_FILE.exists():
        raise RuntimeError(
            f"{ENV_FILE} missing — run `cd pipeline/publish/web && vercel env pull .env.local` first"
        )

    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    man = _manifest()
    prev = man.get(pathname)
    if not _force_upload() and prev and prev.get("hash") == digest and prev.get("url"):
        return prev["url"], True  # unchanged — skipped the node spawn + network

    proc = subprocess.run(
        ["node", f"--env-file={ENV_FILE}", str(UPLOAD_SCRIPT), pathname],
        input=body,
        capture_output=True,
        text=True,
        cwd=WEB_DIR,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"upload-blob.mjs failed for {pathname}:\nstderr: {proc.stderr}"
        )
    url = proc.stdout.strip()
    man[pathname] = {"hash": digest, "url": url}
    _MANIFEST_PATH.write_text(json.dumps(man, indent=2))
    return url, False

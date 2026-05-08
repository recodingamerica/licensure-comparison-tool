"""Upload JSON payloads to Vercel Blob via the @vercel/blob SDK.

We shell out to a tiny Node helper (web/scripts/upload-blob.mjs) so the
official SDK does the work — handles auth, content-types, overwrite
semantics — instead of re-implementing the HTTP API in Python.

Reads BLOB_READ_WRITE_TOKEN from web/.env.local, pulled there by
`vercel env pull`.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from paths import PIPELINE_ROOT

WEB_DIR = PIPELINE_ROOT / "publish" / "web"
ENV_FILE = WEB_DIR / ".env.local"
UPLOAD_SCRIPT = WEB_DIR / "scripts" / "upload-blob.mjs"


def upload_json(pathname: str, body: str) -> str:
    """Upload a JSON string to Blob at the given pathname; return the public URL."""
    if not ENV_FILE.exists():
        raise RuntimeError(
            f"{ENV_FILE} missing — run `cd pipeline/publish/web && vercel env pull .env.local` first"
        )
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
    return proc.stdout.strip()

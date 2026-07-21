#!/bin/bash
# One-time setup for the state-licensing pipeline. Run this ONCE after cloning/receiving
# the repo. It creates the Python environment, installs everything, and checks your API
# key. After it finishes you never run it again — you use the dashboard + the four
# commands (see SETUP.md and docs/runbooks/client_refetch.md).
#
#   bash setup.sh
#
# Safe to re-run: it skips steps that are already done.

set -euo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"   # repo root, wherever this script lives

VENV="pipeline/.venv"
PY="$VENV/bin/python"
say() { printf '\n\033[1m%s\033[0m\n' "$*"; }   # bold section headers
ok()  { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn(){ printf '  \033[33m!\033[0m %s\n' "$*"; }

# --- 1. Python (need 3.11+) --------------------------------------------------------
say "1/4  Checking Python"
if ! command -v python3 >/dev/null 2>&1; then
  echo "  ✗ python3 is not installed. Install Python 3.11+ from https://www.python.org/downloads/ and re-run."
  exit 1
fi
PYVER=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)'; then
  echo "  ✗ Found Python $PYVER, but 3.11 or newer is required. Please install a newer Python and re-run."
  exit 1
fi
ok "Python $PYVER"

# --- 2. Virtual environment + packages --------------------------------------------
say "2/4  Installing the pipeline (this can take a few minutes the first time)"
if [ ! -x "$PY" ]; then
  python3 -m venv "$VENV"
  ok "created the environment ($VENV)"
else
  ok "environment already exists ($VENV) — reusing it"
fi
"$PY" -m pip install --quiet --upgrade pip
"$PY" -m pip install --quiet -r pipeline/requirements.txt
ok "installed all Python packages"

# --- 3. The fetch browser (only needed to re-fetch a changed state later) ----------
say "3/4  Fetch browser (optional — only needed to re-fetch statutes later)"
echo "  The repo you received is already fetched, so you can skip this. It downloads a"
echo "  headless browser used ONLY by 'refetch.sh' when a state changes its law."
if "$PY" -m scrapling install >/dev/null 2>&1; then
  ok "fetch browser ready (you can re-fetch states)"
else
  warn "couldn't install the fetch browser now — that's fine. Everyday work (clean/trim/"
  warn "extract/publish) doesn't need it. To enable re-fetching later, run:  $PY -m scrapling install"
fi

# --- 4. API key (needed only for the two paid steps: trim + extract) ---------------
say "4/4  API key (needed only for the 'trim' and 'extract' steps)"
if [ -f .env ] && grep -qE '^(ANTHROPIC|CLAUDE)_API_KEY=.+' .env; then
  ok "found an API key in .env"
elif [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  ok "found ANTHROPIC_API_KEY in your environment"
else
  cat > .env <<'ENV'
# Paste your Anthropic API key after the = sign (no quotes, no spaces), then save.
# It is used only by the paid 'trim' and 'extract' steps. This file is git-ignored.
ANTHROPIC_API_KEY=
ENV
  warn "no API key yet — I created a .env file. Open it, paste your key after"
  warn "'ANTHROPIC_API_KEY=', and save. (You only need this for trim/extract.)"
fi

# --- done -------------------------------------------------------------------------
say "Setup complete."
cat <<EOF
  You're ready. From here on you only use these:

    See what's there:   $PY -m pipeline.client.dashboard   (opens a page you tick occupations on)
    Free step:          $PY -m pipeline.client.run clean   --professions <name>
    Paid (~\$0.05/state): $PY -m pipeline.client.run trim    --professions <name>
    Paid (~\$0.15/state): $PY -m pipeline.client.run extract --professions <name>
    Publish (free):     $PY -m pipeline.client.run publish --professions <name>

  Plain-English walkthrough:  docs/runbooks/client_refetch.md
  Setup notes / troubleshooting:  SETUP.md
EOF

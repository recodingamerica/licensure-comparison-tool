"""Single source for scrape throttle.

The per-host delay lives in config/limits.yaml (fetch.per_host_delay_seconds)
so it's visible alongside every other data/risk knob; env PULL_HOST_DELAY
overrides it for a run. This is a BLOCK-RISK knob — too low and Cloudflare
rate-blocks the CDP session mid-run. Every discovery crawler that imports
PER_HOST_DELAY picks up the configured value here.
"""

from __future__ import annotations

import os

from pipeline.config.loaders import load_limits

try:
    PER_HOST_DELAY = float(os.environ.get(
        "PULL_HOST_DELAY", str(load_limits()["fetch"]["per_host_delay_seconds"])))
except (ValueError, KeyError):
    PER_HOST_DELAY = 3.0  # seconds between fetches against one host

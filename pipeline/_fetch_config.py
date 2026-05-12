"""Single source for scrape throttle.

Justia handles ~3 req/s from one IP without complaining. Lower this if you
start seeing 429s; raise if Justia tightens up. Centralizing here means one
edit instead of five.
"""

from __future__ import annotations

PER_HOST_DELAY = 0.3  # seconds to sleep between fetches against one host

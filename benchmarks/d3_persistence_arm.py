"""Historical name for the promoted D3 arm.

The matched source-frequency denominator was promoted into the shipped
``SleepService`` on 2026-11-10. This module remains so the frozen D3 runners and their
records keep a stable import; the class no longer changes behavior.
"""

from __future__ import annotations

from organica.sleep import SleepService


class MatchedFrequencySleepService(SleepService):
    """Compatibility name for the engine that now carries the matched-frequency repair."""

"""The D3 fixed arm: matched source-frequency decay, in process, no engine change.

The preregistration is `docs/D3-PERSISTENCE-PREREGISTRATION.md`. This module implements only the
treatment arm it names. Nothing here runs a cell, and no file under `organica/` is changed.

The shipped strength denominator is the raw tag frequency, which grows without bound on a
repeated stimulus while the temporal count it divides decays. `MatchedFrequencySleepService`
maintains a per-tag denominator with the same 0.95 decay as the temporal graph, so a re-presented
edge is not diluted by its own history. Every other constant and rule is inherited unchanged.
"""

from __future__ import annotations

from organica.sleep import SleepService


class MatchedFrequencySleepService(SleepService):
    """The shipped engine plus a decayed source-frequency denominator."""

    FREQUENCY_DECAY = 0.95

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._decayed_freqs: dict[str, float] = {}
        self._last_raw: dict[str, float] = {}
        self._cycle_key = None
        self.frequency_updates = 0

    def _update(self, raw: dict[str, int]) -> dict[str, float]:
        """One cycle's decayed counter: D = 0.95 * D_previous + the raw count delta."""
        raw = {tag: float(count) for tag, count in raw.items()}
        if not self._decayed_freqs:
            self._decayed_freqs = dict(raw)
        else:
            tags = set(raw) | set(self._decayed_freqs) | set(self._last_raw)
            self._decayed_freqs = {
                tag: (self.FREQUENCY_DECAY * self._decayed_freqs.get(tag, 0.0)
                      + max(0.0, raw.get(tag, 0.0) - self._last_raw.get(tag, 0.0)))
                for tag in tags
            }
        self._last_raw = raw
        self.frequency_updates += 1
        return self._decayed_freqs

    def _predict_frequencies(self, raw: dict[str, int]) -> dict[str, float]:
        """Update once per sleep cycle, so a second prediction call cannot apply a delta twice."""
        key = self.memory.latest_sleep_cycle()
        if key != self._cycle_key:
            self._cycle_key = key
            self._update(raw)
        return self._decayed_freqs

    def _build_predictions(self, temporal, freqs):
        return super()._build_predictions(temporal, self._predict_frequencies(freqs))

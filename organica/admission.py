"""The adopted admission rule: diversity-first ordering over the source side.

Adopted on the confirmatory evidence recorded in `docs/DECISION-ADMISSION-RULE.md`
and registered in `docs/RANKING-ADMISSION-PREREGISTRATION.md`. The rule changes
*which eligible candidate occupies a budget slot*; eligibility, candidate
construction, strength, the count filter and the caps are untouched.

Two orderings live here. ``DIVERSITY`` is adopted; ``COUNT`` is the frozen
engine's own rule, kept so that every published count-basis measurement stays
reproducible and so that the claim "only the ordering changed" is checkable:

* ``COUNT``      — top-k by count, the frozen engine's rule.
* ``DIVERSITY``  — each slot takes the candidate whose left-hand tag owns the
  fewest already-admitted outgoing edges; ties break on count, then on the
  stable key.

``organica/sleep.py`` is frozen and is never edited. The adopted rule therefore
arrives the way this repository already changes a frozen layer: by subclassing
(``DiversityFirstSleepService``), so the reference class keeps the reference
behaviour and ``tests/test_admission_rule.py`` can show that the count arm
reproduces it exactly.

No third-party dependencies, and the frozen engine does not import this module.
"""
from __future__ import annotations

from .sleep import PredictionCandidate, SleepService, _make_id

#: The reference engine's rule: top-k by count.
COUNT = "count"
#: The adopted rule: fewest already-admitted outgoing edges per source.
DIVERSITY = "diversity"
POLICIES = (COUNT, DIVERSITY)
#: The rule an engine version adopts unless it says otherwise.
DEFAULT_POLICY = DIVERSITY


def _count(candidate: PredictionCandidate) -> int:
    return int(candidate.evidence.get("temporal_count", 0))


def _check(policy: str) -> str:
    if policy not in POLICIES:
        raise ValueError("unknown admission policy %r; known: %r"
                         % (policy, list(POLICIES)))
    return policy


def effective_cap(cap: int, eligible_sources: int,
                  policy: str = DEFAULT_POLICY) -> int:
    """The budget floor the decision records.

    Under the adopted rule the cap must be at least the number of eligible
    source tags, because below that the diversity order has at most one slot
    per source and degenerates toward count order. This is a **floor, not an
    increase**: at the engine's own caps in a 16-source world it returns the cap
    unchanged, which is what the confirmatory block relied on.

    The count rule is not a diversity order and has no floor.
    """
    policy = _check(policy)
    if policy == COUNT:
        return int(cap)
    if int(eligible_sources) < 0:
        raise ValueError("eligible_sources cannot be negative")
    return max(int(cap), int(eligible_sources))


def rank(predictions: list[PredictionCandidate], k: int,
         policy: str = DEFAULT_POLICY) -> list[PredictionCandidate]:
    """The first ``k`` candidates the policy admits, in admission order.

    ``COUNT`` is the frozen engine's rule exactly: a stable sort by descending
    count, then truncation. It deliberately adds no secondary key, because the
    engine's own sort adds none and a tie would otherwise be reordered.
    """
    policy = _check(policy)
    k = int(k)
    if k <= 0:
        return []
    if policy == COUNT:
        return sorted(predictions, key=lambda p: -_count(p))[:k]

    remaining = sorted(predictions, key=lambda p: (-_count(p), p.source, p.target))
    per_source: dict[str, int] = {}
    chosen: list[PredictionCandidate] = []
    while remaining and len(chosen) < k:
        best = min(remaining,
                   key=lambda p: (per_source.get(p.source, 0), -_count(p),
                                  p.source, p.target))
        chosen.append(best)
        per_source[best.source] = per_source.get(best.source, 0) + 1
        remaining.remove(best)
    return chosen


class DiversityFirstSleepService(SleepService):
    """``SleepService`` with the adopted admission rule.

    Under ``COUNT`` the override **delegates to the engine** and returns exactly
    the admission ``SleepService`` would have returned, so the reference
    behaviour is preserved by construction rather than re-implemented here.

    Under ``DIVERSITY`` the engine's eligible pool is ranked by the adopted
    order and admitted up to the floor-guarded budget. Candidate construction,
    the ``PREDICTION_MIN_COUNT`` filter, strengths and evidence remain the
    engine's own; what the adopted order supersedes is the engine's stratified
    transition/co-occurrence quota, which has no notion of a source and so
    cannot express a diversity order. That consequence is disclosed in
    `docs/DECISION-ADMISSION-RULE.md` §5.
    """

    #: ``COUNT`` reproduces the reference engine; ``DIVERSITY`` is adopted.
    admission_policy = DEFAULT_POLICY

    #: A budget large enough that the engine's own truncation cannot bind. It is
    #: used only to see the eligible pool, and is restored in a ``finally``.
    _POOL_PROBE = 1_000_000

    def _build_predictions(self, temporal, freqs, prior_schemas=None):
        if self.admission_policy == COUNT:
            return super()._build_predictions(temporal, freqs, prior_schemas)

        cap = self.MAX_PREDICTIONS
        try:
            self.MAX_PREDICTIONS = self._POOL_PROBE
            pool = list(super()._build_predictions(temporal, freqs, prior_schemas))
        finally:
            self.MAX_PREDICTIONS = cap

        eligible_sources = len({p.source for p in pool})
        budget = effective_cap(cap, eligible_sources, self.admission_policy)
        return rank(pool, budget, self.admission_policy)

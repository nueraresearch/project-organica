"""Guard the confidence-amendment harness against its own protocol.

Three things can go wrong with a harness like this, and each is checked here:

1. **The parameterisation is not the frozen formula.**  With ``alpha = beta = 0``
   the copy must return *exactly* the value the frozen engine computes, including
   on a zero denominator.  If it does not, C1 is measuring a different engine and
   the whole study is void.
2. **The constants drift from the protocol.**  The arm names, the stream names,
   the seed block and the 40-cycle horizon are the pre-registration's; a change
   here without a dated amendment would re-score the protocol.
3. **The formula does not do what the mechanism says.**  The amendment's premise
   is that a small-sample minority survives instead of being diluted -- so the
   test pins one case where the share dies and the posterior lives, and one where
   both agree, so a later edit cannot quietly make the claim unfalsifiable.

Nothing here runs a cell or reads a result.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "benchmarks"))

import confidence_posterior as cp  # noqa: E402


def test_the_constants_are_the_protocol_s():
    assert cp.CYCLES == 40
    assert cp.SEEDS == list(range(700001001, 700001013))
    assert cp.RESERVE == (700001013, 700001024)
    assert cp.ARMS == ("share", "jeffreys", "laplace")
    assert cp.CONTROL_ARM == "share_reimplemented"
    assert set(cp.STREAMS) == {
        "baseline", "no_branch", "cold_start", "cold_start_unbranched",
        "real_git_history", "wide_lookback",
    }


def test_the_grid_is_the_declared_size():
    cells = len(cp.ARMS) * len(cp.STREAMS) * len(cp.SEEDS)
    assert cells == 216
    # The control arm adds its own cells on top of the declared grid.
    assert len((cp.ARMS + (cp.CONTROL_ARM,))) * len(cp.STREAMS) * len(cp.SEEDS) == 288


@pytest.mark.parametrize("support,contradiction", [
    (0, 0), (1, 0), (3, 1), (1, 6), (10, 10), (2, 40), (0, 5),
])
def test_the_zero_prior_reduces_to_the_frozen_formula(support, contradiction):
    frozen = (round(support / (support + contradiction), 4)
              if (support + contradiction) > 0 else 0.0)
    assert cp.confidence(support, contradiction, 0.0, 0.0) == frozen


def test_the_mechanism_moves_in_the_direction_the_protocol_claims():
    # A minority expectation the share kills and the posterior keeps alive.
    assert cp.confidence(1, 6, 0.0, 0.0) < 0.15
    assert cp.confidence(1, 6, 0.5, 0.5) >= 0.15
    # A genuinely split subject stays near one half under both.
    assert cp.confidence(10, 10, 0.5, 0.5) == 0.5
    assert cp.confidence(10, 10, 1.0, 1.0) == 0.5
    # And the posterior cannot rescue a minority that is simply small.
    assert cp.confidence(2, 40, 0.5, 0.5) < 0.15


def test_the_arms_map_to_the_declared_priors():
    assert cp.ALPHA_BETA["jeffreys"] == (0.5, 0.5)
    assert cp.ALPHA_BETA["laplace"] == (1.0, 1.0)
    assert cp.ALPHA_BETA[cp.CONTROL_ARM] == (0.0, 0.0)


def test_the_posterior_subclass_copies_the_hypothesis_method():
    # If the frozen engine ever grows a new branch in this method, the copy
    # would silently miss it.  Compare the two bodies as source text: they must
    # differ only in the amendment's expression.
    import inspect
    from organica import SleepService as Frozen

    frozen = inspect.getsource(Frozen._form_and_test_hypotheses)
    copied = inspect.getsource(cp.PosteriorSleep._form_and_test_hypotheses)
    assert "support / (support + contradiction)" in frozen
    assert "support / (support + contradiction)" not in copied
    assert "confidence(support, contradiction, self.ALPHA, self.BETA)" in copied
    # The death rule must be identical, since the amendment moves confidence
    # and not the threshold at which a belief is culled.
    death = "if conf < self.DEATH_THRESHOLD and (support + contradiction) >= 3:"
    assert death in frozen
    assert death in copied
    # Retention and the marker allowance are not part of the amendment.
    for tail in ("_belief_info(beliefs, prior_hyps, temporal)",
                 "_retain_hypotheses(beliefs, info, temporal)",
                 "_retain_markers(markers, info)"):
        assert tail in frozen
        assert tail in copied


def test_the_streams_come_from_the_cold_start_study_unchanged():
    git_events = ["a commit message about parsing", "another about caching"]
    for name in cp.STREAMS:
        spec = cp.stream_spec(name, git_events)
        assert spec["events"], f"{name} has no stream"
        assert spec["per_cycle"] in (1, 8)
    # The lookback ablation must be the same memory variant, not a new one.
    assert cp.stream_spec("wide_lookback", git_events)["memory_cls"] is not None
    assert cp.stream_spec("baseline", git_events)["memory_cls"] is not \
        cp.stream_spec("wide_lookback", git_events)["memory_cls"]

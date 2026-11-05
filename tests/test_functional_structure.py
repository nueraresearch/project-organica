"""The scoring layer must reproduce the house scorer and its gate must fire."""
from __future__ import annotations

import random

import pytest

from benchmarks import acquisition_baselines as ab
from benchmarks import functional_structure as fs


def _fixture(seed: int = 0, events: int = 12):
    rng = random.Random(seed)
    vocab = [f"tag{i}" for i in range(6)]
    ctx = [rng.sample(vocab, 2) for _ in range(events)]
    obs = [rng.sample(vocab, 2) for _ in range(events)]
    table = {(a, b): rng.uniform(0.02, 0.98) for a in vocab for b in vocab}

    def prob(a: str, b: str) -> float:
        return table[(a, b)]

    return vocab, ctx, obs, prob


@pytest.mark.parametrize("seed", [0, 1, 2])
@pytest.mark.parametrize("exclude_self", [True, False])
def test_matches_the_house_scorer(seed: int, exclude_self: bool):
    vocab, ctx, obs, prob = _fixture(seed)
    ours = fs.score(prob, ctx, obs, vocab, exclude_self=exclude_self)["log_loss"]
    # The house scorer intersects the vocabulary, so it needs a set.
    house = ab.score(prob, ctx, obs, set(vocab), exclude_self=exclude_self)["log_loss"]
    assert ours == pytest.approx(house, abs=1e-6)


def test_denominator_counts_every_cell_including_b_equal_a():
    vocab, ctx, obs, prob = _fixture()
    n = fs.score(prob, ctx, obs, vocab)["cells"]
    assert n == sum(len(c) for c in ctx) * len(vocab)


def test_two_tag_events_contribute_two_sources():
    vocab = ["aaaa", "bbbb", "cccc"]
    ctx = [["aaaa", "bbbb"]]
    obs = [["cccc"]]
    cs = fs.cells(lambda a, b: 0.5, ctx, obs, vocab)
    assert len(cs) == 2 * len(vocab)
    assert sum(c["y"] for c in cs) == 2


def test_attribution_ignores_unrealised_cells():
    """A large improvement on a cell that did not occur must not move the share."""
    base, org, prov = fs._fixture(n_world=2, n_self=3)
    extra_base = {"pair": 99, "source": "zzzz", "target": "yyyy", "y": 0, "p": 0.5}
    extra_org = {"pair": 99, "source": "zzzz", "target": "yyyy", "y": 0, "p": 0.999}
    prov2 = dict(prov)
    prov2[("zzzz", "yyyy")] = (0, 500)
    with_extra = fs.attribute(base + [extra_base], org + [extra_org], prov2)
    plain = fs.attribute(base, org, prov)
    assert with_extra["share_self"] == pytest.approx(plain["share_self"])


def test_tie_counts_against_the_claim():
    assert fs.classify_pair(4, 4) == "self"
    assert fs.classify_pair(5, 4) == "world"
    assert fs.classify_pair(0, 0) == "unattributed"


def test_gate_fixtures_fire_every_outcome():
    report = fs.gate_fixtures()
    assert {r["status"] for r in report} >= set(fs.STATUSES)


def test_gate_can_fail_when_the_rule_is_broken(monkeypatch):
    """The gate is not decoration: a non-firing rule must make it raise."""
    def never_withholds(base, org, provenance, threshold=fs.THRESHOLD):
        return {"status": fs.STATUS_WORLD, "withheld": False, "threshold": threshold,
                "margin_positive": 1.0, "share_world": 1.0, "share_self": 0.0,
                "share_unattributed": 0.0, "counts": {}}

    monkeypatch.setattr(fs, "attribute", never_withholds)
    with pytest.raises(AssertionError):
        fs.gate_fixtures()

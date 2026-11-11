"""Controls for the pair-resolver stability rule and page."""

from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json

from benchmarks.pair_resolver_stability import (
    ARTIFACT,
    BUCKETS,
    PAGE,
    PUBLISHED,
    label_for,
    render,
)


def _cell(seed=1, denominator=14, resolved=8, polarity=6, control=False):
    return {
        "seed": seed,
        "control": control,
        "denominator": denominator,
        "resolved": resolved,
        "polarity_only": polarity,
        "share": (resolved / denominator) if denominator else None,
        "single_role_resolved": 0,
    }


def _control(**kwargs):
    return _cell(seed=20261101, control=True, **kwargs)


def test_a_moved_control_blocks_the_reading():
    assert label_for(_control(resolved=7), [_cell()]) == "CONTROL_FAILED"


def test_a_missing_control_blocks_the_reading():
    assert label_for(None, [_cell()]) == "CONTROL_FAILED"


def test_an_exact_reproduction_on_every_fresh_seed_is_stable():
    assert label_for(_control(), [_cell(seed=2), _cell(seed=3)]) == "STABLE_SPLIT"


def test_a_moved_resolved_count_keeps_the_denominator_but_not_the_split():
    assert label_for(_control(), [_cell(seed=2, resolved=7)]) == "DENOMINATOR_STABLE"


def test_a_moved_denominator_is_variable():
    assert label_for(_control(), [_cell(seed=2, denominator=12, resolved=8)]) == "VARIABLE_DENOMINATOR"


def test_a_zero_denominator_is_not_measurable_not_zero():
    assert label_for(_control(), [_cell(seed=2, denominator=0, resolved=0, polarity=0)]) == "INCOMPLETE_DENOMINATOR"


def test_no_fresh_cells_is_not_a_stability_claim():
    assert label_for(_control(), []) == "INCOMPLETE_DENOMINATOR"


def test_every_declared_bucket_is_reachable():
    seen = {
        label_for(None, []),
        label_for(_control(), [_cell(seed=2, denominator=0, resolved=0, polarity=0)]),
        label_for(_control(), [_cell(seed=2)]),
        label_for(_control(), [_cell(seed=2, polarity=5)]),
        label_for(_control(), [_cell(seed=2, denominator=13)]),
    }
    assert seen == set(BUCKETS)


def test_the_page_is_the_render_of_the_artifact_and_names_its_label():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["label"] in BUCKETS
    assert artifact["published"] == PUBLISHED
    assert PAGE.read_text(encoding="utf-8") == render(artifact)
    assert artifact["label"] in render(artifact)
    assert "{}" not in render(artifact)

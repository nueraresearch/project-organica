"""Each frozen presence block has a bounded canary that fails on a digest change.

The canary is one 120-cycle cell, not a campaign: it answers "does the engine still produce what
the frozen block recorded?" and nothing else. `test_the_runners_can_go_red` is the control the
project requires of every check -- it breaks a runner path and requires the canary to report it.
"""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import block_canaries as bc  # noqa: E402

BLOCKS = bc.frozen_blocks()


def test_every_frozen_block_has_a_canary():
    assert BLOCKS == ["PRESENCE-CAP-1", "PRESENCE-CONSTRUCT-1",
                      "PRESENCE-CONVERSION-1", "PRESENCE-CONVERSION-2"]
    recorded = bc.load()["cells"]
    assert sorted(recorded) == BLOCKS
    assert bc.load()["cycles"] == 120


@pytest.mark.parametrize("block", BLOCKS)
def test_the_canary_matches_the_recorded_digest(block):
    assert bc.check(only=block) == []


def test_the_runners_can_go_red():
    """The control: a broken runner path must be reported, not silently skipped."""
    block = "PRESENCE-CAP-1"
    problems = bc.check(only=block, runner_override="benchmarks.presence_cap_experiment:no_such_cell")
    assert problems, "a broken runner path must fail the canary"
    assert any("PRESENCE-CAP-1" in problem and "cannot run" in problem for problem in problems), problems
    assert any("does not resolve" in problem for problem in problems), problems


def test_a_changed_digest_is_reported():
    committed = json.loads(json.dumps(bc.load()))
    committed["cells"]["PRESENCE-CONSTRUCT-1"]["digest"] = "0" * 64
    problems = bc.check(only="PRESENCE-CONSTRUCT-1", committed=committed)
    assert any("digest changed" in problem for problem in problems), problems


def test_the_record_names_the_engine_it_was_taken_on():
    committed = bc.load()
    assert committed["engine_sha256"]
    assert committed["engine_version"]
    assert committed["cycles"] == 120

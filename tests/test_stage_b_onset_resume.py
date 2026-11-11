"""A resumed onset cell must be the same measurement as an uninterrupted one.

`benchmarks/stage_b_onset_withholding.py` can outlive a command limit: it writes
its DI trace after every completed cycle, snapshots the engine database every few
cycles, and on the next invocation resumes from the snapshot and replays the
short trace tail before continuing. That machinery is only worth having if a
resumed cell is the cell an uninterrupted run would have produced. Otherwise a
long cell silently measures a different run, and the artifact records an onset
the engine never had -- the failure mode Phase L's pilot has already taught this
project to look for.

The equivalence is checked on a small world rather than on a real cell, because
what is under test is the checkpoint mechanism and not the duration: the
withholding window is shortened so six cycles are enough to make DI vary, which
is what makes the equality check able to fail rather than being an equality of
zeros. The published 6:1 cell at seed 20261023 was separately rerun uninterrupted
against the artifact and matched it exactly (onset cycle 233, all three
sustention rules); that is a property of the engine, and this file is the
property of the harness.

What the mutation runs established, and why the equality assertion alone is not
enough. Deleting the trace-tail replay, or deleting the restored RNG state,
leaves this world's trajectory **unchanged**: a resume that replays nothing is still correct here
because re-storing a cycle is inert, and the harness never draws from the generator it restores --
`organica/sleep.py` uses `_rng` only in the `stochastic` retention lottery, and the engine's policy is
`salience`, which no Stage B module overrides. So those two mutations are equivalent
re-implementations, not defects, and no behavioural test can distinguish them.
The defect that must be caught is a resume that continues from a state it did
not actually restore, and that is what
`test_a_resume_that_did_not_restore_its_database_is_caught` asserts.
"""
from __future__ import annotations
LAYER = "synthetic"  # benchmarks/test_layers.py: the module's execution layer

import json
import time as real_time

import pytest

from benchmarks import stage_b_onset_withholding as harness
from benchmarks.stage_b_stream_withholding import CONFIG_RATIOS, DESIGN_SEEDS

LABEL = next(iter(CONFIG_RATIOS))
SEED = DESIGN_SEEDS[0]
INDEX = DESIGN_SEEDS.index(SEED)
CYCLES = 6


class _Clock:
    """A clock that advances one second per reading, so the budget stop is fixed.

    The harness stops a cell when `time.time() - started > budget`, so a real
    clock would stop it after however many cycles happened to fit. This makes the
    stop land on a chosen cycle, which is what puts the trace tail one cycle
    ahead of the last database snapshot.
    """

    def __init__(self) -> None:
        self.now = 0.0

    def time(self) -> float:
        self.now += 1.0
        return self.now

    sleep = staticmethod(real_time.sleep)


@pytest.fixture()
def small_world(tmp_path, monkeypatch):
    """Isolate the checkpoint files and shorten the withholding window."""
    monkeypatch.setattr(harness, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(harness, "CONFIRMATION_CYCLE",
                        {label: 2 for label in harness.CONFIRMATION_CYCLE})
    monkeypatch.setattr(harness, "LEARN_CYCLES", 2)
    monkeypatch.setattr(harness, "CHECKPOINT_INTERVAL", 2)
    return tmp_path


def _pause_a_cell() -> dict:
    with pytest.MonkeyPatch.context() as clock:
        clock.setattr(harness, "time", _Clock())
        return harness.run_cell(LABEL, SEED, cycles=CYCLES, budget=2.5)


def test_a_resumed_cell_reproduces_the_uninterrupted_trajectory(small_world):
    straight = harness.run_cell(LABEL, SEED, cycles=CYCLES, checkpoint=False)
    assert straight["complete"] is True and straight["cycles_run"] == CYCLES
    trajectory = straight["di_trajectory"]
    assert len(set(trajectory)) > 1, (
        "the world must make DI vary across cycles, or equal trajectories prove nothing")

    paused = _pause_a_cell()
    assert paused["incomplete"] is True, "a budget stop must not be recorded as a completed cell"
    assert paused["stopped_at_budget"] is True
    assert paused["cycles_run"] < CYCLES
    assert paused["di_trajectory"] == trajectory[:len(paused["di_trajectory"])], (
        "the paused run must be a prefix of the uninterrupted one before it is resumed")

    pointer = json.loads(harness._snapshot_pointer_path(LABEL, INDEX).read_text(encoding="utf-8"))
    meta = json.loads((small_world / pointer["metadata"]).read_text(encoding="utf-8"))
    assert meta["cycles_run"] < paused["cycles_run"], (
        "the snapshot must lag the trace, so the resume has a tail to replay")
    assert meta["di_trajectory"] == trajectory[:meta["cycles_run"]]

    resumed = harness.run_cell(LABEL, SEED, cycles=CYCLES)
    assert resumed["complete"] is True and resumed["cycles_run"] == CYCLES
    assert resumed["di_trajectory"] == trajectory, (
        "a resumed cell must be the same measurement, cycle for cycle")
    assert resumed["onset_by_sustention_rule"] == straight["onset_by_sustention_rule"]
    assert resumed["late_available"] == straight["late_available"]


def test_a_resume_that_did_not_restore_its_database_is_caught(small_world):
    """The one defect the equality check exists for: a resume from an empty substrate.

    A copy that does nothing leaves the working database empty, so the resume
    claims to be at the snapshot's cycle while the engine has none of the history
    behind it. Either the replay guard refuses the cell or the trajectory differs;
    what must not happen is a cell that looks like the uninterrupted run.
    """
    straight = harness.run_cell(LABEL, SEED, cycles=CYCLES, checkpoint=False)
    trajectory = straight["di_trajectory"]
    _pause_a_cell()

    with pytest.MonkeyPatch.context() as broken:
        broken.setattr(harness.shutil, "copy2", lambda *args, **kwargs: None)
        try:
            resumed = harness.run_cell(LABEL, SEED, cycles=CYCLES)
        except RuntimeError as exc:
            assert "differ" in str(exc) or "resume" in str(exc), exc
            return
    assert resumed["di_trajectory"] != trajectory, (
        "a resume with no restored substrate must not reproduce the uninterrupted run")


def test_progress_without_its_snapshot_is_refused_rather_than_restarted(small_world):
    harness._write_json_atomic(harness._progress_path(LABEL, INDEX), {
        "version": harness.CHECKPOINT_VERSION,
        "identity": "unused: the snapshot check fires first",
        "cycles_run": 1,
        "di_trajectory": [0.0],
    })
    with pytest.raises(RuntimeError, match="no committed database snapshot"):
        harness.run_cell(LABEL, SEED, cycles=CYCLES)


def test_a_checkpoint_from_different_inputs_is_refused(small_world):
    harness._write_json_atomic(harness._snapshot_pointer_path(LABEL, INDEX), {
        "version": harness.CHECKPOINT_VERSION,
        "identity": "the inputs this cell was not run with",
        "cycles_run": 0,
        "database": "absent.sqlite",
        "metadata": "absent.json",
    })
    with pytest.raises(RuntimeError, match="checkpoint inputs changed"):
        harness.run_cell(LABEL, SEED, cycles=CYCLES)

"""Generator-level tests for the reusable-knowledge harness (§10 build).

No engine run: every check here is about the instrument — that the conditioning
really withholds the declared transitions, that Gate F's denominator is the 96
available relations and that the gate CAN fire, that the ceiling is the closed
form of §14, and that the confirmatory guard refuses before calibration passes.
"""
from __future__ import annotations

import time
from unittest import mock

import pytest

from benchmarks import reusable_knowledge as rk
from benchmarks.acquisition_compositional import (
    CELLS, EVENTS_PER_CYCLE, LAW_R0, PHASE_RETENTION, PHASE_REVISION_LEARN,
    PHASE_REVISION_TEST, PHASE_TRANSFER, TAGS_PER_CELL, flip_p, flip_q,
    generate_compositional_world, score,
)

SEED = 20261201


@pytest.fixture(scope="module")
def world():
    return generate_compositional_world(seed=SEED)


@pytest.fixture(scope="module")
def formation(world):
    return rk.conditioned_formation_stream(world, SEED)


def test_withheld_is_two_declared_transitions():
    assert rk.WITHHELD == (((0, 0), "flip_p"), ((0, 1), "flip_q"))
    for cell, _kind in rk.WITHHELD:
        permitted = [k for k in rk.KINDS if (cell, k) not in set(rk.WITHHELD)]
        assert len(permitted) == 1, "every context must keep an exit"


def test_conditioning_never_shows_a_withheld_transition(formation):
    observed = formation["observed"]
    for cell, kind in rk.WITHHELD:
        assert observed.get(f"{cell}|{kind}", 0) == 0
    assert formation["compensated"] > 0, "the manipulation must have fired"


def test_formation_adjacency_is_genuine(formation):
    cells = formation["raw_cells"]
    assert len(formation["events"]) == rk.formation_cycles() * EVENTS_PER_CYCLE
    for a, b in zip(cells, cells[1:]):
        assert b in (flip_p(a), flip_q(a)), "a stored event must follow its context"
    assert {str(c) for c in cells} == {str(c) for c in CELLS}


def test_every_permitted_transition_is_instantiated(formation):
    observed = formation["observed"]
    permitted = [(c, k) for c in CELLS for k in rk.KINDS
                 if (c, k) not in set(rk.WITHHELD)]
    for cell, kind in permitted:
        assert observed.get(f"{cell}|{kind}", 0) > 0


def test_gate_f_denominator_is_the_available_relations(world):
    rel = rk.relation_sets(world)
    assert len(rel["available"]) == rk.GATE_F_DENOMINATOR == 96
    assert len(rel["withheld"]) == 32
    assert not (rel["available"] & rel["withheld"])
    assert len(rel["all"]) == 128


def test_gate_f_passes_on_full_and_fails_on_degraded(world):
    rel = rk.relation_sets(world)
    assert rk.gate_f(rel["available"], rel)["passed"] is True
    partial = set(sorted(rel["available"])[:86])
    failed = rk.gate_f(partial, rel)
    assert failed["passed"] is False, "a gate that cannot fire is decoration"
    assert failed["coverage"] == pytest.approx(86 / 96, abs=1e-6)
    assert rk.gate_f(set(), rel)["precision"] is None, "no denominator is not zero"


def test_ceiling_is_the_closed_form(world):
    holder = rk.latent_rule_holder(world)
    for cell, kind in rk.WITHHELD:
        target_cell = flip_p(cell) if kind == "flip_p" else flip_q(cell)
        src = world["cell_tags"][f"p{cell[0]}q{cell[1]}"][0]
        name = f"p{target_cell[0]}q{target_cell[1]}"
        target = world["cell_tags"][name][0]
        assert holder(src, target) == pytest.approx(
            LAW_R0[kind] * 2 / TAGS_PER_CELL, abs=1e-12)


def test_transfer_limb_contains_only_withheld_relations(world):
    held = rk.limbs(world)
    names = [(int(c[1]), int(c[3])) for c in world["cells"]]
    blocked = set(rk.WITHHELD)
    lo, hi = PHASE_TRANSFER[0] * EVENTS_PER_CYCLE, PHASE_TRANSFER[1] * EVENTS_PER_CYCLE
    expected = 0
    for i in range(lo, hi - 1):
        src, dst = names[i], names[i + 1]
        kind = ("flip_p" if dst == flip_p(src)
                else "flip_q" if dst == flip_q(src) else None)
        expected += int(kind is not None and (src, kind) in blocked)
    assert held["transfer_pairs"] == expected
    assert held["transfer_pairs"] >= 20, "the floor of the feasibility check"
    assert len(held["retention"][0]) == (PHASE_RETENTION[1] - PHASE_RETENTION[0]) \
        * EVENTS_PER_CYCLE - 1


def test_endpoint_separates_the_law_from_a_one_transition_learner(world):
    ctx, obs = rk.limbs(world)["transfer"]
    vocab = {t for r in world["events"] for t in r.split()}
    ceiling = score(rk.latent_rule_holder(world), ctx, obs, vocab)["log_loss"]
    broken = score(rk.broken_rule_holder(world), ctx, obs, vocab)["log_loss"]
    assert broken > ceiling, "the transfer limb must be able to see the law"


def _artifact(**over):
    art = {
        "kind": "reusable_knowledge_calibration",
        "variant": rk.VARIANT_NAME,
        "cap": rk.MAX_PREDICTIONS,
        "seeds": list(rk.CALIBRATION_SEEDS),
        "cells": [],
        "pythonhashseed": "0",
        "all_seeds_passed": True,
        "audit_all_passed": True,
        "attribution": {"all_seeds_passed": True},
        "revision": {"all_seeds_passed": True},
        "support_provenance": {"all_seeds_passed": True},
        "per_claim_provenance": {"all_seeds_passed": True},
    }
    art.update(over)
    return art


def test_confirmatory_guard_refuses_without_calibration(monkeypatch):
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    monkeypatch.setattr(rk, "_load_calibration", lambda: None)
    ok, why = rk.confirmatory_allowed()
    assert ok is False and "no calibration" in why
    monkeypatch.setattr(rk, "_load_calibration", lambda: _artifact(
        all_seeds_passed=False,
        cells=[{"seed": 20261201, "calibration_passed": False}]))
    ok, why = rk.confirmatory_allowed()
    assert ok is False and "20261201" in why
    monkeypatch.setattr(rk, "_load_calibration", lambda: _artifact())
    assert rk.confirmatory_allowed()[0] is True


def test_confirmatory_guard_checks_cap_label_and_seeds(monkeypatch):
    """A pass flag alone must not authorise seeds under another variant."""
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    monkeypatch.setattr(rk, "_load_calibration", lambda: _artifact(cap=250))
    ok, why = rk.confirmatory_allowed()
    assert ok is False and "cap 250" in why
    monkeypatch.setattr(rk, "_load_calibration",
                        lambda: _artifact(variant="V1.1-cap(250)"))
    ok, why = rk.confirmatory_allowed()
    assert ok is False and "V1.1-cap(250)" in why
    monkeypatch.setattr(rk, "_load_calibration",
                        lambda: _artifact(seeds=[20261201, 20261202]))
    ok, why = rk.confirmatory_allowed()
    assert ok is False and "seed set" in why
    monkeypatch.setattr(rk, "_load_calibration", lambda: _artifact(audit_all_passed=False))
    ok, why = rk.confirmatory_allowed()
    assert ok is False and "audit" in why
    monkeypatch.setattr(rk, "_load_calibration",
                        lambda: _artifact(attribution={"all_seeds_passed": False}))
    ok, why = rk.confirmatory_allowed()
    assert ok is False and "attribution" in why


def test_variant_label_follows_the_capacity():
    assert rk.variant_label() == rk.VARIANT_NAME
    assert rk.variant_label(1_000) == rk.VARIANT_NAME
    assert rk.variant_label(250) == "V1.1-cap(250)"


def test_calibration_refuses_a_noncanonical_cap(monkeypatch, tmp_path):
    with pytest.raises(ValueError, match="different variant"):
        rk.run_calibration(250)
    called = []
    monkeypatch.setattr(rk, "run_calibration", lambda cap: called.append(cap))
    assert rk.main(["--calibration", "--cap", "250"]) == 4
    assert called == [], "a refused calibration must not run a cell"


def test_calibration_requires_a_fixed_hash_seed(monkeypatch):
    """An unset hash seed makes two identical calibrations disagree."""
    monkeypatch.delenv("PYTHONHASHSEED", raising=False)
    with pytest.raises(ValueError, match="PYTHONHASHSEED"):
        rk.run_calibration()
    assert rk.main(["--calibration"]) == 5
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    assert rk.hash_seed() == "0"


def test_attribution_share_is_measured_and_can_fire():
    layer1 = {"prediction_candidate": {"alpha": {"beta": 3.0}}}
    other = {"concept_candidate": {"alpha": {"beta": 1.0}}}
    dominant = rk.attribution_share({"type_rows": {**layer1, **other}})
    assert dominant["share"] == pytest.approx(0.75)
    assert dominant["passed"] is True
    assert dominant["without_layer1_share"] == 0.0
    assert dominant["without_layer1_share"] < rk.ATTRIBUTION_MINIMUM, \
        "the control must fire, or the gate is decoration"

    reversed_ = rk.attribution_share({"type_rows": {
        "prediction_candidate": {"alpha": {"beta": 1.0}},
        "concept_candidate": {"alpha": {"beta": 3.0}}}})
    assert reversed_["share"] == pytest.approx(0.25)
    assert reversed_["passed"] is False, "a majority outside Layer 1 must fail"

    empty = rk.attribution_share({"type_rows": {}})
    assert empty["share"] is None, "no evidence is not a zero share"
    assert empty["passed"] is False
    assert empty["without_layer1_share"] is None, "no control without evidence"


def test_confirmatory_guard_requires_the_calibrated_hash_seed(monkeypatch):
    """Calibration is hash-sensitive, so a different pin is a different run."""
    monkeypatch.setattr(rk, "_load_calibration", lambda: _artifact(pythonhashseed="0"))
    monkeypatch.delenv("PYTHONHASHSEED", raising=False)
    ok, why = rk.confirmatory_allowed()
    assert ok is False and "unset" in why
    monkeypatch.setenv("PYTHONHASHSEED", "7")
    ok, why = rk.confirmatory_allowed()
    assert ok is False and "run at" in why
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    assert rk.confirmatory_allowed()[0] is True


def test_revision_stream_withholds_the_pair_under_the_new_law():
    world = generate_compositional_world(seed=SEED)
    stream = rk.conditioned_revision_stream(world, SEED, (0, 0))
    span = (PHASE_REVISION_LEARN[1] - PHASE_REVISION_LEARN[0]) * EVENTS_PER_CYCLE
    assert len(stream["events"]) == span
    assert stream["compensated"] > 0, "the revision manipulation must fire"
    for cell, kind in rk.WITHHELD:
        assert stream["observed"].get(f"{cell}|{kind}", 0) == 0
    permitted = [(c, k) for c in CELLS for k in rk.KINDS
                 if (c, k) not in set(rk.WITHHELD)]
    for cell, kind in permitted:
        assert stream["observed"].get(f"{cell}|{kind}", 0) > 0


def test_revision_limbs_have_denominators(world):
    held = rk.limbs(world)
    span = (PHASE_REVISION_TEST[1] - PHASE_REVISION_TEST[0]) * EVENTS_PER_CYCLE
    assert len(held["revision"][0]) == span - 1
    assert len(held["revision_held_out"][0]) == held["revision_pairs"] > 0
    assert set(held["revision_instances"]) <= set(rk.KINDS)
    switch = PHASE_REVISION_LEARN[0] * EVENTS_PER_CYCLE
    assert world["regimes"][switch - 1] == 0 and world["regimes"][switch] == 1, \
        "the law must actually rotate at the revision boundary"


def test_support_provenance_counts_distinct_transitions():
    # Two transitions from the SAME prior event to different targets are two
    # pieces of evidence: the identity is (prior event, target event).
    support = {("alpha", "beta"): {(1, 2): False, (1, 3): True}}
    prov = rk.support_provenance(support, {("alpha", "beta")}, windows_with_sleep=5)
    assert prov["distinct_support"] == 2, "one prior event, two transitions"
    assert prov["share_self_sourced"] == pytest.approx(0.5)


def test_per_claim_rule_is_the_disqualifier():
    claim = [{"type": "prediction_candidate", "source": "alpha", "target": "beta",
              "on_withheld": True}]
    dirty = rk.per_claim_provenance(
        claim, {("alpha", "beta"): {(1, 2): False, (1, 3): False, (2, 4): True}})
    assert dirty["claims_measurable"] == 1
    assert dirty["max_share"] == pytest.approx(1 / 3)
    assert dirty["all_claims_passed"] is False, \
        "a third self-sourced exceeds the 17.9 % reference"
    assert dirty["evaluable"] is True

    clean = rk.per_claim_provenance(
        claim, {("alpha", "beta"): {(1, 2): False, (1, 3): False, (2, 4): False}})
    assert clean["all_claims_passed"] is True

    empty = rk.per_claim_provenance(claim, {})
    assert empty["claims_measurable"] == 0
    assert empty["evaluable"] is False, "a mostly unmeasurable population is not a pass"
    assert empty["all_claims_passed"] is False


def test_the_all_self_control_runs_the_evaluator():
    claim = [{"type": "prediction_candidate", "source": "a", "target": "b",
              "on_withheld": False}]
    got = rk.per_claim_provenance(claim, {("a", "b"): {(1, 2): True}})
    assert got["control"] == {"claims": 1, "failed": 1, "max_share": 1.0}
    assert got["control_all_self_fails"] is True, \
        "the control must judge claims through the evaluator"


def test_withheld_claims_are_reported_separately():
    claims = [{"type": "prediction_candidate", "source": "a", "target": "b",
               "on_withheld": True},
              {"type": "prediction_candidate", "source": "b", "target": "a",
               "on_withheld": False}]
    support = {("a", "b"): {(1, 2): True, (1, 3): False},
               ("b", "a"): {(2, 3): False}}
    got = rk.per_claim_provenance(claims, support)
    assert got["withheld_claims"]["claims_measurable"] == 1
    assert got["withheld_claims"]["claims_failed"] == 1


def test_a_pass_reports_how_much_of_the_population_it_covers():
    """The measurable floor bounds exclusion; it does not stop a pass covering a
    minority.  The worst case is pinned here so a pass cannot be quoted as if it
    spoke for the whole asserted population."""
    claims = [{"type": "prediction_candidate", "source": "a", "target": "b",
               "on_withheld": False},
              {"type": "prediction_candidate", "source": "c", "target": "d",
               "on_withheld": False}]
    got = rk.per_claim_provenance(claims, {("a", "b"): {(1, 2): False}})
    assert got["claims_measurable"] == 1 and got["claims_unmeasurable"] == 1
    assert got["evaluable"] is True, "exactly at the floor"
    assert got["all_claims_passed"] is True, "a half-unjudged population can pass"
    assert got["pass_coverage"] == pytest.approx(0.5)
    assert got["excluded_share"] == pytest.approx(0.5)


class _TieClock:
    """One timestamp per `group` calls, so lookback windows genuinely tie."""

    def __init__(self, group: int = 4, base: float = 1_700_000_000.0):
        self.group, self.base, self.calls = group, base, 0

    def time(self) -> float:
        value = self.base + (self.calls // self.group) * 0.0001
        self.calls += 1
        return value


TIE_TEXTS = ["alpha beta gamma delta", "epsilon zeta eta theta",
             "iota kappa lambda mu", "nu xi omicron pi",
             "rho sigma tau upsilon", "phi chi psi omega"]


def _lookback(mem) -> list:
    return mem._conn.execute(
        "SELECT rowid, tags, event_type FROM events ORDER BY time DESC LIMIT 3"
    ).fetchall()


def test_a_tied_window_still_names_the_event_the_store_inserted(tmp_path):
    """Measured tie arm: the window ties, and every target is the stored row.

    Ties are forced so the lookback genuinely has no tie-breaker (spec §3.3).
    On this SQLite build the window's first row happened to be the stored row in
    every tied store -- that is an implementation observation, not a guarantee,
    which is why the identity does not rest on it (`test_target_identity_does_
    not_come_from_the_window_order`).
    """
    mem = rk.MemoryService(str(tmp_path / "tied.db"))
    record, support, _state = rk._support_observer(mem)
    clock = _TieClock(group=4)
    tied_windows = first_row_disagreements = stores = 0
    try:
        with mock.patch.object(time, "time", clock.time):
            for text in TIE_TEXTS:
                event = mem.store(text, event_type="observe", source="env")
                stored = rk.stored_rowid(mem, event.id)
                window = _lookback(mem)
                times = [r[0] for r in mem._conn.execute(
                    "SELECT time FROM events ORDER BY time DESC LIMIT 3").fetchall()]
                tied_windows += int(len(times) != len(set(times)))
                first_row_disagreements += int(window[0][0] != stored)
                before = {k for recs in support.values() for k in recs}
                record(sorted(text.split()), stored)
                added = {k for recs in support.values() for k in recs} - before
                stores += 1
                assert added, "a store must contribute transitions"
                assert {k[1] for k in added} == {stored}, (
                    "every transition of a store must name the event that store "
                    "inserted")
    finally:
        mem._conn.close()
    assert tied_windows >= 1, "the clock never produced a tied window"
    assert stores == len(TIE_TEXTS)
    # Recorded, not asserted: the window's own order agreed here.
    assert first_row_disagreements == 0, (
        "this SQLite build ordered the tied window differently than expected; "
        "the assertion above is what carries the identity, not rows[0]")


class _WindowOrder:
    """A connection whose lookback returns the tied window in the other order.

    SQLite promises nothing about the order of rows that tie on `time`, so an
    implementation may legitimately return the stored row last.  This wrapper
    produces that order deterministically, which is what makes the identity
    check able to fail: under the old rule the target would be an older tied
    row, and every transition of the store would carry the wrong event.
    """

    class _Rows:
        def __init__(self, rows):
            self._rows = rows

        def fetchall(self):
            return self._rows

    def __init__(self, conn):
        self._conn = conn
        self.rotated = False

    def execute(self, sql, params=()):
        cur = self._conn.execute(sql, params)
        if (self.rotated and "ORDER BY time DESC LIMIT 3" in sql
                and "rowid, tags, event_type" in sql):
            rows = cur.fetchall()
            return self._Rows(rows[1:] + rows[:1])
        return cur

    def __getattr__(self, name):
        return getattr(self._conn, name)


def test_target_identity_does_not_come_from_the_window_order(tmp_path):
    """With the tied window ordered against it, the target is still the store's."""
    mem = rk.MemoryService(str(tmp_path / "rotated.db"))
    record, support, _state = rk._support_observer(mem)
    clock = _TieClock(group=4)
    real = mem._conn
    order = _WindowOrder(real)
    mem._conn = order
    try:
        with mock.patch.object(time, "time", clock.time):
            for text in TIE_TEXTS:
                event = mem.store(text, event_type="observe", source="env")
                stored = rk.stored_rowid(mem, event.id)
                order.rotated = True
                window = order.execute(
                    "SELECT rowid, tags, event_type FROM events "
                    "ORDER BY time DESC LIMIT 3").fetchall()
                order.rotated = False
                if len(window) < 2:
                    continue
                assert window[0][0] != stored, (
                    "the rotated window must put an older tied row first, or "
                    "this test cannot tell the two identity sources apart")
                before = {k for recs in support.values() for k in recs}
                record(sorted(text.split()), stored)
                added = {k for recs in support.values() for k in recs} - before
                assert added, "a store must contribute transitions"
                assert {k[1] for k in added} == {stored}, (
                    "the old rule would have named rows[0], an older tied event")
                assert window[0][0] not in {k[1] for k in added}
    finally:
        mem._conn = real
        mem._conn.close()


def test_confirmatory_guard_requires_the_per_claim_rule(monkeypatch):
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    monkeypatch.setattr(rk, "_load_calibration",
                        lambda: _artifact(per_claim_provenance={"all_seeds_passed": False}))
    ok, why = rk.confirmatory_allowed()
    assert ok is False and "per-claim" in why

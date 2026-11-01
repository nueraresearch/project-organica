"""Generator-level tests for the reusable-knowledge harness (§10 build).

No engine run: every check here is about the instrument — that the conditioning
really withholds the declared transitions, that Gate F's denominator is the 96
available relations and that the gate CAN fire, that the ceiling is the closed
form of §14, and that the confirmatory guard refuses before calibration passes.
"""
from __future__ import annotations

import pytest

from benchmarks import reusable_knowledge as rk
from benchmarks.acquisition_compositional import (
    CELLS, EVENTS_PER_CYCLE, LAW_R0, PHASE_RETENTION, PHASE_TRANSFER,
    TAGS_PER_CELL, flip_p, flip_q, generate_compositional_world, score,
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


def test_confirmatory_guard_refuses_without_calibration(monkeypatch):
    monkeypatch.setattr(rk, "_load_calibration", lambda: None)
    ok, why = rk.confirmatory_allowed()
    assert ok is False and "no calibration" in why
    monkeypatch.setattr(rk, "_load_calibration",
                        lambda: {"all_seeds_passed": False, "cells": [
                            {"seed": 20261201, "calibration_passed": False}]})
    ok, why = rk.confirmatory_allowed()
    assert ok is False and "20261201" in why
    monkeypatch.setattr(rk, "_load_calibration",
                        lambda: {"all_seeds_passed": True, "cells": []})
    assert rk.confirmatory_allowed()[0] is True

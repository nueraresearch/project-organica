"""The D3 preregistration must be reachable in every direction it claims, and its seeds fresh."""
LAYER = "dry-run"  # benchmarks/test_layers.py: the module's execution layer

import json
from pathlib import Path

import pytest

from benchmarks import d3_persistence_prereg as P

ROOT = Path(__file__).resolve().parent.parent


def _body():
    return P.prereg()


def _cells(body, alive=True, early=0.0, witness_cycles=39, witness_peak=6,
           predictions=100, first_zero=39):
    cells = []
    for seed in body["design"]["seeds"]:
        counts = [5] * 3000 if alive else [5] * 36 + [0] * 64
        cells.append({"stage": "witness", "seed": seed, "arm": "control",
                      "theory_cycles": 39, "peak": 6, "theory_counts": [5] * 40,
                      "predictions_early": predictions})
        cells.append({"stage": "witness", "seed": seed, "arm": "treatment",
                      "theory_cycles": witness_cycles, "peak": witness_peak,
                      "theory_counts": [5] * 40, "predictions_early": predictions})
        cells.append({"stage": "preflight", "seed": seed, "arm": "control",
                      "first_zero_cycle": first_zero, "theory_counts": [5] * 36 + [0],
                      "recall_early": 0.90, "predictions_early": predictions})
        cells.append({"stage": "preflight", "seed": seed, "arm": "treatment",
                      "first_zero_cycle": None if alive else 100,
                      "theory_counts": counts,
                      "recall_early": 0.90 + early, "predictions_early": predictions})
    return cells


def _run(body, cells):
    return {"prereg": body["prereg"],
            "engine": {"fingerprint": "shipped", "decay": 0.95, "death_threshold": 0.15},
            "arms": {"control": {"decay": 0.95, "death_threshold": 0.15,
                                 "frequency_decay": "none", "fingerprint": "shipped"},
                     "treatment": {"decay": 0.95, "death_threshold": 0.15,
                                   "frequency_decay": 0.95, "fingerprint": "matched"}},
            "control_rerun_fingerprint": "shipped",
            "witness_negative_controls": {"NO_DREAMS": {"dreams_max": 0},
                                          "NO_QUESTIONS": {"questions_max": 0}},
            "cells": cells}


def test_the_record_is_frozen_and_allocates_a_fresh_block():
    body = _body()
    assert P.validate(body) == []
    assert body["status"] == "FROZEN, NOT RUN"
    assert body["mechanism"]["implemented"] is False
    assert body["predicts"]["success"] and body["predicts"]["failure"]
    assert body["adoption"]["withdrawal"]
    assert body["no_cells_run"] is True
    assert len(body["design"]["seeds"]) == 6
    assert body["design"]["cells"] == 24


def test_the_committed_page_is_what_the_record_renders():
    assert P.DOC.exists()
    assert P.DOC.read_text(encoding="utf-8") == P.render(_body())


def test_every_verdict_in_the_table_is_reachable():
    body = _body()
    assert P.verdict(body, _run(body, _cells(body)))[0] == "PERSISTENCE REPAIRED"
    assert P.verdict(body, _run(body, _cells(body, early=-0.05)))[0] == (
        "PERSISTENCE REPAIRED WITH EARLY COST")
    assert P.verdict(body, _run(body, _cells(body, alive=False)))[0] == "NO REPAIR"
    assert P.verdict(body, _run(body, _cells(body, witness_cycles=10, witness_peak=2)))[0] == (
        "WITNESS BROKEN")


def test_every_gate_can_fire():
    body = _body()
    cases = {}

    no_death = _run(body, _cells(body, first_zero=100))
    cases["G1_baseline_death"] = no_death

    slow = _run(body, _cells(body))
    slow["arms"]["treatment"]["decay"] = 0.99
    cases["G2_manipulation_live"] = slow

    noop = _run(body, _cells(body))
    noop["arms"]["control"]["fingerprint"] = "not-the-engine"
    cases["G3_noop_control"] = noop

    determinism = _run(body, _cells(body))
    determinism["control_rerun_fingerprint"] = "different"
    cases["G4_determinism"] = determinism

    block = _run(body, _cells(body))
    block["cells"] = block["cells"][:-1]
    cases["G5_seed_block"] = block

    denominator = _run(body, _cells(body, predictions=0))
    cases["G6_denominator"] = denominator

    controls = _run(body, _cells(body))
    controls["witness_negative_controls"]["NO_DREAMS"]["dreams_max"] = 1
    cases["G7_negative_controls"] = controls

    for gate, run in cases.items():
        label, details = P.verdict(body, run)
        assert label == "VOID", gate
        assert details.get("gate") == gate, (gate, details)


def test_the_repair_may_not_buy_its_effect_with_a_slower_decay():
    body = _body()
    for arm in P.ARMS:
        assert body["arms"][arm]["decay"] == 0.95
        assert body["arms"][arm]["death_threshold"] == 0.15
    broken = json.loads(json.dumps(body))
    broken["arms"]["treatment"]["decay"] = 0.99
    assert any("decay" in problem for problem in P.validate(broken))
    broken = json.loads(json.dumps(body))
    broken["arms"]["treatment"]["frequency_decay"] = 0.99
    assert any("denominator" in problem for problem in P.validate(broken))


def test_the_seed_block_appears_nowhere_else():
    body = _body()
    seeds = [str(seed) for seed in body["design"]["seeds"]] + [str(body["design"]["bootstrap"])]
    own = {P.PREREG.resolve(), P.DOC.resolve(),
           (ROOT / "docs" / "d3_persistence_run.json").resolve(),
           (ROOT / "docs" / "D3-PERSISTENCE-RESULT.md").resolve(),
           (ROOT / "docs" / "stage_b_protocol.json").resolve(),
           (ROOT / "docs" / "test_count.json").resolve(),
           (ROOT / "docs" / "research_question_registry.json").resolve(),
           (ROOT / "docs" / "USER-MANUAL.md").resolve(),
           (ROOT / "docs" / "ACTION-PLAN.md").resolve(),
           (ROOT / "tests" / "test_d3_persistence_seed_varying.py").resolve()}
    roots = ["docs", "benchmarks", "tests", "papers", "research-journal"]
    for root in roots:
        for path in (ROOT / root).rglob("*"):
            if not path.is_file() or path.resolve() in own:
                continue
            if path.suffix not in (".py", ".md", ".json", ".txt", ".cff", ".toml"):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for seed in seeds:
                assert seed not in text, "%s reuses seed %s" % (path, seed)


def test_the_record_must_state_success_failure_and_withdrawal():
    body = _body()
    broken = json.loads(json.dumps(body)); broken.pop("predicts")
    assert any("success and failure" in problem for problem in P.validate(broken))
    broken = json.loads(json.dumps(body)); broken["adoption"].pop("withdrawal")
    assert any("withdrawal" in problem for problem in P.validate(broken))


def test_the_scorer_refuses_a_run_for_another_preregistration(tmp_path):
    path = tmp_path / "run.json"
    path.write_text(json.dumps({"prereg": "something-else", "cells": []}), encoding="utf-8")
    with pytest.raises(SystemExit):
        P.main(["--analyze", str(path)])


def test_check_mode_writes_nothing():
    before = P.DOC.read_bytes()
    assert P.main(["--check"]) == 0
    assert P.DOC.read_bytes() == before

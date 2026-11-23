"""The Q053 preregistration must be reachable in every direction it claims, and its seeds fresh.

The fixtures are synthetic cells: no engine runs, no world is generated, and the scorer is the
committed one, so a verdict that cannot be reached here cannot be reached in the block either.
"""
LAYER = "dry-run"  # benchmarks/test_layers.py: the module's execution layer

import json
from pathlib import Path

import pytest

from benchmarks import q053_mechanism_prereg as P

ROOT = Path(__file__).resolve().parent.parent


def _body():
    return P.prereg()


def _cells(body, capability=0.05, early=0.0, m1=0.5, spread=0.01,
           liveness=1.0, predictions=100):
    """A synthetic block: `capability` is the treatment's late advantage."""
    cells = []
    for index, seed in enumerate(body["design"]["seeds"]):
        wobble = (index % 3 - 1) * spread
        cells.append({"seed": seed, "arm": "control", "early_recall": 0.90,
                      "late_recall": 0.50, "late_competition_share": 0.05,
                      "late_theory_zero_share": liveness,
                      "predictions_early": predictions, "predictions_late": predictions})
        cells.append({"seed": seed, "arm": "treatment", "early_recall": 0.90 + early,
                      "late_recall": 0.50 + capability + wobble,
                      "late_competition_share": 0.05 + m1,
                      "late_theory_zero_share": 0.0,
                      "predictions_early": predictions, "predictions_late": predictions})
    return cells


def _run(body, cells):
    return {"prereg": body["prereg"],
            "engine": {"fingerprint": "shipped", "decay": 0.95, "death_threshold": 0.15},
            "arms": {"control": {"decay": 0.95, "death_threshold": 0.15, "fingerprint": "shipped"},
                     "treatment": {"decay": 0.95, "death_threshold": 0.15,
                                   "fingerprint": "floor"}},
            "control_rerun_fingerprint": "shipped",
            "cells": cells}


def test_the_record_is_frozen_and_allocates_a_fresh_block():
    body = _body()
    assert P.validate(body) == []
    assert body["status"] == "FROZEN, NOT RUN"
    assert body["mechanism"]["implemented"] is False
    assert body["no_cells_run"] is True
    assert len(body["design"]["seeds"]) == 10
    assert body["design"]["cells"] == 20


def test_the_committed_page_is_what_the_record_renders():
    assert P.DOC.exists()
    assert P.DOC.read_text(encoding="utf-8") == P.render(_body())


def test_every_verdict_in_the_table_is_reachable():
    body = _body()
    reachable = {}
    reachable["COMPETITION PRESERVED WITH CAPABILITY GAIN"] = P.verdict(
        body, _run(body, _cells(body, capability=0.05)))[0]
    reachable["COMPETITION PRESERVED, NO CAPABILITY GAIN"] = P.verdict(
        body, _run(body, _cells(body, capability=0.0, spread=0.004)))[0]
    reachable["GAIN AT AN EARLY COST"] = P.verdict(
        body, _run(body, _cells(body, capability=0.05, early=-0.05)))[0]
    reachable["MECHANISM DID NOT OPERATE"] = P.verdict(
        body, _run(body, _cells(body, m1=0.0)))[0]
    for expected, produced in reachable.items():
        assert produced == expected, (expected, produced)


def test_underpowered_is_reachable_and_distinct_from_no_gain():
    body = _body()
    noisy = _cells(body, capability=0.0, spread=0.4)
    label, details = P.verdict(body, _run(body, noisy))
    assert label == "UNDERPOWERED"
    assert details["width"] > body["criteria"]["underpowered_width"]


def test_every_gate_can_fire():
    body = _body()
    cases = {}
    cases["G1_liveness"] = _run(body, _cells(body, liveness=0.0))
    cases["G6_denominator"] = _run(body, _cells(body, predictions=0))

    noop = _run(body, _cells(body))
    noop["arms"]["control"]["fingerprint"] = "not-the-engine"
    cases["G2_noop_control"] = noop

    determinism = _run(body, _cells(body))
    determinism["control_rerun_fingerprint"] = "different"
    cases["G3_determinism"] = determinism

    confound = _run(body, _cells(body))
    confound["arms"]["treatment"]["decay"] = 0.99
    cases["G4_persistence_confound"] = confound

    block = _run(body, _cells(body))
    block["cells"] = block["cells"][:-1]
    cases["G5_seed_block"] = block

    for gate, run in cases.items():
        label, details = P.verdict(body, run)
        assert label == "VOID", gate
        assert details.get("gate") == gate, (gate, details)


def test_the_mechanism_may_not_buy_its_effect_with_persistence():
    body = _body()
    for arm in ("control", "treatment"):
        assert body["arms"][arm]["decay"] == 0.95
        assert body["arms"][arm]["death_threshold"] == 0.15
    broken = json.loads(json.dumps(body))
    broken["arms"]["treatment"]["decay"] = 1.0
    assert any("threshold 0.15" in problem or "decay" in problem
               for problem in P.validate(broken))


def test_the_seed_block_appears_nowhere_else():
    body = _body()
    seeds = [str(seed) for seed in body["design"]["seeds"]] + [str(body["design"]["bootstrap"])]
    own = {P.PREREG.resolve(), P.DOC.resolve(),
           (ROOT / "docs" / "stage_b_protocol.json").resolve(),
           (ROOT / "docs" / "test_count.json").resolve(),
           (ROOT / "docs" / "research_question_registry.json").resolve(),
           (ROOT / "docs" / "USER-MANUAL.md").resolve(),
           (ROOT / "docs" / "q053_mechanism_run.json").resolve(),
           (ROOT / "docs" / "Q053-MECHANISM-RESULT.md").resolve()}
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


def test_the_scorer_refuses_a_run_for_another_preregistration(tmp_path, capsys):
    body = _body()
    path = tmp_path / "run.json"
    path.write_text(json.dumps({"prereg": "something-else", "cells": []}), encoding="utf-8")
    with pytest.raises(SystemExit):
        P.main(["--analyze", str(path)])


def test_check_mode_writes_nothing():
    before = P.DOC.read_bytes()
    assert P.main(["--check"]) == 0
    assert P.DOC.read_bytes() == before

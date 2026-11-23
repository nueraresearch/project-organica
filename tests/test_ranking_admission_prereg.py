"""The confirmatory registration must allocate a fresh block, calibrate its bar on data it does
not judge, and let every outcome of its decision table be reached and voided.

The fixtures are synthetic cells: no engine runs, no world is generated. The scorer is the
committed one, so a verdict that cannot be reached here cannot be reached in the run either.
"""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
import re
from pathlib import Path

import pytest

from benchmarks import run_ranking_admission as R
from benchmarks import score_ranking_admission as A
from benchmarks.decay_confirmation import harvest_seeds

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "ranking_admission_prereg.json"
DOC = ROOT / "docs" / "RANKING-ADMISSION-PREREGISTRATION.md"
ORDERING_RESULT = ROOT / "docs" / "rank_ordering_result.json"

SPARSE = 0.1
DENSE = 0.8


def _body():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _flat():
    return " ".join(DOC.read_text(encoding="utf-8").split())


def _used_elsewhere():
    found = set()

    def ints(value):
        if isinstance(value, int):
            found.add(value)
        elif isinstance(value, list):
            for item in value:
                ints(item)
        elif isinstance(value, dict):
            for item in value.values():
                ints(item)

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if "seed" in key.lower():
                    ints(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    # this block's own files carry its seeds by construction, so freshness is judged
    # against the artifacts that existed before it, never against its own outputs
    recorded = {ARTIFACT, ROOT / "docs" / "stage_b_protocol.json",
                ROOT / "docs" / "ranking_admission_run.json",
                ROOT / "docs" / "ranking_admission_result.json"}
    for path in sorted((ROOT / "docs").glob("*.json")):
        if path in recorded:
            continue
        try:
            walk(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
    return found


def _cell(arm, cap, rho, seed, coverage, differ=True):
    world = round(rho * 240)
    covered = max(0, min(int(cap), round(coverage * world)))
    selected = (["c-%d" % i for i in range(3)] if arm == "control"
                else ["d-%d" % i for i in range(3)] if differ else ["c-%d" % i for i in range(3)])
    return {"arm": arm, "cap": cap, "rho_world": rho, "seed": seed,
            "coverage": round(covered / world, 6), "precision": round(covered / cap, 6),
            "rho_rank": round(0.55 * rho, 6), "presence": 1.0, "selected": selected,
            "asserted": cap, "covered": covered}


def _grid(sparse, dense, presence=1.0, differ=True):
    """`sparse` and `dense` map a seed to (control coverage, treated coverage)."""
    body = A.prereg()
    design = body["design"]
    cells = []
    for seed in design["seeds"]:
        for rho in design["densities"]:
            pair = (sparse(seed) if abs(rho - SPARSE) < 1e-9
                    else dense(seed) if abs(rho - DENSE) < 1e-9 else (0.0, 0.0))
            for cap in design["caps"]:
                for arm in design["arms"]:
                    cell = _cell(arm, cap, rho, seed, pair[0] if arm == "control" else pair[1],
                                 differ)
                    cell["presence"] = presence
                    cells.append(cell)
    return {"cells": cells,
            "identity": {"rho_world": 1.0, "arms_identical": True, "delta": 0.0}}


def _flat_pair(value):
    return lambda seed: (0.0, value)


FLAT_ZERO = lambda seed: (0.0, 0.0)


# ---------------------------------------------------------------------------
# The artifact
# ---------------------------------------------------------------------------

def test_the_grid_is_the_documented_arithmetic():
    design = _body()["design"]
    product = (len(design["arms"]) * len(design["caps"])
               * len(design["densities"]) * len(design["seeds"]))
    assert design["cells"] == product == 160
    assert design["caps"] == [20, 40]
    assert design["densities"] == [SPARSE, 0.2, 0.4, 0.6, DENSE]
    assert design["world_edges_at_each_density"] == [
        round(d * 240) for d in design["densities"]]


def test_the_seed_block_is_fresh_and_contiguous():
    body = _body()
    world, bootstrap = body["seeds"]["world"], body["seeds"]["bootstrap"]
    assert body["seeds"]["block"] == [world[0], world[-1]]
    assert len(world) == 8 and world == list(range(world[0], world[0] + 8))
    assert bootstrap == world[-1] + 1 and bootstrap not in world
    used = _used_elsewhere()
    assert not (set(world + [bootstrap]) & used), sorted(set(world) & used)
    assert set(world + [bootstrap]) <= harvest_seeds(ROOT / "docs")


def test_the_bar_is_calibrated_on_the_completed_run_and_not_on_the_judged_one():
    crit = _body()["criteria"]
    result = json.loads(ORDERING_RESULT.read_text(encoding="utf-8"))
    mean = result["criteria"]["M1"]["mean_delta_at_min_density"]
    expected = int(mean / 2.0 * 100) / 100.0
    assert crit["adoption_bar"] == expected
    assert "%.4f" % mean in crit["adoption_bar_provenance"]
    assert "not the block being judged" in crit["adoption_bar_provenance"]
    assert crit["guard_bar"] == -0.05
    assert "declared, not calibrated" in crit["guard_bar_provenance"]
    assert crit["sign_test"] == {"required": 7, "of": 8}
    assert crit["interval"] == 0.95 and crit["bootstrap_reps"] == 4000


def test_the_allocation_is_recorded_and_both_thresholds_are_fixed():
    alloc = _body()["allocation"]
    assert alloc["seeds"] == 8 and alloc["cells"] == 160
    assert alloc["thresholds"] == 2 and alloc["bars"] == 2
    assert _body()["analysis"]["frozen"] is True


# ---------------------------------------------------------------------------
# The decision path
# ---------------------------------------------------------------------------

def test_a_reproduced_gain_on_fresh_seeds_adopts_the_rule():
    result = A.score(_grid(_flat_pair(4 / 24), lambda seed: (0.5, 0.5)))
    assert result["gates"]["all_passed"] is True
    assert result["criteria"]["adoption"]["passed"] is True
    assert result["criteria"]["guard"]["passed"] is True
    assert result["decision"]["verdict"] == "ADOPT THE ADMISSION RULE"
    assert result["decision"]["decision"] == "adopt"


def test_a_loss_at_the_dense_end_prices_the_trade_and_nothing_is_adopted():
    result = A.score(_grid(_flat_pair(4 / 24), lambda seed: (20 / 192, 8 / 192)))
    assert result["criteria"]["adoption"]["passed"] is True
    assert result["criteria"]["guard"]["passed"] is False
    assert result["decision"]["verdict"] == "PRICE THE TRADE"
    assert result["decision"]["decision"] == "trade"


def test_a_flat_gain_closes_the_ordering_line():
    result = A.score(_grid(FLAT_ZERO, FLAT_ZERO))
    adoption = result["criteria"]["adoption"]
    assert adoption["passed"] is False
    assert adoption["conditions"]["mean_at_or_above_bar"] is False
    assert result["decision"]["verdict"] == "CLOSE ORDERING"
    assert result["decision"]["decision"] == "close"


def test_the_sign_test_can_fail_while_the_mean_clears_the_bar():
    sparse = lambda seed: (0.0, 4 / 24) if seed < 20310507 else (0.0, 0.0)
    result = A.score(_grid(sparse, lambda seed: (0.5, 0.5)))
    adoption = result["criteria"]["adoption"]
    assert adoption["conditions"]["mean_at_or_above_bar"] is True
    assert adoption["conditions"]["sign_test_met"] is False
    assert adoption["passed"] is False
    assert result["decision"]["verdict"] == "CLOSE ORDERING"


def test_a_wide_interval_is_underpowered_and_closes_nothing():
    sparse = lambda seed: (0.0, 20 / 24) if seed % 2 == 0 else (0.0, 0.0)
    result = A.score(_grid(sparse, lambda seed: (0.0, 0.0)))
    adoption = result["criteria"]["adoption"]
    assert adoption["passed"] is False
    assert adoption["interval_width"] > 0.3
    assert result["decision"]["verdict"] == "UNDERPOWERED"
    assert result["decision"]["decision"] == "neither"


def test_a_failed_gate_voids_the_block_and_no_criterion_is_read():
    result = A.score(_grid(_flat_pair(4 / 24), lambda seed: (0.5, 0.5), presence=0.9))
    assert result["gates"]["G1_presence_ceiling"]["passed"] is False
    assert result["decision"]["verdict"] == "VOID"
    assert result["criteria"]["adoption"]["passed"] is None


def test_an_inert_arm_voids_the_block():
    result = A.score(_grid(_flat_pair(4 / 24), lambda seed: (0.5, 0.5), differ=False))
    assert result["gates"]["G0_liveness"]["passed"] is False
    assert result["decision"]["verdict"] == "VOID"


def test_the_scorer_refuses_a_grid_that_is_not_the_preregistered_one():
    payload = _grid(_flat_pair(4 / 24), lambda seed: (0.5, 0.5))
    payload["cells"] = payload["cells"][:-1]
    with pytest.raises(ValueError, match="pre-registered grid"):
        A.score(payload)


def test_the_analysis_path_is_committed_and_does_not_touch_the_engine():
    path = ROOT / _body()["analysis"]["path"]
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    assert "import organica" not in source and "from organica" not in source
    assert _body()["analysis"]["frozen"] is True


def test_the_runner_audits_before_it_runs():
    record = _body()
    assert R.audit(record) == {"passed": True, "problems": []}
    tampered = json.loads(json.dumps(record))
    tampered["design"]["seeds"] = tampered["design"]["seeds"][:4]
    assert R.audit(tampered)["passed"] is False


def test_the_document_quotes_the_artifact_and_has_no_placeholders():
    body, flat = _body(), _flat()
    low, high = body["seeds"]["block"]
    for token in ("%d\u2013%d" % (low, high), str(body["seeds"]["bootstrap"]),
                  "160", "%.2f" % body["criteria"]["adoption_bar"],
                  "%.2f" % body["criteria"]["guard_bar"], "95%",
                  "cap %d" % body["design"]["caps"][0]):
        assert token in flat, token
    for row in body["decision_table"]:
        assert row["verdict"] in flat, row["verdict"]
    assert "cap %d" % body["design"]["caps"][0] in flat
    assert "cap 0 " not in flat
    assert "No cell may run before this file is committed" in flat
    assert not re.search(r"\{[a-z_]+\}", DOC.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# The result, once run
# ---------------------------------------------------------------------------

RESULT = ROOT / "docs" / "ranking_admission_result.json"


def test_the_result_is_the_preregistered_grid_scored_by_the_frozen_path():
    body = _body()
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["prereg"] == body["prereg"]
    assert result["cells"] == body["design"]["cells"] == 160
    assert result["gates"]["all_passed"] is True
    assert result["criteria"]["adoption"]["bar"] == body["criteria"]["adoption_bar"]
    assert result["criteria"]["guard"]["bar"] == body["criteria"]["guard_bar"]
    assert result["decision"]["verdict"] in [r["verdict"] for r in body["decision_table"]]


def test_the_recorded_run_agrees_with_the_result_artifact():
    body = _body()
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    run = body["run"]
    assert run["verdict"] == result["decision"]["verdict"]
    assert run["cells"] == result["cells"]
    assert run["adoption"]["mean_delta_at_sparsest"] == \
        result["criteria"]["adoption"]["mean_delta_at_sparsest"]
    assert run["adoption"]["interval"] == result["criteria"]["adoption"]["interval"]
    assert run["guard"]["mean_delta_at_densest"] == \
        result["criteria"]["guard"]["mean_delta_at_densest"]
    assert run["gates_all_passed"] == result["gates"]["all_passed"]
    assert body["registered_status"].startswith("FROZEN, NOT RUN")


def test_the_result_section_quotes_the_result_artifact():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    a = result["criteria"]["adoption"]
    g = result["criteria"]["guard"]
    flat = _flat()
    assert "## 9. Result" in DOC.read_text(encoding="utf-8")
    for token in ("%+.6f" % a["mean_delta_at_sparsest"],
                  "%+.6f" % a["interval"][0], "%+.6f" % a["interval"][1],
                  "%+.6f" % g["mean_delta_at_densest"],
                  result["decision"]["verdict"]):
        assert token in flat, token
    assert "preserved exactly as committed before the run" in flat
    assert not re.search(r"\{[a-z_]+\}", DOC.read_text(encoding="utf-8"))

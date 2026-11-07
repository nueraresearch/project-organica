"""The ranking pre-registration is frozen, allocates a fresh block, and its analysis path
can reach every branch of the decision table and be voided by every gate.

The fixtures are synthetic cells: no engine runs, no world is generated. The scorer is the
committed one, so a criterion that cannot fire here cannot fire in the run either.
"""

import json
import re
from pathlib import Path

import pytest

from benchmarks import score_rank_ordering as S
from benchmarks.decay_confirmation import harvest_seeds

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "rank_ordering_prereg.json"
DOC = ROOT / "docs" / "RANK-ORDERING-PREREGISTRATION.md"
DESIGN = ROOT / "docs" / "nonfrequency_ranking_design.json"
MAP = ROOT / "docs" / "bottleneck_map.json"


def _body():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _flat():
    return " ".join(DOC.read_text(encoding="utf-8").split())


def _harvest_elsewhere():
    """Seeds under seed-naming keys in every other docs artifact."""
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

    recorded = {ARTIFACT, ROOT / "docs" / "stage_b_protocol.json"}
    for path in sorted((ROOT / "docs").glob("*.json")):
        if path in recorded:
            continue
        try:
            walk(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
    return found


def _grid(delta_low, delta_high, *, presence=1.0, differ=True, identity=None,
          alternate=False, flat_rank=False, delta_override=None, covered_gt_asserted=False):
    """Synthetic cells built in precision space: covered = precision x cap."""
    body = S.prereg()
    design = body["design"]
    cells = []
    for seed in sorted(design["seeds"]):
        low = delta_low * (1 if (seed % 2 == 0 or not alternate) else -1)
        if delta_override and seed in delta_override:
            low = delta_override[seed]
        for cap in design["caps"]:
            for rho in design["densities"]:
                frac = (rho - design["densities"][0]) / (
                    design["densities"][-1] - design["densities"][0])
                gap = low if rho == design["densities"][0] else low + (delta_high - low) * frac
                world = round(rho * 240)
                control_precision = 0.10
                rho_rank = 0.3 if flat_rank else 0.55 * rho
                for arm in design["arms"]:
                    precision = (control_precision if arm == "control"
                                 else max(0.0, min(1.0, control_precision + gap)))
                    covered = round(precision * cap)
                    if covered_gt_asserted:
                        covered = cap + 1
                    selected = (["c-%d" % i for i in range(3)] if arm == "control"
                                else ["d-%d" % i for i in range(3)])
                    if not differ:
                        selected = ["same-%d" % i for i in range(3)]
                    cells.append({
                        "arm": arm, "cap": cap, "rho_world": rho, "seed": seed,
                        "coverage": round(min(1.0, covered / world), 6),
                        "precision": round(covered / cap, 6),
                        "rho_rank": rho_rank, "presence": presence,
                        "selected": selected, "asserted": cap, "covered": covered,
                    })
    return {"cells": cells,
            "identity": identity or {"rho_world": 1.0, "arms_identical": True,
                                     "delta": 0.0}}


# ---------------------------------------------------------------------------
# The artifact
# ---------------------------------------------------------------------------

def test_the_grid_is_the_documented_arithmetic():
    body = _body()
    design = body["design"]
    product = (len(design["arms"]) * len(design["caps"])
               * len(design["densities"]) * len(design["seeds"]))
    assert design["cells"] == product == 160
    assert body["allocation"]["cells"] == 160
    assert design["caps"] == [20, 40]
    assert design["densities"] == [0.1, 0.2, 0.4, 0.6, 0.8]
    assert design["world_edges_at_each_density"] == [
        round(d * 240) for d in design["densities"]]


def test_the_seed_block_is_fresh_and_registered():
    body = _body()
    block = body["seeds"]["block"]
    world = body["seeds"]["world"]
    bootstrap = body["seeds"]["bootstrap"]
    assert block == [world[0], world[-1]]
    assert len(world) == 8 and world == list(range(world[0], world[0] + 8))
    assert bootstrap == world[-1] + 1 and bootstrap not in world
    used = _harvest_elsewhere()
    assert not (set(world + [bootstrap]) & used), sorted(set(world) & used)
    harvested = harvest_seeds(ROOT / "docs")
    assert set(world + [bootstrap]) <= harvested


def test_the_bar_is_declared_before_any_cell():
    crit = _body()["criteria"]
    assert crit["M1_bar"] == 0.15
    assert crit["M2_min_gradient"] == 0.05
    assert "declared before any cell, not computed from a run" in crit["M1_bar_provenance"]
    assert crit["interval"] == 0.95 and crit["bootstrap_reps"] == 4000
    assert crit["sign_test"] == {"required": 7, "of": 8}
    assert crit["underpowered_width"] == 0.3
    assert "no line is closed" in crit["underpowered_rule"]


# ---------------------------------------------------------------------------
# The analysis path
# ---------------------------------------------------------------------------

def test_the_positive_pole_is_reachable():
    result = S.score(_grid(0.80, 0.05))
    assert result["gates"]["all_passed"]
    assert result["decision"]["verdict"] == "ORDERING SUPPORTED"
    assert result["decision"]["decision"] == "positive"


def test_a_decisive_null_licenses_the_negative_pole():
    result = S.score(_grid(0.0, 0.0))
    assert result["criteria"]["M1"]["passed"] is False
    assert result["criteria"]["M1"]["interval_width"] <= 0.3
    assert result["decision"]["verdict"] == "ORDERING NOT THE LEVER"
    assert result["decision"]["decision"] == "negative"


def test_a_wide_interval_is_underpowered_and_closes_nothing():
    seeds = sorted(S.prereg()["design"]["seeds"])
    override = {seed: -0.10 for seed in seeds}
    override[seeds[0]] = 1.0
    result = S.score(_grid(0.0, 0.0, delta_override=override))
    assert result["criteria"]["M1"]["passed"] is False
    assert result["criteria"]["M1"]["interval_width"] > 0.3
    assert result["decision"]["verdict"] == "UNDERPOWERED"
    assert result["decision"]["decision"] == "neither"


def test_a_level_without_a_gradient_is_not_the_positive_pole():
    result = S.score(_grid(0.40, 0.40))
    assert result["criteria"]["M1"]["passed"] is True
    assert result["criteria"]["M2"]["passed"] is False
    assert result["decision"]["verdict"] == "ORDERING HELPS, GRADIENT ABSENT"
    assert result["decision"]["decision"] == "neither"


def test_an_interaction_without_a_level_is_neither_pole():
    result = S.score(_grid(0.05, -0.60))
    assert result["criteria"]["M1"]["passed"] is False
    assert result["criteria"]["M2"]["passed"] is True
    assert result["decision"]["verdict"] == "GRADIENT WITHOUT LEVEL"
    assert result["decision"]["decision"] == "neither"


@pytest.mark.parametrize("kwargs,gate", [
    ({"differ": False}, "G0_liveness_cap_20"),
    ({"presence": 0.9}, "G1_presence_ceiling"),
    ({"covered_gt_asserted": True}, "G2_arithmetic_consistency"),
    ({"flat_rank": True}, "G3_axis_live"),
    ({"identity": {"rho_world": 1.0, "arms_identical": False, "delta": 0.0}},
     "G5_identity_at_density_1"),
    ({"identity": {"rho_world": 1.0, "arms_identical": True, "delta": 0.01}},
     "G5_identity_at_density_1"),
])
def test_every_gate_can_fire_and_voids_the_block(kwargs, gate):
    result = S.score(_grid(0.80, 0.05, **kwargs))
    assert result["gates"]["all_passed"] is False
    assert result["gates"][gate]["passed"] is False
    assert result["decision"]["verdict"] == "VOID"
    assert gate in result["decision"]["failed_gates"]
    assert result["criteria"]["M1"]["passed"] is None


def test_the_scorer_refuses_a_grid_that_is_not_the_preregistered_one():
    payload = _grid(0.80, 0.05)
    payload["cells"] = payload["cells"][:-1]
    with pytest.raises(ValueError, match="pre-registered grid"):
        S.score(payload)


def test_the_scorer_is_the_committed_script_and_does_not_touch_the_engine():
    path = ROOT / _body()["analysis"]["path"]
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    assert "import organica" not in source and "from organica" not in source
    assert _body()["analysis"]["frozen"] is True
    assert "rank_ordering_run.json" in _body()["analysis"]["input"]


# ---------------------------------------------------------------------------
# Frozen, and honest about it
# ---------------------------------------------------------------------------

def test_no_judged_cell_has_run_and_the_smoke_run_is_recorded():
    body = _body()
    assert body["status"].startswith("FROZEN, NOT RUN")
    assert body["not_run"]["cells_executed"] == 0
    assert body["not_run"]["engine_cycles"] == 0
    assert body["not_run"]["result_artifact_exists"] is False
    assert not (ROOT / "docs" / "rank_ordering_run.json").exists()
    assert not (ROOT / "docs" / "rank_ordering_result.json").exists()
    smoke = body["not_run"]["smoke"]
    assert smoke["seed"] not in body["design"]["seeds"]
    assert smoke["seed"] != body["seeds"]["bootstrap"]
    assert smoke["engine_cycles"] > 0
    assert smoke["pool"]["world_coverage_in_memory"] == 1.0
    assert smoke["audits_held"] is True
    assert smoke["observed"]["control_cap_20"]["coverage"] == 0.0
    assert smoke["observed"]["diversity_cap_20"]["coverage"] == 0.0
    assert smoke["counts"]["world_edges_in_top_40"] == 0
    assert body["not_run"]["blocked"]


def test_the_design_record_still_allocates_nothing_and_the_map_is_untouched():
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    assert design["allocation"]["seeds"] == 0
    rows = json.loads(MAP.read_text(encoding="utf-8"))["rows"]
    specified = [r for r in rows if r["study_specified"]]
    assert len(specified) == 1 and specified[0]["candidate"] == "Density interaction"


def test_the_document_quotes_the_artifact_and_has_no_placeholders():
    body = _body()
    flat = _flat()
    low, high = body["seeds"]["block"]
    for token in ("160", "%d-%d" % (low, high), str(body["seeds"]["bootstrap"]),
                  "%.2f" % body["criteria"]["M1_bar"], "4000", "95%",
                  "%.2f" % body["criteria"]["underpowered_width"], "0.05"):
        assert token in flat, token
    smoke = body["not_run"]["smoke"]
    for token in (str(smoke["seed"]), str(smoke["pool"]["rows"]),
                  str(smoke["counts"]["rank_of_first_world_edge"])):
        assert token in flat, token
    for row in body["decision_table"]:
        assert row["verdict"] in flat, row["verdict"]
    assert "No cell may run before this file is committed" in flat
    assert not re.search(r"\{[a-z_]+\}", DOC.read_text(encoding="utf-8"))

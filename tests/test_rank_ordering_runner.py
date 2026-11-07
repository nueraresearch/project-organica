"""The runner's harness audits must pass, its grid must be the frozen one, and the
cells it builds must be the cells the scorer accepts.

No engine runs here: the audits are pure, and the integration test builds synthetic
pools with the runner's own two orderings.
"""

import json
import random
from pathlib import Path

import pytest

from benchmarks import run_rank_ordering as R
from benchmarks import score_rank_ordering as S

ROOT = Path(__file__).resolve().parent.parent
RUN = ROOT / "docs" / "rank_ordering_run.json"


def test_the_self_tests_pass():
    report = R.self_test()
    assert report["all_passed"], {k: v for k, v in report["checks"].items()
                                  if not v["passed"]}


def test_the_world_generator_has_the_density_it_claims():
    body = R.prereg()
    for rho in body["design"]["densities"]:
        for seed in body["design"]["seeds"][:2]:
            edges = R.world_edges(seed, rho)
            assert len(edges) == round(rho * 240)
            assert len(edges) == len(set(edges))
            assert all(a in R.VOCAB and b in R.VOCAB and a != b for a, b in edges)


def test_every_world_edge_is_emitted_and_non_world_rows_exist():
    for rho in R.prereg()["design"]["densities"]:
        stream = R.density_stream(R.prereg()["design"]["seeds"][0], rho)
        world = R.world_edges(R.prereg()["design"]["seeds"][0], rho)
        emitted = {"%s>%s" % (tags[0], tags[1])
                   for tags in (text.split() for text in stream)}
        assert {"%s>%s" % edge for edge in world} <= emitted
        assert R.designed_pairs(stream) - world, rho


def test_the_diversity_ordering_spreads_across_sources():
    # one source owns every high-count row; a count ordering must spend on it
    rows = [("amber", "birch", 9), ("amber", "cedar", 8), ("amber", "maple", 7)]
    rows += [(tag, "slate", 1) for tag in R.VOCAB if tag != "slate"]
    control = R.rank_control(rows, 6)
    diversity = R.rank_diversity(rows, 6)
    assert len({a for a, _b in control}) < len({a for a, _b in diversity})
    assert len({a for a, _b in diversity}) == 6


def test_the_identity_check_is_identical_and_zero():
    identity = R.identity_audit()
    assert identity["arms_identical"] is True
    assert identity["delta"] == 0
    assert identity["pool"] <= identity["cap"]
    assert identity["passed"] is True


def test_the_plan_is_the_preregistered_grid():
    body = R.prereg()
    cells = R.plan(body)
    assert len(cells) == 160
    design = body["design"]
    assert {c["cap"] for c in cells} == set(design["caps"])
    assert {c["arm"] for c in cells} == set(design["arms"])
    assert {round(c["rho_world"], 6) for c in cells} == set(design["densities"])
    assert {c["seed"] for c in cells} == set(design["seeds"])


def test_the_runner_refuses_a_grid_off_the_preregistration():
    body = json.loads(R.PREREG.read_text(encoding="utf-8"))
    body["design"]["seeds"] = body["design"]["seeds"][:4]
    with pytest.raises(SystemExit, match="eight distinct seeds"):
        R.assert_grid(body)
    body = json.loads(R.PREREG.read_text(encoding="utf-8"))
    body["status"] = "DRAFT, NOT FROZEN"
    with pytest.raises(SystemExit, match="not frozen"):
        R.assert_grid(body)


def test_the_runner_refuses_a_state_that_already_has_cells():
    body = json.loads(R.PREREG.read_text(encoding="utf-8"))
    body["not_run"]["cells_executed"] = 1
    with pytest.raises(SystemExit, match="already records executed cells"):
        R.plan(body)


def test_the_runner_refuses_a_record_blocked_by_a_smoke_finding(tmp_path):
    body = json.loads(R.PREREG.read_text(encoding="utf-8"))
    body["not_run"]["blocked"] = "both arms cover zero world edges at the primary point"
    with pytest.raises(SystemExit, match="blocked"):
        R.run(tmp_path / "never.json", body)
    assert not (tmp_path / "never.json").exists()


def test_the_runner_never_opens_the_live_database():
    source = Path(R.__file__).read_text(encoding="utf-8")
    assert "temp_db(" in source
    assert "LIVE_DB" in source and "refusing to open the live database" in source


def _pools():
    """Synthetic engine pools in the runner's own shape: filler outranks world edges."""
    body = R.prereg()
    for seed in body["design"]["seeds"]:
        for rho in body["design"]["densities"]:
            world = R.world_edges(seed, rho)
            pool = [(a, b, R.EDGE_REPEATS) for a, b in sorted(world)]
            pool += [(a, b, R.FILLER_REPEATS) for a, b in R.filler_pairs()
                     if (a, b) not in world]
            # a few extra non-world rows, as cross-event transitions produce
            rng = random.Random(seed + round(rho * 100))
            for _ in range(5):
                a, b = rng.sample(sorted(R.VOCAB), 2)
                if (a, b) not in world:
                    pool.append((a, b, 3))
            yield seed, rho, pool, world


def test_the_runner_payload_is_a_payload_the_scorer_accepts():
    body = R.prereg()
    cells = []
    for seed, rho, pool, world in _pools():
        cells.extend(R.cells_for(seed, rho, pool, world, body))
    payload = {"prereg": body["prereg"], "cells": cells,
               "identity": R.identity_audit()}
    assert len(payload["cells"]) == 160
    result = S.score(payload, body)
    assert result["cells"] == 160
    assert result["gates"]["all_passed"] is True
    assert result["decision"]["verdict"] in {
        "ORDERING SUPPORTED", "ORDERING HELPS, GRADIENT ABSENT",
        "GRADIENT WITHOUT LEVEL", "ORDERING NOT THE LEVER", "UNDERPOWERED"}
    assert result["gates"]["G0_liveness_cap_20"]["passed"] is True


def test_no_judged_cell_has_run():
    assert not RUN.exists()

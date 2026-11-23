"""Guards for the D3 seed-varying confirmation block and its frozen protocol."""
LAYER = "dry-run"  # benchmarks/test_layers.py: the module's execution layer
import copy
import json

import pytest

from benchmarks import d3_persistence_prereg as P
from benchmarks import d3_persistence_run as R
from benchmarks import d3_persistence_seed_varying as S

BODY = S.prereg()
SEEDS = list(BODY["design"]["seeds"])


def test_the_block_is_twenty_four_cells_on_a_fresh_seed_window():
    assert len(SEEDS) == 6
    assert len(set(SEEDS)) == 6
    assert BODY["design"]["bootstrap"] == 20611107
    assert BODY["design"]["cells"] == 24 == 2 * 2 * len(SEEDS)
    assert not set(SEEDS) & {20410301, 20410302, 20410303, 20410304, 20410305, 20410306}
    assert BODY["prior"]["prereg"] == "D3-PERSISTENCE-1"


def test_the_g8_seed_axis_gate_is_precommitted():
    assert "G8_seed_axis_live" in BODY["gates"]
    assert "at least two distinct trajectory signatures" in BODY["gates"]["G8_seed_axis_live"]
    assert BODY["design"]["world_variation"]


def test_each_seed_gets_its_own_world_in_both_designs():
    for design in ("L3_hub1_t3_mixed", "L1_hub1_t3_disjoint"):
        streams = [S.seeded_events(design, seed) for seed in SEEDS]
        assert all(len(stream) == 216 for stream in streams)
        assert len({S.world_digest(stream) for stream in streams}) == 6


def test_the_page_is_the_record():
    assert S.PREREG_DOC.read_text(encoding="utf-8") == S.render_prereg(BODY)


def test_the_result_is_the_frozen_scorers_reading():
    artifact = json.loads(S.ARTIFACT.read_text(encoding="utf-8"))
    label, details = P.verdict(BODY, artifact)
    assert artifact["prereg"] == "D3-PERSISTENCE-2"
    assert label == artifact["verdict"]
    assert details == artifact["details"]
    assert len(artifact["cells"]) == 24
    assert artifact["seed_axis"]["live"] is True
    R.require_varied_treatment(artifact)
    assert artifact["seed_axis"]["effective_n"] >= 2
    for stage in ("witness", "preflight"):
        assert len({cell["world_digest"] for cell in artifact["cells"]
                    if cell["stage"] == stage}) == 6


def test_g8_voids_a_block_with_one_repeated_treatment_trajectory():
    artifact = json.loads(S.ARTIFACT.read_text(encoding="utf-8"))
    forged = copy.deepcopy(artifact)
    first = next(cell for cell in forged["cells"]
                 if cell["stage"] == "preflight" and cell["arm"] == "treatment")
    for cell in forged["cells"]:
        if cell["stage"] == "preflight" and cell["arm"] == "treatment":
            cell["digest"] = first["digest"]
            cell["theory_counts"] = list(first["theory_counts"])
            cell["first_zero_cycle"] = first["first_zero_cycle"]
            cell["recall_early"] = first["recall_early"]
            cell["predictions_early"] = first["predictions_early"]
            cell["world_digest"] = first["world_digest"]
    forged["seed_axis"] = S.seed_axis(forged["cells"])
    label, details = P.verdict(BODY, forged)
    assert label == "VOID"
    assert details["gate"] == "G8_seed_axis_live"
    assert details["distinct_preflight_treatment"] == 1


def test_the_seed_varying_finish_refuses_a_degenerate_axis(monkeypatch, tmp_path):
    artifact = json.loads(S.ARTIFACT.read_text(encoding="utf-8"))
    forged = copy.deepcopy(artifact)
    first = next(cell for cell in forged["cells"]
                 if cell["stage"] == "preflight" and cell["arm"] == "treatment")
    for cell in forged["cells"]:
        if cell["stage"] == "preflight" and cell["arm"] == "treatment":
            for key in ("theory_counts", "first_zero_cycle", "recall_early",
                        "predictions_early"):
                cell[key] = copy.deepcopy(first[key])
    forged["seed_axis"] = S.seed_axis(forged["cells"])
    out = tmp_path / "d3_persistence_seed_varying_run.json"
    page = tmp_path / "D3-PERSISTENCE-SEED-VARYING-RESULT.md"
    monkeypatch.setattr(S, "ARTIFACT", out)
    monkeypatch.setattr(S, "RESULT", page)
    monkeypatch.setattr(S, "build", lambda: forged)
    with pytest.raises(SystemExit, match="single-world pass cannot be reported"):
        S.finish()
    assert not out.exists()
    assert not page.exists()


def test_the_runner_check_is_clean():
    assert S.check() == 0

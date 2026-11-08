"""The paired 0.9924/0.9925 check is reproducible, and its gates can fail."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from benchmarks import decay_paired_bracket as paired
from benchmarks.decay_threshold_prereg import FROZEN_DIGEST, protocol_digest

ROOT = Path(__file__).resolve().parents[1]


def load_artifact():
    path = ROOT / "docs" / "decay_paired_bracket.json"
    assert path.exists(), "the paired-bracket artifact has not been written"
    return json.loads(path.read_text(encoding="utf-8"))


def load_cells():
    return paired.cells_from_parts()


def rebuilt(cells):
    """An artifact that agrees with the given cells, for testing the label logic."""
    artifact = copy.deepcopy(load_artifact())
    artifact["cells"] = cells
    artifact["gates"] = paired.gates_for(cells)
    artifact["predictions"] = paired.predictions_for(cells)
    artifact["label"] = paired.label_for(cells, artifact["gates"])
    artifact["prediction_paired_bracket"] = (
        artifact["predictions"]["P1_lower_dead_all"]
        and artifact["predictions"]["P2_upper_alive_all"]
    )
    artifact["pairs"] = []
    return artifact


def test_the_committed_artifact_passes_its_own_check():
    assert paired.validate(load_artifact(), load_cells()) == []


def test_every_cell_equals_its_committed_part():
    for cell in load_artifact()["cells"]:
        part = json.loads((ROOT / cell["part"]).read_text(encoding="utf-8"))
        assert part["factor"] == cell["factor"]
        assert part["seed"] == cell["seed"]
        for key in paired.CELL_KEYS:
            if key in ("factor", "seed"):
                continue
            assert cell[key] == part["facts"][key], (cell["part"], key)


def test_the_check_is_a_paired_bracket_at_one_cycle():
    cells = load_cells()
    lower = [cell for cell in cells if cell["factor"] == paired.LOWER]
    upper = [cell for cell in cells if cell["factor"] == paired.UPPER]
    assert {cell["seed"] for cell in lower} == {cell["seed"] for cell in upper} == set(paired.SEEDS)
    assert all(cell["death_cycle"] == paired.CYCLES for cell in lower)
    assert all(cell["death_cycle"] == paired.ALIVE for cell in upper)


def test_a_missing_cell_voids_the_check():
    cells = [cell for cell in load_cells()
             if not (cell["factor"] == paired.UPPER and cell["seed"] == 20302703)]
    artifact = rebuilt(cells)
    assert artifact["label"] == "VOID"
    assert artifact["gates"]["G3_cells_complete"] is False
    assert artifact["gates"]["G4_seed_pairing"] is False
    assert paired.validate(artifact, cells) == []


def test_a_live_factor_gate_catches_a_wrong_factor():
    cells = copy.deepcopy(load_cells())
    for cell in cells:
        if cell["factor"] == paired.UPPER:
            cell["decay_factors"] = [paired.LOWER]
            break
    artifact = rebuilt(cells)
    assert artifact["label"] == "VOID"
    assert artifact["gates"]["G1_factor_live"] is False
    assert paired.validate(artifact, cells) == []


def test_the_artifact_cannot_disagree_with_the_parts():
    artifact = copy.deepcopy(load_artifact())
    artifact["cells"][0]["death_cycle"] += 1
    assert paired.validate(artifact, load_cells()) != []


def test_the_bracket_can_fail():
    cells = copy.deepcopy(load_cells())
    for cell in cells:
        if cell["factor"] == paired.UPPER:
            cell["death_cycle"] = paired.CYCLES
    artifact = rebuilt(cells)
    assert artifact["gates"]["G1_factor_live"] is True
    assert artifact["gates"]["G3_cells_complete"] is True
    assert artifact["label"] == "PAIRED_BRACKET_NOT_CONFIRMED"
    assert artifact["predictions"]["P2_upper_alive_all"] is False
    assert paired.validate(artifact, cells) == []


def test_the_page_names_the_label_and_has_no_placeholder():
    artifact = load_artifact()
    page = (ROOT / "docs" / "DECAY-PAIRED-BRACKET.md").read_text(encoding="utf-8")
    assert artifact["label"] in page
    assert "{" not in page and "}" not in page
    assert "Not yet written" not in page


def test_the_protocol_records_section_14_and_keeps_its_frozen_digest():
    text = (ROOT / "docs" / "DECAY-THRESHOLD-PREREGISTRATION.md").read_text(encoding="utf-8")
    assert "## 14. Paired same-block check" in text
    for label in paired.BUCKETS:
        assert label in text
    assert protocol_digest(text) == FROZEN_DIGEST

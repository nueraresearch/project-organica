"""The competition-collapse probe is reproducible, and its labels can be reached."""

from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import copy
import json
from pathlib import Path

from benchmarks import decay_competition_probe as probe
from benchmarks.decay_threshold_prereg import FROZEN_DIGEST, protocol_digest

ROOT = Path(__file__).resolve().parents[1]


def load_artifact():
    path = ROOT / "docs" / "decay_competition_probe.json"
    assert path.exists(), "the competition-probe artifact has not been written"
    return json.loads(path.read_text(encoding="utf-8"))


def load_cells():
    return probe.cells_from_parts()


def rebuilt(cells):
    artifact = copy.deepcopy(load_artifact())
    artifact["cells"] = cells
    artifact["gates"] = probe.gates_for(cells, probe.control_facts())
    artifact["predictions"] = probe.predictions_for(cells)
    artifact["seed_insensitive"] = probe.seed_insensitive(cells)
    artifact["label"] = probe.label_for(cells, artifact["gates"])
    artifact["prediction_same_pair"] = (
        artifact["predictions"]["P1_same_subject_all_seeds"]
        and artifact["predictions"]["P2_two_competing_all_seeds"]
    )
    return artifact


def test_the_committed_artifact_passes_its_own_check():
    assert probe.validate(load_artifact(), load_cells()) == []


def test_the_control_reproduces_the_committed_probe():
    control = probe.control_facts()
    assert control == {"subject": "bravo", "support_count": 866, "supports": [433, 433]}
    assert load_artifact()["gates"]["G3_control_reproduced"] is True


def test_every_seed_has_the_competing_pair_loss_signature():
    cells = load_cells()
    assert {cell["seed"] for cell in cells} == set(probe.SEEDS)
    for cell in cells:
        assert cell["death_cycle"] == cell["last_live_cycle"] + 1
        assert cell["theories_at_death"] == 0
        assert cell["subjects_with_competing_at_death"] == {}
        assert len(cell["top_theory"]["competing"]) >= 2
        assert probe.signature_holds(cell)


def test_the_raw_death_list_still_carries_the_significance_marker():
    for cell in load_cells():
        assert cell["subjects_with_pairs_at_death"], "the raw marker count is not recorded"
        assert all(count == 2 for count in cell["subjects_with_pairs_at_death"].values())


def test_the_three_cells_are_the_same_trajectory():
    artifact = load_artifact()
    assert artifact["seed_insensitive"] is True
    assert probe.seed_insensitive(load_cells()) is True


def test_the_artifact_cannot_disagree_with_the_parts():
    artifact = copy.deepcopy(load_artifact())
    artifact["cells"][0]["top_theory"]["support_count"] += 1
    assert probe.validate(artifact, load_cells()) != []


def test_a_missing_seed_voids_the_check():
    cells = [cell for cell in load_cells() if cell["seed"] != probe.SEEDS[-1]]
    artifact = rebuilt(cells)
    assert artifact["label"] == "VOID"
    assert artifact["gates"]["G4_threshold_block"] is False
    assert probe.validate(artifact, cells) == []


def test_a_different_subject_reaches_same_mechanism():
    cells = copy.deepcopy(load_cells())
    cells[1]["top_theory"]["subject"] = "alpha"  # not the control seed
    artifact = rebuilt(cells)
    assert artifact["label"] == "SAME_MECHANISM"
    assert probe.validate(artifact, cells) == []


def test_a_death_with_a_competing_pair_is_signature_absent():
    cells = copy.deepcopy(load_cells())
    cells[0]["theories_at_death"] = 1
    cells[0]["subjects_with_competing_at_death"] = {"alpha": 2}
    artifact = rebuilt(cells)
    assert artifact["label"] == "SIGNATURE_ABSENT"
    assert probe.validate(artifact, cells) == []


def test_the_page_names_the_label_and_has_no_placeholder():
    artifact = load_artifact()
    page = (ROOT / "docs" / "DECAY-COMPETITION-PROBE.md").read_text(encoding="utf-8")
    assert artifact["label"] in page
    assert "{" not in page and "}" not in page
    assert "Not yet written" not in page


def test_the_protocol_records_section_15_and_keeps_its_frozen_digest():
    text = (ROOT / "docs" / "DECAY-THRESHOLD-PREREGISTRATION.md").read_text(encoding="utf-8")
    assert "## 15. Competition-collapse signature" in text
    assert "### 15.1 Correction to the endpoint's hypothesis population" in text
    for label in probe.BUCKETS:
        assert label in text
    assert protocol_digest(text) == FROZEN_DIGEST

"""A pair-split construction holds candidates fixed while the alphabet grows."""
import json
from pathlib import Path

from benchmarks import a1_offset_discriminator_spec as spec

DOC = json.loads(Path("docs/a1_offset_discriminator_spec.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert spec.problems(DOC) == []
    assert spec.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert DOC["differential"]["measured_difference"] is None
    assert DOC["constants"]["active"] == 4


def test_the_split_blocks_match_the_16_tag_candidate_count():
    blocks = {row["label"]: row for row in DOC["blocks"]}
    reference = blocks["fresh-16"]["candidates_mean"]
    for label, density in (("split-32", 1.994792), ("split-48", 1.329861)):
        assert blocks[label]["candidates_mean"] == reference
        assert blocks[label]["density"] == density
        assert blocks[label]["active"] == 4
    assert blocks["split-32"]["tags"] == 32
    assert blocks["split-48"]["tags"] == 48
    assert blocks["fresh-16"]["tags"] == 16


def test_both_blocks_use_every_declared_tag():
    controls = {row["name"]: row for row in DOC["controls"]}
    assert controls["split-32 uses every declared tag"]["ok"] is True
    assert controls["split-48 uses every declared tag"]["ok"] is True
    assert controls["split-32 uses every declared tag"]["observed"] == 32
    assert controls["split-48 uses every declared tag"]["observed"] == 48


def test_the_size_model_predicts_one_level_and_density_predicts_two():
    predicted = {row["label"]: row for row in DOC["predictions"]}
    assert predicted["split-32"]["size_offset"] == predicted["split-48"]["size_offset"]
    assert predicted["split-32"]["size_offset"] == predicted["fresh-16"]["size_offset"]
    assert (predicted["split-32"]["density_offset"],
            predicted["split-48"]["density_offset"]) == (0.761487, 0.877867)
    differential = DOC["differential"]
    assert differential["size_predicted_difference"] == 0.0
    assert differential["density_predicted_difference"] == -0.11638


def test_the_differential_clears_the_declared_floor():
    differential = DOC["differential"]
    assert abs(differential["density_predicted_difference"]) >= spec.DECISION_CEILING
    assert abs(differential["size_predicted_difference"]) <= spec.DECISION_FLOOR
    rule = DOC["decision_rule"]
    assert "0.05" in rule["if_abs_below"]
    assert "0.09" in rule["if_abs_above"]
    assert rule["density_model"].startswith("negative")


def test_controls_reproduce_both_committed_laws():
    controls = {row["name"]: row for row in DOC["controls"]}
    assert controls["the committed 16-tag law reproduces 20630101"]["observed"] == 64
    assert controls["the committed 16-tag law reproduces 20630102"]["observed"] == 63
    assert controls["the committed 28-tag law reproduces 20660101"]["observed"] == 169
    assert all(row["ok"] for row in DOC["controls"])


def test_no_measurement_is_recorded():
    assert DOC["found"]["seeds_per_block"] == 6
    assert DOC["found"]["candidate_rows"] == 12
    assert len(DOC["candidate_rows"]) == 12
    assert all(row["candidate_edges"] in (63, 64) for row in DOC["candidate_rows"])

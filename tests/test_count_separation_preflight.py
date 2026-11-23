"""The preflight's rule is probed on synthetic fixtures and its collection path on a hand-built stream."""
import json

from benchmarks import count_separation_preflight as preflight

# The preflight's pure rule function. Aliased away from "measure" so the layer
# census does not read this synthetic test as a harness --measure entry point.
apply_rule = preflight.measure

LAYER = "synthetic"  # the smoke test runs the engine over a hand-built stream


def test_the_preflight_rule_holds_on_synthetic_fixtures():
    assert preflight.main(["--self-test"]) == 0


def test_the_collection_path_on_a_hand_built_stream():
    assert preflight.smoke_test() == []


def test_verbose_collection_prints_the_per_seed_heartbeat(capsys):
    assert preflight.smoke_test(verbose=True) == []
    out = capsys.readouterr().out
    assert "[preflight] seed hand-built: cycle 18/18" in out


def test_the_margin_curve_and_gold_minimum_are_reported():
    verdict = apply_rule([preflight._fixture(1, decoys=1, decoy_cooc=7)])
    assert verdict.floor == 10
    assert verdict.gold_min[1] == 10
    assert verdict.curve[1][-1] == (10, preflight.GOLD_PAIRS, preflight.GOLD_PAIRS)
    assert (1, preflight.GOLD_PAIRS + 1, preflight.GOLD_PAIRS + 1) in verdict.curve[1]
    text = preflight.report(verdict)
    assert "gold min=10" in text
    assert "M(F)/directed(F):" in text
    assert "PASS: 18 <= M_s(F*) <= 69" in text


def test_a_binding_prediction_cap_is_marked_not_silent():
    verdict = apply_rule([preflight._fixture(
        1, decoys=preflight.BAND_HIGH - preflight.GOLD_PAIRS,
        reverse_temporal=10)])
    assert verdict.passed is True
    assert verdict.curve[1][-1][2] == 2 * preflight.BAND_HIGH
    text = preflight.report(verdict)
    assert "directed admitted=138/112 (CAP BINDS)" in text
    assert "PASS OF THE BAND ONLY" in text
    assert "\nPASS: 18 <= M_s(F*) <= 69" not in text


def _decision_record(tmp_path, **fields):
    body = {"kind": "build_decision", "decided_by": "owner",
            "date": "2026-11-20", "allocation_law": "a", "term_sheet": "T1"}
    body.update(fields)
    path = tmp_path / "DECISION-COOCCURRENCE-BUILD.json"
    path.write_text(json.dumps(body), encoding="utf-8")
    return path


def test_run_refuses_without_a_recorded_owner_decision(tmp_path, monkeypatch):
    monkeypatch.setattr(preflight, "DECISION_RECORD", tmp_path / "missing.json")
    assert preflight.decision_problems()
    assert preflight.main(["--run"]) == 2


def test_run_refuses_an_incomplete_or_inapplicable_decision(tmp_path):
    for fields in ({"allocation_law": "b"}, {"term_sheet": "T2"},
                   {"decided_by": "an agent"}, {"date": "not a date"},
                   {"kind": "constraint_decision"}):
        assert preflight.decision_problems(_decision_record(tmp_path, **fields))


def test_run_accepts_a_recorded_a_t1_decision(tmp_path):
    assert preflight.decision_problems(_decision_record(tmp_path)) == []

"""The source-diversified top-20 diagnostic stays bounded and post hoc."""
LAYER = "static"

import json

import pytest

from benchmarks import source_diversified_top20 as gate


def test_artifact_page_and_headline():
    art = json.loads(gate.ARTIFACT.read_text(encoding="utf-8"))
    assert art["kind"] == "source_diversified_top20"
    assert art["status"] == "POST-HOC DIAGNOSTIC"
    assert art["posthoc"] is True
    assert art["prereg"] is None
    assert not gate.engine_stamp.missing(art)
    assert art["verdict"] == "NO RELIABLE RECOVERY GAIN"
    assert art["baseline"]["selected"] == 120
    assert art["baseline"]["recovered"] == 18
    assert art["cap3"]["selected"] == 120
    assert art["cap3"]["recovered"] == 19
    assert art["cap3"]["displaced"] == 8
    assert art["cap3"]["displaced_asserted"] == 0
    assert art["cap3"]["added"] == 8
    assert art["cap3"]["added_asserted"] == 1
    assert gate.PAGE.read_text(encoding="utf-8") == gate.render(art)
    assert not gate.problems(art)


def test_cap_sweep_is_monotone_in_the_expected_direction():
    art = json.loads(gate.ARTIFACT.read_text(encoding="utf-8"))
    sweep = {row["cap"]: row for row in art["cap_sweep"]}
    assert sweep[1]["full_windows"] == 0
    assert sweep[1]["selected"] < 120
    assert sweep[2]["recovered"] == 18
    assert sweep[2]["displaced_asserted"] == 3
    assert sweep[3]["recovered"] == 19
    assert sweep[4]["recovered"] == 18
    assert sweep[5]["recovered"] == 18
    assert sweep[5]["displaced"] == 0
    assert sweep[5]["added"] == 0


def test_cap_is_applied_per_seed_and_the_gain_is_one_seed():
    art = json.loads(gate.ARTIFACT.read_text(encoding="utf-8"))
    cap3 = art["cap3"]
    assert cap3["full_windows"] == 6
    changed = [row for row in cap3["per_seed"]
               if row["recovered"] != row["baseline_recovered"]]
    assert [(row["seed"], row["baseline_recovered"], row["recovered"])
            for row in changed] == [(20613101, 0, 1)]
    assert all(row["max_source_seats"] <= 3 for row in cap3["per_seed"])
    assert max(row["max_source_seats"] for row in cap3["per_seed"]) == 3


def test_other_rank_fields_do_not_reproduce_the_gain():
    art = json.loads(gate.ARTIFACT.read_text(encoding="utf-8"))
    by_field = {row["rank_field"]: row for row in art["rank_sensitivity"]}
    assert by_field["min_rank"]["cap3_recovered"] == 19
    assert by_field["median_rank"]["cap3_recovered"] == 23
    assert by_field["median_rank"]["baseline_recovered"] == 25
    assert by_field["final_rank"]["cap3_recovered"] == 23
    assert by_field["final_rank"]["baseline_recovered"] == 24
    assert by_field["median_rank"]["cap3_displaced_asserted"] == 3
    assert by_field["final_rank"]["cap3_displaced_asserted"] == 3


def test_check_rejects_a_tampered_headline():
    art = json.loads(gate.ARTIFACT.read_text(encoding="utf-8"))
    art["cap3"]["recovered"] = 20
    assert "cap-3 recovery" in gate.problems(art)
    art = json.loads(gate.ARTIFACT.read_text(encoding="utf-8"))
    art["checks"]["cap3_19_of_26"] = False
    assert "checks" in gate.problems(art)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

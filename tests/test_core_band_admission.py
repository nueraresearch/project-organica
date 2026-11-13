"""CORE-BAND-ADMISSION-1 is frozen, granted, run and correctly recorded as VOID."""
LAYER = "static"

import json

from benchmarks import core_band_admission as gate
from benchmarks import core_band_admission_prereg as block


def test_prereg_is_frozen_granted_and_run():
    doc = block.record()
    assert doc["prereg"] == "CORE-BAND-ADMISSION-1"
    assert doc["status"] == "FROZEN, RUN"
    assert doc["frozen_on"] == "2026-11-12"
    assert doc["design"]["seeds"] == [20617101, 20617102, 20617103,
                                      20617104, 20617105, 20617106]
    assert doc["design"]["cells"] == 12
    assert doc["design"]["cap"] == 112
    assert doc["authorisation"]["granted"] is True
    assert doc["runner"]["built"] is True
    assert doc["runner"]["cells_run"] == 12
    assert block.RESULT.exists()
    assert block.problems() == []


def test_result_is_void_on_the_frozen_gates():
    art = json.loads(gate.ARTIFACT.read_text(encoding="utf-8"))
    assert art["verdict"] == "VOID"
    assert art["cells"] == 12
    assert art["gates"]["C1_build"]["passed"] is True
    assert art["gates"]["C2_world"]["passed"] is True
    assert art["gates"]["C3_tier"]["passed"] is False
    assert art["gates"]["C4_length"]["passed"] is False
    assert art["gates"]["C5_ledger"]["passed"] is True
    assert art["gates"]["C6_control"]["passed"] is True
    assert art["gates"]["C7_treatment"]["passed"] is True


def test_control_and_treatment_are_identical_and_zero_replacement():
    art = json.loads(gate.ARTIFACT.read_text(encoding="utf-8"))
    assert art["control"]["coverage"] == 1.0
    assert art["treatment"]["coverage"] == 1.0
    assert art["control"]["replacements"] == 0
    assert art["treatment"]["replacements"] == 0
    assert art["control"]["false_admission"] == art["treatment"]["false_admission"]
    assert art["treatment"]["false_admission_difference"] == 0.0
    assert art["window_digests_equal"] is True


def test_void_reading_does_not_claim_a_recovery():
    art = json.loads(gate.ARTIFACT.read_text(encoding="utf-8"))
    assert "no coverage effect is adjudicated" in art["reading"]
    assert "identical" in art["reading"]
    assert "already serves" not in art["reading"]


def test_page_and_check_are_current():
    art = json.loads(gate.ARTIFACT.read_text(encoding="utf-8"))
    assert gate.PAGE.read_text(encoding="utf-8") == gate.render(art)
    assert gate.main(["--check"]) == 0


if __name__ == "__main__":
    raise SystemExit(__import__("pytest").main([__file__, "-q"]))

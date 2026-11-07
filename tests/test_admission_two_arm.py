"""The two-arm registration must be fixed before it runs, and every outcome must be reachable.

The scorer is exercised on synthetic cells: no engine runs, no world is generated. If a verdict
cannot be reached here it cannot be reached by the block either.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from benchmarks import score_admission_two_arm as S

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "admission_two_arm_prereg.json"
DOC = ROOT / "docs" / "ADMISSION-TWO-ARM-PREREGISTRATION.md"
RUN = ROOT / "docs" / "admission_two_arm_run.json"
RESULT = ROOT / "docs" / "admission_two_arm_result.json"
ORDERING = ROOT / "docs" / "rank_ordering_result.json"


def _body():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _flat():
    return " ".join(DOC.read_text(encoding="utf-8").split())


def _payload(gain, guard=0.0, raw=1.0, differ=True):
    body = _body()
    cells = []
    for seed in body["design"]["seeds"]:
        g = gain(seed)
        for arm in body["design"]["arms"]:
            coverage = 0.30 + (g if arm == "adopted" else 0.0)
            covered = round(coverage * 100)
            precision = 0.75 + (guard if arm == "adopted" else 0.0)
            asserted = max(1, round(covered / precision))
            cells.append({
                "seed": seed, "arm": arm, "world_edges": 100,
                "covered": covered, "asserted": asserted,
                "coverage": round(covered / 100, 6),
                "precision": round(covered / asserted, 6),
                "raw_temporal_coverage": raw,
                "asserted_fingerprint": ("a" if arm == "reference" else "b") if differ else "a",
            })
    return {"prereg": body["prereg"], "cells": cells,
            "determinism": {"matched": True}, "boundary": {"frozen_files_clean": True}}


FLAT_ZERO = lambda seed: 0.0
FLAT_GAIN = lambda seed: 0.10


def test_the_grid_is_two_arms_by_eight_seeds():
    design = _body()["design"]
    assert design["cells"] == len(design["arms"]) * len(design["seeds"]) == 16
    assert design["arms"] == ["reference", "adopted"]
    assert design["cycles"] == 120


def test_the_seed_block_is_fresh_and_contiguous():
    body = _body()
    world, bootstrap = body["seeds"]["world"], body["seeds"]["bootstrap"]
    assert len(world) == 8 and world == list(range(world[0], world[0] + 8))
    assert bootstrap == world[-1] + 1
    used = set()
    # This block's own artifacts name its seeds by construction; freshness is
    # judged against documents that predate it.
    recorded = {ARTIFACT, DOC, RUN, RESULT,
                ROOT / "docs" / "stage_b_protocol.json",
                ROOT / "docs" / "USER-MANUAL.md"}
    for path in sorted(list((ROOT / "docs").glob("*.json"))
                       + list((ROOT / "docs").glob("*.md"))):
        if path in recorded:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        used |= {int(m.group()) for m in re.finditer(r"\b\d{7,9}\b", text)}
    assert not (set(world + [bootstrap]) & used), sorted(set(world) & used)


def test_the_bar_is_carried_from_the_completed_run_and_says_so():
    crit = _body()["criteria"]
    mean = json.loads(ORDERING.read_text(encoding="utf-8"))["criteria"]["M1"]["mean_delta_at_min_density"]
    assert crit["bar"] == int(mean / 2 * 100) / 100
    assert "%.4f" % mean in crit["bar_provenance"]
    assert "NOT calibrated on this" in crit["bar_provenance"]
    assert crit["guard_bar"] == -0.05
    assert "declared, not calibrated" in crit["guard_provenance"]


def test_a_gain_without_a_precision_loss_is_claimed():
    result = S.score(_payload(FLAT_GAIN))
    assert result["gates"]["all_passed"] is True
    assert result["criteria"]["adoption"]["passed"] is True
    assert result["decision"]["verdict"] == "ADOPTED ARM GAINS"


def test_a_gain_with_a_precision_loss_is_priced_not_claimed():
    result = S.score(_payload(FLAT_GAIN, guard=-0.10))
    assert result["criteria"]["adoption"]["passed"] is True
    assert result["criteria"]["guard"]["passed"] is False
    assert result["decision"]["verdict"] == "PRICED TRADE"


def test_no_gain_closes_this_layer():
    result = S.score(_payload(FLAT_ZERO))
    assert result["criteria"]["adoption"]["passed"] is False
    assert result["decision"]["verdict"] == "NO GAIN ON THIS LAYER"


def test_a_wide_interval_is_underpowered():
    result = S.score(_payload(lambda seed: 0.25 if seed % 2 == 0 else -0.25))
    adoption = result["criteria"]["adoption"]
    assert adoption["passed"] is False
    assert adoption["interval_width"] > 0.3
    assert result["decision"]["verdict"] == "UNDERPOWERED"


def test_a_world_that_was_not_present_voids_the_block():
    result = S.score(_payload(FLAT_GAIN, raw=0.5))
    assert result["gates"]["G1_world_present"]["passed"] is False
    assert result["decision"]["verdict"] == "VOID"
    assert result["criteria"] == {}


def test_arms_that_never_differ_void_the_block():
    result = S.score(_payload(FLAT_GAIN, differ=False))
    assert result["gates"]["G0_liveness"]["passed"] is False
    assert result["decision"]["verdict"] == "VOID"


def test_a_dirty_frozen_file_voids_the_block():
    payload = _payload(FLAT_GAIN)
    payload["boundary"]["frozen_files_clean"] = False
    assert S.score(payload)["decision"]["verdict"] == "VOID"


def test_the_scorer_refuses_a_grid_that_is_not_the_registered_one():
    payload = _payload(FLAT_GAIN)
    payload["cells"] = payload["cells"][:-1]
    with pytest.raises(ValueError, match="pre-registered grid"):
        S.score(payload)


def test_the_analysis_path_does_not_import_the_engine():
    source = (ROOT / _body()["analysis"]["path"]).read_text(encoding="utf-8")
    assert "import organica" not in source and "from organica" not in source


def test_the_gate_default_arm_is_the_frozen_engine():
    import inspect
    from benchmarks.acquisition_harness import gate_acquisition_sufficiency
    default = inspect.signature(gate_acquisition_sufficiency).parameters["service_cls"].default
    assert default is None


def test_the_document_quotes_the_artifact_and_has_no_placeholders():
    body, flat = _body(), _flat()
    low, high = body["seeds"]["block"]
    for token in ("%d\u2013%d" % (low, high), str(body["seeds"]["bootstrap"]),
                  "%.2f" % body["criteria"]["bar"], "%.2f" % body["criteria"]["guard_bar"],
                  "95%", str(body["design"]["cells"])):
        assert token in flat, token
    for row in body["decision_table"]:
        assert row["verdict"] in flat, row["verdict"]
    assert "Every figure this block produces carries its arm" in flat
    assert not re.search(r"\{[a-z_]+\}", DOC.read_text(encoding="utf-8"))


def test_the_result_is_the_registered_grid_scored_by_the_frozen_path():
    body = _body()
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["prereg"] == body["prereg"]
    assert result["cells"] == body["design"]["cells"] == 16
    assert result["gates"]["all_passed"] is True
    assert result["decision"]["verdict"] in [r["verdict"] for r in body["decision_table"]]
    assert body["run"]["verdict"] == result["decision"]["verdict"]
    assert body["registered_status"].startswith("FROZEN, NOT RUN")


def test_the_recorded_run_agrees_with_the_result_artifact():
    body = _body()
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert body["run"]["adoption"] == result["criteria"]["adoption"]
    assert body["run"]["guard"] == result["criteria"]["guard"]
    assert body["run"]["per_seed"] == result["criteria"]["per_seed"]


def test_the_result_section_quotes_the_result_artifact():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    a, g = result["criteria"]["adoption"], result["criteria"]["guard"]
    flat = _flat()
    for token in ("%+.6f" % a["mean_paired_gain"],
                  "%+.6f" % a["interval"][0], "%+.6f" % a["interval"][1],
                  "%+.6f" % g["mean_paired_precision_difference"],
                  result["decision"]["verdict"]):
        assert token in flat, token
    assert "preserved exactly as committed before the run" in flat
    for seed in result["criteria"]["per_seed"]:
        assert seed in flat

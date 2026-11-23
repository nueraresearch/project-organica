"""Q006's pinned result must be the frozen block's result, not a typed summary."""
from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import copy
import json
import re
from pathlib import Path

from benchmarks import q006_admission_rederivation as Q

ROOT = Path(__file__).resolve().parents[1]


def test_the_record_is_exactly_the_frozen_block():
    record = json.loads(Q.ARTIFACT.read_text(encoding="utf-8"))
    assert Q.check() == []
    assert list(record["seeds"]) == Q.prereg()["design"]["seeds"]
    assert len(record["cells"]) == 16
    assert {cell["arm"] for cell in record["cells"]} == {"reference", "adopted"}
    assert record["decision"]["verdict"] == "NO GAIN ON THIS LAYER"
    assert record["survival"] == "SURVIVED"
    assert record["criteria"]["adoption"]["mean_paired_gain"] == -0.069197
    assert record["criteria"]["adoption"]["seeds_positive"] == 0
    assert record["gates"]["all_passed"] is True
    assert record["determinism"]["matched"] is True


def test_the_page_is_generated_from_the_record():
    record = json.loads(Q.ARTIFACT.read_text(encoding="utf-8"))
    assert Q.PAGE.read_text(encoding="utf-8") == Q.render(record)
    page = Q.PAGE.read_text(encoding="utf-8")
    assert "NO GAIN ON THIS LAYER" in page
    assert "SURVIVED" in page


def test_the_record_names_the_engine_it_was_measured_on_and_clean_boundary():
    record = json.loads(Q.ARTIFACT.read_text(encoding="utf-8"))
    # Q006 ran on 0.13.0; the promotion does not rewrite its historical result.
    assert record["engine_version"] == "0.13.0"
    assert record["engine_sha256"] == "ed0851d119470d2561900471f79f3302ea44184a278c0c622f49ae80e487c4c2"
    assert record["boundary"]["frozen_files_clean"] is True


def test_the_check_can_fail_on_a_changed_verdict():
    record = json.loads(Q.ARTIFACT.read_text(encoding="utf-8"))
    changed = copy.deepcopy(record)
    changed["decision"]["verdict"] = "ADOPTED ARM GAINS"
    assert Q.check(changed), "a changed verdict must be reported"


def test_the_fresh_seed_block_is_not_reused_elsewhere():
    frozen = Q.prereg()
    own = {
        Q.PREREG.resolve(),
        Q.ARTIFACT.resolve(),
        Q.PAGE.resolve(),
        (ROOT / "docs" / "Q006-ADMISSION-RE-DERIVATION-PREREGISTRATION.md").resolve(),
        (ROOT / "docs" / "stage_b_protocol.json").resolve(),
        (ROOT / "docs" / "STAGE-B-PROTOCOL.md").resolve(),
        (ROOT / "tests" / "test_q006_admission_rederivation.py").resolve(),
    }
    seeds = set(frozen["design"]["seeds"]) | {frozen["seeds"]["bootstrap"]}
    paths = []
    for directory in ("docs", "tests", "benchmarks", "research-journal", "papers"):
        base = ROOT / directory
        if base.exists():
            paths.extend(base.rglob("*.*"))
    for path in paths:
        if path.resolve() in own or path.suffix not in (".md", ".json", ".py", ".txt"):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        found = {int(m.group()) for m in re.finditer(r"\b2051010[1-9]\b", text)}
        assert not (seeds & found), (path, sorted(seeds & found))


def test_the_old_comparator_is_historical_not_the_new_reference():
    frozen = Q.prereg()
    assert frozen["comparator"]["verdict"] == "NO GAIN ON THIS LAYER"
    assert frozen["comparator"]["build"].startswith("unattributed")
    assert frozen["comparator"]["seeds"][0] == 20320101
    assert frozen["design"]["seeds"][0] == 20510101
    assert not set(frozen["comparator"]["seeds"]) & set(frozen["design"]["seeds"])

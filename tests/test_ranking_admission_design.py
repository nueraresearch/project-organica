"""The admission record must change admission and the budget floor, allocate nothing, and
license a different decision from each outcome.

The last test guards a neighbouring artifact: the bottleneck map claims exactly one specified
experiment, and a design record must not quietly become a second row there.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "ranking_admission_design.json"
DOC = ROOT / "docs" / "RANKING-ADMISSION-DESIGN.md"
MAP = ROOT / "docs" / "bottleneck_map.json"
RESULT = ROOT / "docs" / "rank_ordering_result.json"


def _body():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _flat():
    return " ".join(DOC.read_text(encoding="utf-8").split())


def test_the_change_is_admission_plus_a_budget_floor():
    change = _body()["the_change"]
    assert "count-ranked admission" in change["admission"]["from"]
    assert change["admission"]["to"].startswith("diversity-first admission over the source side")
    assert "count as the tie-break" in change["admission"]["to"]
    assert change["admission"]["scope"].startswith("which eligible candidate occupies")
    assert "already-admitted edges sharing a source" in change["admission"]["not_a_frequency_variant"]
    assert "the cap must be at least the number of eligible source tags" in change["budget"]["rule"]
    assert change["budget"]["floor"] == 16
    assert change["budget"]["increase"].startswith("none")
    unchanged = " ".join(change["unchanged"])
    assert "eligibility of rows" in unchanged
    assert "frozen engine" in unchanged


def test_the_budget_route_is_not_adopted_as_an_increase():
    budget = _body()["the_change"]["budget"]
    assert "twelve times the budget" in budget["why_not_an_increase"]
    assert "0.3438" in budget["why_not_an_increase"]
    flat = _flat()
    assert "a larger budget buys noise" in flat
    assert "the cap stays at the engine's own value" in flat


def test_the_cited_result_is_the_committed_one():
    cited = _body()["licensed_by"]
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    m1 = result["criteria"]["M1"]
    assert cited["verdict"] == result["decision"]["verdict"]
    assert cited["decision"] == result["decision"]["decision"]
    for token in ("%.4f" % m1["mean_delta_at_min_density"],
                  "[%.4f, %.4f]" % (m1["interval"][0], m1["interval"][1]),
                  "%.2f" % m1["bar"]):
        assert token in cited["criterion"], token
        assert token in _flat(), token


def test_each_outcome_licenses_a_different_decision():
    decisions = _body()["decisions"]
    assert "replaces count ranking in the next engine version" in decisions["adopt"]
    assert "may not be followed by another admission variant" in decisions["no_adopt"]
    assert "trade is priced" in decisions["trade"]
    assert len({decisions["adopt"], decisions["no_adopt"], decisions["trade"]}) == 3
    assert "run it again" in _body()["why_each_pole_is_a_different_decision"]
    assert "may not be followed by another admission variant" in _flat()


def test_the_dense_end_is_a_guard_that_voids_rather_than_a_second_criterion():
    claim = _body()["the_claim"]
    assert claim["primary"] == "the sparsest density at cap 20"
    assert "voids adoption" in claim["guard"]
    assert "not a second criterion" in claim["guard"]
    assert "guard that voids adoption, not a second criterion to score" in _flat()


def test_the_checks_can_fail_and_an_inert_arm_is_not_a_null():
    checks = " ".join(_body()["harness_checks"])
    assert "below 1.0, or the manipulation did not occur" in checks
    assert "void rather than a result" in checks
    assert "presence must be 1.0" in checks.lower()
    assert "an unrun experiment, not a null result" in _flat()
    assert "only active difference" in " ".join(_body()["falsifiers"])


def test_the_stop_condition_is_closed_and_the_record_may_not_grow():
    stop = _body()["stop_condition"]
    assert len(stop["stops_when"]) == 3
    assert "may not grow" in stop["no_growth"]
    scope = " ".join(stop["scope"])
    assert "16 tags" in scope and "cap 20 primary" in scope
    assert "No admission variant may be added to this record after the run" in _flat()


def test_the_record_allocates_nothing_and_consumes_no_seeds():
    allocation = _body()["allocation"]
    assert allocation["seeds"] == 0 and allocation["cells"] == 0
    assert allocation["thresholds"] == 0 and allocation["bars"] == 0
    assert not re.search(r"\b20\d{6}\b", ARTIFACT.read_text(encoding="utf-8"))


def test_the_document_quotes_the_artifact_and_has_no_placeholders():
    flat = _flat()
    assert "this record allocates nothing" in flat.lower()
    assert "Coverage is not behaviour" in flat
    assert not re.search(r"\{[a-z_]+\}", DOC.read_text(encoding="utf-8"))


def test_the_bottleneck_map_still_has_exactly_one_specified_experiment():
    body = json.loads(MAP.read_text(encoding="utf-8"))
    specified = [row for row in body["rows"] if row["study_specified"]]
    assert len(specified) == 1
    assert specified[0]["candidate"] == "Density interaction"

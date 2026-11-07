"""The ranking record must change ordering and nothing else, must allocate nothing, and
must license a decision from both outcomes.

The last test guards a neighbouring artifact: the bottleneck map claims exactly one
specified experiment, and a second design record must not quietly become a second row there.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "nonfrequency_ranking_design.json"
DOC = ROOT / "docs" / "NONFREQUENCY-RANKING-DESIGN.md"
MAP = ROOT / "docs" / "bottleneck_map.json"


def _body():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _flat():
    return " ".join(DOC.read_text(encoding="utf-8").split())


def test_the_treatment_changes_ordering_and_nothing_else():
    selection = _body()["selection"]
    assert selection["control"]["name"] == "global count-ranked top-k"
    assert selection["treatment"]["name"] == "diversity-first ordering"
    identical = " ".join(selection["identical_by_construction"])
    assert "eligibility: all rows stay eligible" in identical
    assert "cap, the scoring function and the admission window" in identical
    assert "the order in which eligible candidates fill the budget" in selection["only_ordering_differs"]
    assert "not which candidates are eligible" in selection["only_ordering_differs"]


def test_the_treatment_is_not_frequency_derived():
    selection = _body()["selection"]
    assert "already-selected outgoing edges" in selection["treatment"]["rule"]
    assert "tie-break only" in selection["tie_break"]
    assert "not the candidate's own frequency" in selection["why_not_frequency_derived"]
    flat = _flat()
    assert "frequency enters only as a tie-break" in flat
    assert "not a frequency-derived variant" in flat


def test_it_is_an_ordering_record_not_an_eligibility_record():
    distinction = _body()["distinction_from_density"]
    assert "varies eligibility" in distinction["density_record"]
    assert "ordering at the same eligibility" in distinction["this_record"]
    assert "neither subsumes the other" in distinction["relation"]
    flat = _flat()
    assert "varies **eligibility**" in flat
    assert "varies **ordering** at the same eligibility" in flat


def test_the_frequency_ceiling_is_not_called_a_universal_bound():
    caveat = _body()["ranking_bottleneck"]["ceiling_caveat"]
    assert "0.3438" in caveat
    assert "not an information-theoretic bound" in caveat
    assert "not an information-theoretic bound" in _flat()


def test_both_outcomes_license_a_different_architectural_decision():
    decision = _body()["architectural_decision"]
    assert "replaced by a diversity-based order" in decision["positive"]
    assert "candidate space" in decision["negative"]
    assert "not followed by another ordering variant" in decision["negative"]
    assert decision["positive"] != decision["negative"]
    assert "neither pole licenses a behavioural claim" in decision["neither"].lower()
    assert "coverage is not behavior" in _flat().lower()


def test_the_stop_condition_is_closed_and_the_record_may_not_grow():
    stop = _body()["stop_condition"]
    assert len(stop["stops_when"]) >= 2
    joined = " ".join(stop["stops_when"])
    assert "flat Delta" in joined
    assert "adoption bar" in joined
    assert "may not grow" in stop["no_growth"]
    scope = " ".join(stop["scope"])
    assert "16 tags" in scope and "caps 20 and 40" in scope
    assert "No ordering variant may be added to this record after the run" in _flat()


def test_a_harness_check_can_detect_an_inert_arm():
    checks = " ".join(_body()["harness_checks"])
    assert "selected sets must differ at the lowest density" in checks
    assert "must be 1.0" in checks
    assert "precision cannot exceed rho_rank" in checks
    flat = _flat()
    assert "unrun experiment, not a null result" in flat


def test_the_record_allocates_nothing_and_consumes_no_seeds():
    allocation = _body()["allocation"]
    assert allocation["seeds"] == 0 and allocation["cells"] == 0
    assert allocation["thresholds"] == 0 and allocation["bars"] == 0
    assert not re.search(r"\b20\d{6}\b", ARTIFACT.read_text(encoding="utf-8"))


def test_the_document_quotes_the_artifact_and_has_no_placeholders():
    flat = _flat()
    assert "At density 1 every candidate is a true edge" in flat
    raw = ARTIFACT.read_text(encoding="utf-8")
    for token in ("112", "320", "106", "109", "0.3438"):
        assert token in flat, token
        assert token in raw, token
    assert not re.search(r"\{[a-z_]+\}", DOC.read_text(encoding="utf-8"))


def test_the_bottleneck_map_still_has_exactly_one_specified_experiment():
    body = json.loads(MAP.read_text(encoding="utf-8"))
    specified = [row for row in body["rows"] if row["study_specified"]]
    assert len(specified) == 1
    assert specified[0]["candidate"] == "Density interaction"

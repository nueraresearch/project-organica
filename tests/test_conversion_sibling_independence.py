"""The sibling-independence clause must be present, and the check must be able to go red."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import conversion_sibling_independence as guard  # noqa: E402


def test_the_three_run_records_carry_a_dated_independence_clause():
    records = guard.load()

    assert guard.problems(records) == []
    for path in guard.RECORDS:
        clauses = [a for a in records[path]["amendments"]
                   if a.get("kind") == "sibling-independence"]
        assert len(clauses) == 1
        assert clauses[0]["date"] == guard.DATE


def test_the_check_fails_when_a_clause_is_removed():
    records = json.loads(json.dumps(guard.load()))
    path = next(iter(guard.RECORDS))
    records[path]["amendments"] = [a for a in records[path]["amendments"]
                                   if a.get("kind") != "sibling-independence"]

    assert guard.problems(records)


def test_the_check_fails_on_a_wrong_date():
    records = json.loads(json.dumps(guard.load()))
    path = next(iter(guard.RECORDS))
    for amendment in records[path]["amendments"]:
        if amendment.get("kind") == "sibling-independence":
            amendment["date"] = "2026-11-10"

    assert guard.problems(records)


def test_the_check_fails_when_a_record_copies_a_siblings_verdict():
    records = json.loads(json.dumps(guard.load()))
    paths = list(guard.RECORDS)
    records[paths[0]]["result"]["verdict"] = records[paths[1]]["result"]["verdict"]

    assert guard.problems(records)


def test_the_check_fails_when_a_record_lists_a_siblings_artifact_as_evidence():
    records = json.loads(json.dumps(guard.load()))
    path, sibling = list(guard.RECORDS)[:2]
    sibling_artifact = records[sibling]["result"]["artifact"]
    records[path]["result"]["evidence"] = [sibling_artifact]

    found = guard.problems(records)
    assert any("lists sibling" in problem for problem in found), found


def test_the_check_fails_when_a_siblings_artifact_hides_in_a_prior_entry():
    records = json.loads(json.dumps(guard.load()))
    path, sibling = list(guard.RECORDS)[:2]
    sibling_artifact = records[sibling]["result"]["artifact"]
    records[path]["prior"].append({"artifact": sibling_artifact, "claim": "borrowed"})

    found = guard.problems(records)
    assert any("lists sibling" in problem for problem in found), found

"""The change-to-failure map must cover the engine and be able to fail."""
LAYER = "dry-run"  # benchmarks/test_layers.py: the module's execution layer

import copy

from benchmarks import change_map as cm


def test_the_map_validates():
    data = cm.load()
    report = cm.validate(data)
    assert report["passed"], report["errors"]


def test_the_document_matches_a_fresh_render():
    data = cm.load()
    report = cm.validate(data)
    assert cm.DOC.exists()
    assert cm.DOC.read_text(encoding="utf-8") == cm.render(data, report)


def test_every_post_freeze_commit_is_claimed_exactly_once():
    data = cm.load()
    claimed = [commit for row in data["changes"] for commit in row["commits"]]
    assert len(claimed) == len(set(claimed)), "a commit is claimed by more than one row"
    assert sorted(claimed) == cm.commits_since_freeze(), "the map and git disagree on the commits"


def test_an_unclaimed_commit_is_rejected():
    data = copy.deepcopy(cm.load())
    data["changes"] = [row for row in data["changes"] if row["id"] != "M05"]
    report = cm.validate(data)
    assert not report["passed"]
    assert any("no row" in message for message in report["errors"]), report["errors"]


def test_a_row_with_the_same_two_decisions_is_rejected():
    data = copy.deepcopy(cm.load())
    row = next(r for r in data["changes"] if r["status"] == "stays")
    row["decision_if_negative"] = row["decision_if_positive"]
    report = cm.validate(data)
    assert any(row["id"] in message and "same" in message for message in report["errors"]), report[
        "errors"
    ]


def test_a_stays_row_without_a_mechanism_is_rejected():
    data = copy.deepcopy(cm.load())
    row = next(r for r in data["changes"] if r["status"] == "stays")
    row["mechanism"] = "it changed something"
    report = cm.validate(data)
    assert any(row["id"] in message and "mechanism" in message for message in report["errors"]), report[
        "errors"
    ]


def test_a_stays_row_naming_no_failure_is_rejected():
    data = copy.deepcopy(cm.load())
    row = next(r for r in data["changes"] if r["status"] == "stays")
    row["failure"] = {"kind": "none", "artifact": None, "note": "nothing to move"}
    report = cm.validate(data)
    assert any(row["id"] in message and "no failure" in message for message in report["errors"]), report[
        "errors"
    ]


def test_an_excluded_row_without_a_reason_is_rejected():
    data = copy.deepcopy(cm.load())
    row = next(r for r in data["changes"] if r["status"] == "excluded")
    row["reason"] = ""
    report = cm.validate(data)
    assert any(row["id"] in message and "reason" in message for message in report["errors"]), report[
        "errors"
    ]


def test_a_missing_failure_artifact_is_rejected():
    data = copy.deepcopy(cm.load())
    row = next(r for r in data["changes"] if r["failure"].get("artifact"))
    row["failure"]["artifact"] = "docs/does-not-exist.json"
    report = cm.validate(data)
    assert any(row["id"] in message and "does not exist" in message for message in report["errors"]), (
        report["errors"]
    )


def test_check_writes_nothing():
    map_before = cm.MAP.read_bytes()
    doc_before = cm.DOC.read_bytes()
    assert cm.main(["--check"]) == 0
    assert cm.MAP.read_bytes() == map_before
    assert cm.DOC.read_bytes() == doc_before

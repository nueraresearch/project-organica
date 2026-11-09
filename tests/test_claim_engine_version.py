"""A claim must name the build its evidence came from, or say plainly that it cannot.

The value is derived from the artifacts rather than typed, so the gate fails on drift in either
direction: a claim naming a build its evidence does not carry, and a load-bearing claim naming
none. Every branch is proved to fire on input built to break it, and proved not to fire on input
built to satisfy it — a guard that cannot fail is decoration (AGENTS.md rule 25(c)).
"""

import json
from pathlib import Path

from benchmarks import provenance as prov
from benchmarks import research_accountability as ra

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "docs" / "claim_ledger.json"

STAMPED = {"engine_version": "0.13.0", "engine_commit": "a" * 40}


def _root(tmp_path, stamped=True):
    """A tree with one JSON result and one prose document."""
    (tmp_path / "docs").mkdir()
    record = dict(STAMPED) if stamped else {"result": 1}
    (tmp_path / "docs" / "result.json").write_text(json.dumps(record), encoding="utf-8")
    (tmp_path / "docs" / "note.md").write_text("prose about a result\n", encoding="utf-8")
    return tmp_path


def _claim(**over):
    claim = {
        "claim_id": "C900",
        "classification": "HYPOTHESIS",
        "status": "ACTIVE",
        "provenance": prov.OWNER_READING,
        "supporting_evidence": ["docs/result.json"],
        "engine_version": "0.13.0",
    }
    claim.update(over)
    return claim


def _codes(claim, root):
    return [f["code"] for f in prov.check_engine_attribution({"claims": [claim]}, root)]


def test_a_stamped_claim_that_records_its_build_passes(tmp_path):
    root = _root(tmp_path)
    assert prov.derived_engine_version(_claim(), root) == "0.13.0"
    assert _codes(_claim(), root) == []


def test_the_published_ledger_states_the_build_for_every_claim():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    for claim in ledger["claims"]:
        assert prov.ENGINE_FIELD in claim, claim["claim_id"]
        assert str(claim[prov.ENGINE_FIELD]) == prov.derived_engine_version(claim, ROOT), (
            "%s records %r but its evidence yields %r"
            % (claim["claim_id"], claim[prov.ENGINE_FIELD],
               prov.derived_engine_version(claim, ROOT))
        )
    assert prov.check_engine_attribution(ledger, ROOT) == []


def test_the_current_ledger_names_no_build_and_records_that_rather_than_hiding_it():
    """The debt is disclosed, not absent: four claims cite unstamped artifacts, seven cite prose."""
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    derived = [prov.derived_engine_version(c, ROOT) for c in ledger["claims"]]
    assert derived.count(prov.UNATTRIBUTED) == 4, derived
    assert derived.count(prov.DOCUMENT_ONLY) == 7, derived
    assert not [d for d in derived if d not in (prov.UNATTRIBUTED, prov.DOCUMENT_ONLY)], derived
    assert [c["claim_id"] for c, d in zip(ledger["claims"], derived) if d == prov.UNATTRIBUTED] == [
        "C003", "C004", "C005", "C010"
    ]


def test_a_claim_without_the_field_is_refused(tmp_path):
    root = _root(tmp_path)
    claim = _claim()
    del claim[prov.ENGINE_FIELD]
    assert _codes(claim, root) == ["claim-engine-version-missing"]


def test_a_hand_typed_version_the_artifact_does_not_carry_is_refused(tmp_path):
    root = _root(tmp_path, stamped=False)
    claim = _claim(engine_version="0.13.0")
    assert prov.derived_engine_version(claim, root) == prov.UNATTRIBUTED
    assert _codes(claim, root) == ["claim-engine-version-stale"]


def test_an_artifact_gaining_a_stamp_makes_the_ledger_stale(tmp_path):
    """The direction that matters in practice: the record moves, the ledger does not."""
    root = _root(tmp_path)
    claim = _claim(engine_version=prov.UNATTRIBUTED)
    assert _codes(claim, root) == ["claim-engine-version-stale"]


def test_an_unattributed_hypothesis_is_counted_and_not_failed(tmp_path):
    root = _root(tmp_path, stamped=False)
    claim = _claim(engine_version=prov.UNATTRIBUTED)
    assert _codes(claim, root) == []
    assert prov.derived_engine_version(claim, root) == prov.UNATTRIBUTED


def test_a_load_bearing_claim_on_an_unstamped_artifact_is_refused(tmp_path):
    root = _root(tmp_path, stamped=False)
    claim = _claim(classification="SUPPORTED", engine_version=prov.UNATTRIBUTED)
    assert _codes(claim, root) == ["claim-load-bearing-unattributed"]
    claim["classification"] = "HYPOTHESIS"
    assert _codes(claim, root) == [], "the rule must depend on the classification, not the field"


def test_a_load_bearing_claim_on_a_document_is_refused(tmp_path):
    root = _root(tmp_path)
    claim = _claim(classification="DEMONSTRATED", supporting_evidence=["docs/note.md"],
                   engine_version=prov.DOCUMENT_ONLY)
    assert prov.derived_engine_version(claim, root) == prov.DOCUMENT_ONLY
    assert _codes(claim, root) == ["claim-load-bearing-unattributed"]


def test_a_withdrawn_supported_claim_is_not_gated_the_same_way(tmp_path):
    """A withdrawn claim is history; the rule protects what a reader is asked to accept now."""
    root = _root(tmp_path, stamped=False)
    claim = _claim(classification="SUPPORTED", status="WITHDRAWN",
                   engine_version=prov.UNATTRIBUTED)
    assert _codes(claim, root) == []


def test_disagreeing_artifacts_are_reported_as_mixed(tmp_path):
    root = _root(tmp_path)
    (root / "docs" / "other.json").write_text(
        json.dumps({"engine_version": "0.12.0", "engine_commit": "b" * 40}), encoding="utf-8")
    claim = _claim(supporting_evidence=["docs/result.json", "docs/other.json"])
    assert prov.derived_engine_version(claim, root) == "mixed:0.12.0+0.13.0"
    assert _codes(claim, root) == ["claim-engine-version-stale"]
    claim[prov.ENGINE_FIELD] = "mixed:0.12.0+0.13.0"
    assert _codes(claim, root) == []


def test_the_validator_carries_the_gate_into_the_ledger_report(tmp_path):
    """`validate` is what the suite and `--check` run; the gate has to reach it."""
    reg, ledger = ra.load_pair()
    ledger = json.loads(json.dumps(ledger))
    claim = next(c for c in ledger["claims"] if c["claim_id"] == "C001")
    claim["classification"] = "SUPPORTED"
    claim["status"] = "ACTIVE"
    report = ra.validate(reg, ledger)
    assert not report["passed"]
    assert any(
        "claim-load-bearing-unattributed" in e and "C001" in e for e in report["errors"]
    ), report["errors"]


def test_the_dashboard_counts_are_computed_from_the_claims():
    reg, ledger = ra.load_pair()
    metrics = dict((name, value) for name, value, _d, _s in ra.metrics(reg, ledger))
    derived = [prov.derived_engine_version(c, ROOT) for c in ledger["claims"]]
    assert metrics["Claims naming an engine build"] == sum(
        1 for d in derived if d not in (prov.UNATTRIBUTED, prov.DOCUMENT_ONLY))
    assert metrics["Claims whose evidence names no build"] == derived.count(prov.UNATTRIBUTED)
    assert metrics["Claims citing a document instead of a result"] == derived.count(
        prov.DOCUMENT_ONLY)
    assert (metrics["Claims naming an engine build"]
            + metrics["Claims whose evidence names no build"]
            + metrics["Claims citing a document instead of a result"]) == len(ledger["claims"])

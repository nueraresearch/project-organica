"""The governance operations checks must pass on the committed records and fail on the defects
they exist to catch. Every test here is static: no engine cell runs and nothing is written.
"""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import copy
import json
from datetime import date

from benchmarks import governance_ops as go


def _ops():
    return copy.deepcopy(go.ops())


def test_the_committed_governance_record_is_clean():
    assert go.all_findings() == []
    assert go.main(["--check"]) == 0


def test_preregistration_paths_resolve_bare_names_and_ids():
    assert go.resolve_prereg("DECAY-ATTRIBUTION-PREREGISTRATION.md") == (
        "docs/DECAY-ATTRIBUTION-PREREGISTRATION.md")
    assert go.resolve_prereg("C6-TIMING-1") == "docs/c6_timing_prereg.json"
    assert go.resolve_prereg("PRESENCE-CONVERSION-2") == "docs/presence_conversion_repair_prereg.json"
    assert go.resolve_prereg("no-such-preregistration") is None


def test_dependency_baseline_covers_claims_decisions_and_constraints():
    paths = go.dependency_paths()
    assert "claim:C003" in paths
    assert "decision:DECISION-V2-SCOPE" in paths
    assert "constraint:K2 - belief revision reversed" in paths
    assert "prereg:C6-TIMING-1" in paths
    assert "prereg:PRESENCE-CONVERSION-2" in paths
    assert "docs/USER-MANUAL.md" not in paths["decision:DECISION-V2-RUNTIME-FAILURE"]


def test_a_changed_dependency_is_marked_needs_review():
    doc = _ops()
    key = "claim:C003"
    path = next(iter(doc["dependency_baseline"]["records"][key]))
    doc["dependency_baseline"]["records"][key][path] = "0" * 64
    findings = go.dependency_findings(doc)
    assert any(item["code"] == "needs-review" and item["subject"] == key for item in findings), findings


def test_a_missing_dependency_baseline_is_not_silently_accepted():
    doc = _ops()
    doc["dependency_baseline"] = {}
    assert go.dependency_findings(doc)[0]["code"] == "unbaselined"


def test_a_missing_dependency_artifact_is_reported(monkeypatch):
    doc = _ops()
    monkeypatch.setattr(go, "dependency_paths", lambda: {"claim:C003": ["docs/no-such-artifact.json"]})
    doc["dependency_baseline"]["records"]["claim:C003"] = {"docs/no-such-artifact.json": "0" * 64}
    findings = go.dependency_findings(doc)
    assert any(item["code"] == "missing" for item in findings), findings


def test_writing_the_baseline_is_a_derived_record_not_a_run(tmp_path):
    out = tmp_path / "ops.json"
    count = go.write_dependency_baseline(out)
    written = json.loads(out.read_text(encoding="utf-8"))
    assert count == len(written["dependency_baseline"]["records"])
    assert written["dependency_baseline"]["engine_sha256"]


def test_decision_classes_distinguish_governance_from_experiment_backed():
    governance = {"decision_id": "DECISION-V2-RUNTIME-FAILURE", "evidence": ["docs/x.json"]}
    experiment = {"decision_id": "DECISION-EXPERIMENT", "evidence": ["docs/result.json"]}
    prereg = {"decision_id": "DECISION-PREREG", "evidence": ["docs/PREREGISTRATION.md"]}
    assert go.decision_class(governance) == "governance"
    assert go.decision_class(experiment) == "experiment-backed"
    assert go.decision_class(prereg) == "preregistration"


def test_an_experiment_decision_without_a_result_is_not_in_force(monkeypatch):
    fake = {
        "decision_id": "DECISION-FAKE",
        "status": "ADOPTED",
        "evidence": ["docs/NO-SUCH-RESULT.json"],
        "status_quote": "adopted",
        "chosen": ["do it"],
    }
    monkeypatch.setattr(go.dg, "load", lambda: {"decisions": [fake]})
    findings = go.decision_findings(_ops())
    assert any(item["code"] == "implementation-missing" for item in findings), findings


def test_a_governance_decision_without_its_record_is_reported(monkeypatch):
    fake = {
        "decision_id": "DECISION-GHOST",
        "status": "ADOPTED",
        "evidence": ["README.md"],
        "status_quote": "adopted",
        "chosen": ["do it"],
    }
    monkeypatch.setattr(go.dg, "load", lambda: {"decisions": [fake]})
    findings = go.decision_findings(_ops())
    assert any(item["code"] == "implementation-missing" for item in findings), findings


def test_an_expired_waiver_fails_closed():
    doc = _ops()
    doc["waivers"] = [{"id": "W-1", "scope": "seed reuse", "owner": "owner",
                       "reason": "one diagnostic", "expires": "2000-01-01",
                       "records": ["docs/governance_ops.json"]}]
    findings = go.waiver_findings(doc, date(2026, 11, 17))
    assert any(item["code"] == "waiver-expired" for item in findings), findings


def test_a_current_waiver_with_existing_records_is_accepted():
    doc = _ops()
    doc["waivers"] = [{"id": "W-1", "scope": "seed reuse", "owner": "owner",
                       "reason": "one diagnostic", "expires": "2027-01-01",
                       "records": ["docs/governance_ops.json"]}]
    assert go.waiver_findings(doc, date(2026, 11, 17)) == []


def test_public_citations_of_withdrawn_or_unknown_claims_are_rejected(tmp_path, monkeypatch):
    public = tmp_path / "paper.md"
    public.write_text("We rely on C005 and C999.\n", encoding="utf-8")
    monkeypatch.setattr(go, "public_documents", lambda _doc=None: [public])
    findings = go.claim_usage_findings(_ops())
    assert any(item["code"] == "inactive-claim" and item["subject"] == "C005" for item in findings)
    assert any(item["code"] == "unknown-claim" and item["subject"] == "C999" for item in findings)


def test_claim_usage_index_is_read_from_public_documents(tmp_path, monkeypatch):
    public = tmp_path / "paper.md"
    public.write_text("We rely on C003.\n", encoding="utf-8")
    monkeypatch.setattr(go, "public_documents", lambda _doc=None: [public])
    usage = go.claim_usage(_ops())
    assert usage["C003"] == [go._rel(public)]


def test_the_lottery_is_deterministic_and_walks_the_claim_chain():
    first = go.lottery(date(2026, 11, 17), count=3)
    second = go.lottery(date(2026, 11, 17), count=3)
    assert first == second
    assert len(first["sampled"]) == 3
    assert first["findings"] == []


def test_the_canaries_fire():
    assert go.canary_problems() == []


def test_a_broken_claim_chain_is_reported():
    reg = {"questions": [{"id": "Q999", "preregistrations": ["docs/no-such.json"], "decisions": []}]}
    claim = {"claim_id": "C999", "supporting_questions": ["Q999"], "supporting_evidence": []}
    findings = go.claim_chain(claim, reg)
    assert any(item["code"] == "broken-chain" for item in findings), findings


def test_the_run_ledger_exposes_seed_status_and_run_status():
    ledger = go.run_ledger(_ops())
    assert any(block["status"] == "spent" for block in ledger["seeds"])
    assert any(block["status"] == "held" for block in ledger["seeds"])
    assert any(run["status"] == "VOID" for run in ledger["runs"])
    assert go.run_ledger_findings(_ops()) == []


def test_a_seed_collision_is_reported(monkeypatch):
    monkeypatch.setattr(go.a1_seed_reservations, "reservations", lambda: [
        {"label": "a", "owner": "x", "seeds": [1], "spent": False},
        {"label": "b", "owner": "y", "seeds": [1], "spent": False},
    ])
    findings = go.run_ledger_findings(_ops())
    assert findings and findings[0]["code"] == "seed-collision"


def test_the_portfolio_respects_the_wip_limit():
    doc = _ops()
    doc["policy"]["portfolio"]["max_open_questions"] = 1
    findings = go.portfolio_findings(doc, date(2026, 11, 17))
    assert any(item["code"] == "wip-exceeded" for item in findings), findings


def test_an_overdue_portfolio_review_is_reported():
    doc = _ops()
    doc["reviews"]["questions"]["Q001"] = {"review_by": "2000-01-01"}
    findings = go.portfolio_findings(doc, date(2026, 11, 17))
    assert any(item["code"] == "review-overdue" and item["subject"] == "Q001" for item in findings)


def test_decision_classes_can_be_summarized():
    counts = go.class_counts(_ops())
    assert sum(counts.values()) == 37
    assert counts["governance"] >= 1


def test_an_event_can_be_appended_without_rewriting_history(tmp_path):
    path = tmp_path / "ops.json"
    path.write_text(json.dumps(_ops()), encoding="utf-8")
    before = list(go.ops()["events"])
    event = {"id": "EVT-0002", "date": "2026-11-17", "actor": "owner",
             "record": "C003", "from": "ACTIVE", "to": "SUPERSEDED",
             "reason": "test", "artifacts": []}
    go.append_event(event, path)
    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["events"][:len(before)] == before
    assert written["events"][-1] == event


def test_the_event_stream_is_ordered_and_append_only():
    doc = _ops()
    doc["events"] = [
        {"id": "E1", "date": "2026-11-17", "actor": "a", "record": "r",
         "from": "x", "to": "y", "reason": "r", "artifacts": []},
        {"id": "E2", "date": "2026-11-16", "actor": "a", "record": "r",
         "from": "y", "to": "z", "reason": "r", "artifacts": []},
    ]
    findings = go.event_findings(doc)
    assert any(item["code"] == "event-order" for item in findings), findings
    doc["events"][1]["date"] = "2026-11-18"
    doc["events"].append(copy.deepcopy(doc["events"][0]))
    findings = go.event_findings(doc)
    assert any(item["code"] == "duplicate-event" for item in findings), findings


def test_preflight_reports_the_exact_failed_obligation(monkeypatch):
    monkeypatch.setattr(go, "_suite_check", lambda: (True, "ok"))
    monkeypatch.setattr(go, "_prereg_check", lambda: (True, "ok"))
    monkeypatch.setattr(go, "_grant_check", lambda: (True, "ok"))
    monkeypatch.setattr(go.rt, "main", lambda argv: 0)
    monkeypatch.setattr(go.dg, "main", lambda argv: 0)
    monkeypatch.setattr(go.engine_pin, "main", lambda argv: 0)
    monkeypatch.setattr(go.a1_seed_reservations, "main", lambda argv: 0)
    checks = go.preflight("run", suite=True, ops_doc=_ops())
    assert all(check["ok"] for check in checks), checks

    monkeypatch.setattr(go, "_prereg_check", lambda: (False, "missing docs/PREREG.md"))
    checks = go.preflight("run", suite=True, ops_doc=_ops())
    failed = [check for check in checks if not check["ok"]]
    assert failed and failed[0]["name"] == "preregistrations"
    assert "missing docs/PREREG.md" in failed[0]["detail"]


def test_publish_preflight_adds_claim_and_decision_checks(monkeypatch):
    monkeypatch.setattr(go, "_suite_check", lambda: (True, "ok"))
    monkeypatch.setattr(go, "_prereg_check", lambda: (True, "ok"))
    monkeypatch.setattr(go, "_grant_check", lambda: (True, "ok"))
    monkeypatch.setattr(go.rt, "main", lambda argv: 0)
    monkeypatch.setattr(go.dg, "main", lambda argv: 0)
    monkeypatch.setattr(go.engine_pin, "main", lambda argv: 0)
    monkeypatch.setattr(go.a1_seed_reservations, "main", lambda argv: 0)
    checks = go.preflight("publish", suite=True, ops_doc=_ops())
    names = {check["name"] for check in checks}
    assert {"claim-usage", "decision-in-force", "waivers"} <= names
    assert all(check["ok"] for check in checks), checks

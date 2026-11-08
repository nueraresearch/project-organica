"""The accountability layers must agree with each other and with their records."""

import json
import re

import pytest

from benchmarks import research_accountability as ra


@pytest.fixture(scope="module")
def records():
    reg, ledger = ra.load_pair()
    return reg, ledger


def test_the_ledger_and_the_registry_validate_together(records):
    reg, ledger = records
    report = ra.validate(reg, ledger)
    assert report["passed"], report["errors"]


def test_every_public_document_matches_what_the_records_generate(records):
    reg, ledger = records
    documents = ra.build(reg, ledger)
    assert len(documents) == 3
    for path, expected in documents.items():
        assert path.exists(), "not generated: %s" % path
        assert path.read_text(encoding="utf-8") == expected, (
            "%s is stale; rebuild with python -m benchmarks.research_accountability" % path
        )


def test_every_public_finding_cites_a_question_that_exists(records):
    reg, ledger = records
    known = {q["id"] for q in reg["questions"]}
    findings = ra.render_findings(reg, ledger)
    cited = set(re.findall(r"\b(Q\d{3})\b", findings))
    assert cited, "the findings page cites no question at all"
    assert cited <= known, "findings cite unknown questions: %r" % sorted(cited - known)


def test_a_withdrawn_interpretation_never_appears_as_current(records):
    reg, ledger = records
    findings = ra.render_findings(reg, ledger)
    sections = re.split(r"^## ", findings, flags=re.MULTILINE)
    current = "\n".join(s for s in sections if not s.startswith("Withdrawn"))
    withdrawn = [c["claim_id"] for c in ledger["claims"] if c["status"] != "ACTIVE"]
    withdrawn += [q["id"] for q in reg["questions"] if q.get("outcome") == "WITHDRAWN"]
    assert withdrawn, "no withdrawn record exists, so this check cannot fire"
    for identifier in withdrawn:
        assert identifier not in current, "%s is shown as current" % identifier


def test_the_dashboard_reports_the_counts_the_records_contain(records):
    reg, ledger = records
    dashboard = ra.render_dashboard(reg, ledger)
    for name, value, _definition, _source in ra.metrics(reg, ledger):
        row = [line for line in dashboard.splitlines() if line.startswith("| %s |" % name)]
        assert len(row) == 1, "metric row missing or duplicated: %s" % name
        assert row[0].split("|")[2].strip() == str(value)


def test_a_load_bearing_claim_on_an_unsupported_question_is_rejected(records):
    reg, ledger = records
    ledger = json.loads(json.dumps(ledger))
    claim = next(c for c in ledger["claims"] if c["claim_id"] == "C001")
    # Build the precondition instead of relying on today's ledger: the rule applies to a
    # load-bearing claim, and it must fire when the question it cites is not closed+SUPPORTED.
    claim["classification"] = "DEMONSTRATED"
    claim["supporting_questions"] = ["Q003"]  # not closed+SUPPORTED on the current record
    report = ra.validate(reg, ledger)
    assert not report["passed"]
    assert any("C001" in e and "Q003" in e for e in report["errors"]), report["errors"]


def test_a_withdrawn_claim_without_a_reason_is_rejected(records):
    reg, ledger = records
    ledger = json.loads(json.dumps(ledger))
    claim = next(c for c in ledger["claims"] if c["status"] == "WITHDRAWN")
    claim["withdrawn_reason"] = ""
    claim["superseded_by"] = None
    report = ra.validate(reg, ledger)
    assert any(claim["claim_id"] in e and "withdrawn" in e for e in report["errors"]), report["errors"]


def test_an_active_claim_carrying_a_withdrawal_reason_is_rejected(records):
    reg, ledger = records
    ledger = json.loads(json.dumps(ledger))
    claim = next(c for c in ledger["claims"] if c["status"] == "ACTIVE")
    claim["withdrawn_reason"] = "quietly softened"
    report = ra.validate(reg, ledger)
    assert any(claim["claim_id"] in e for e in report["errors"]), report["errors"]


def test_a_claim_citing_a_question_that_does_not_exist_is_rejected(records):
    reg, ledger = records
    ledger = json.loads(json.dumps(ledger))
    ledger["claims"][0]["supporting_questions"] = ["Q999"]
    report = ra.validate(reg, ledger)
    assert any("Q999" in e for e in report["errors"]), report["errors"]


def test_an_active_hypothesis_that_cites_nothing_is_rejected(records):
    reg, ledger = records
    ledger = json.loads(json.dumps(ledger))
    claim = next(
        c for c in ledger["claims"] if c["classification"] == "HYPOTHESIS" and c["status"] == "ACTIVE"
    )
    claim["supporting_questions"] = []
    claim["contradicting_questions"] = []
    report = ra.validate(reg, ledger)
    assert any(claim["claim_id"] in e for e in report["errors"]), report["errors"]


def test_the_check_mode_writes_nothing():
    paths = (ra.LEDGER_DOC, ra.DASHBOARD_DOC, ra.FINDINGS_DOC)
    before = {p: p.read_bytes() for p in paths}
    assert ra.main(["--check"]) == 0
    after = {p: p.read_bytes() for p in paths}
    assert before == after


def test_the_check_mode_fails_when_a_generated_page_is_stale(tmp_path, monkeypatch):
    stale = tmp_path / "RESEARCH-FINDINGS.md"
    stale.write_text("an out-of-date page\n", encoding="utf-8")
    monkeypatch.setattr(ra, "FINDINGS_DOC", stale)
    assert ra.main(["--check"]) == 1
    assert stale.read_text(encoding="utf-8") == "an out-of-date page\n", (
        "--check must report a stale page, never repair it"
    )


def test_the_check_mode_fails_when_the_registry_page_is_stale(tmp_path, monkeypatch):
    from benchmarks import research_registry as rr

    stale = tmp_path / "RESEARCH-QUESTION-REGISTRY.md"
    stale.write_text("an out-of-date render\n", encoding="utf-8")
    monkeypatch.setattr(rr, "DOC", stale)
    assert ra.main(["--check"]) == 1

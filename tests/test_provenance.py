"""The provenance tag is a claim about what a status rests on, so it is checked, not described.

Every rule is proved to fire on input built to break it, and proved not to fire on a row built to
satisfy it — a guard that cannot fail is decoration, which is the failure `AGENTS.md` rule 25(c)
names. The committed map is checked in `tests/test_bottleneck_map.py`; this file checks the
validator.
"""

import copy
import json
from pathlib import Path

import pytest

from benchmarks import provenance as prov

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "bottleneck_map.json"
LEDGER = ROOT / "docs" / "claim_ledger.json"
DECISIONS = ROOT / "docs" / "decisions.json"

CITING = "docs/bottleneck_map.json"
REGISTRATION = "docs/DENSITY-INTERACTION-A2-PREREGISTRATION.md"


def _row(**overrides):
    row = {
        "candidate": "A row",
        "status": ["Not established / not measured"],
        "check": "no figure is quoted here",
        "evidence": [CITING],
        "provenance": prov.ARTIFACT_READ,
    }
    row.update(overrides)
    return row


def _map(*rows):
    return {"rows": list(rows)}


def _codes(body, root=None):
    return [finding["code"] for finding in prov.check_map(body, root)]


def test_the_vocabulary_is_closed_and_each_tag_says_what_it_claims():
    assert prov.TAGS == (prov.ARTIFACT_READ, prov.OWNER_READING, prov.AGENT_INFERRED,
                         prov.PROTOCOL_CONSTRAINT)
    assert set(prov.MEANINGS) == set(prov.TAGS)
    assert prov.CITING_TAGS == (prov.ARTIFACT_READ, prov.OWNER_READING)


def test_each_tag_is_reachable_and_a_satisfied_row_produces_no_finding():
    for tag in prov.TAGS:
        evidence = [REGISTRATION] if tag == prov.PROTOCOL_CONSTRAINT else [CITING]
        body = _map(_row(provenance=tag, evidence=evidence))
        assert prov.check_map(body, ROOT) == [], tag


def test_an_unknown_tag_is_refused_rather_than_read_as_a_reading():
    assert _codes(_map(_row(provenance="PROBABLY_FINE"))) == ["tag-unknown"]


def test_a_missing_tag_is_refused_rather_than_defaulted():
    row = _row()
    del row["provenance"]
    assert _codes(_map(row)) == ["tag-missing"]
    with pytest.raises(ValueError):
        prov.counts(_map(row))


def test_the_old_boolean_is_refused_beside_a_tag():
    codes = _codes(_map(_row(read_for_this_record=True)))
    assert codes == ["stale-flag"]


def test_a_citing_tag_with_nothing_named_is_refused():
    for tag in prov.CITING_TAGS:
        assert _codes(_map(_row(provenance=tag, evidence=[]))) == ["unbacked-tag"], tag
    # An inference claims no reading, so it needs no citation.
    assert _codes(_map(_row(provenance=prov.AGENT_INFERRED, evidence=[]))) == []


def test_a_named_record_that_is_not_on_disk_is_refused():
    body = _map(_row(evidence=["docs/NOT-A-RECORD.md"]))
    assert _codes(body, ROOT) == ["missing-evidence"]
    assert _codes(body) == [], "path existence is only checked when a root is supplied"


def test_a_reading_that_quotes_a_figure_is_a_transcription_and_is_refused():
    quoted = {"check": "precision tops out at 0.3438 across 36 measurements"}
    for tag in (prov.OWNER_READING, prov.AGENT_INFERRED):
        assert _codes(_map(_row(provenance=tag, **quoted))) == ["figure-without-reading"], tag
    # The same sentence under ARTIFACT_READ is a claimed reading, which is the honest tag for it.
    assert _codes(_map(_row(provenance=prov.ARTIFACT_READ, **quoted))) == []


def test_an_agent_inference_may_not_carry_a_supported_status():
    supported = {"status": ["Supported within the tested scope"]}
    assert _codes(_map(_row(provenance=prov.AGENT_INFERRED, **supported))) == ["inference-supports"]
    # A reading or a checked row may support a status; only an inference may not.
    for tag in prov.CITING_TAGS:
        assert _codes(_map(_row(provenance=tag, **supported))) == [], tag


def test_the_module_names_all_three_tags_in_its_documentation():
    doc = prov.__doc__ or ""
    for tag in prov.TAGS:
        assert tag in doc, tag


def test_counts_are_derived_from_the_rows():
    body = _map(_row(provenance=prov.ARTIFACT_READ),
                _row(candidate="B", provenance=prov.OWNER_READING),
                _row(candidate="C", provenance=prov.OWNER_READING))
    assert prov.counts(body) == {prov.ARTIFACT_READ: 1, prov.OWNER_READING: 2,
                                 prov.AGENT_INFERRED: 0, prov.PROTOCOL_CONSTRAINT: 0}


def test_counts_refuse_an_untagged_row_instead_of_absorbing_it():
    row = _row()
    del row["provenance"]
    with pytest.raises(ValueError):
        prov.counts(_map(row))


def test_the_summary_is_generated_and_names_the_rows_whose_tag_is_not_a_reading():
    """The table carries every row's tag; the paragraph names the rows that are not read.

    Naming all seven checked rows in prose would be noise beside a column that already holds
    each tag, so the paragraph names the non-reading ones and counts the rest.
    """
    body = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    summary = prov.render_summary(body)
    per_tag = prov.counts(body)
    assert "{" not in summary and "}" not in summary, "a placeholder would be a silent number"
    assert str(len(body["rows"])) in summary
    for tag in prov.TAGS:
        if not per_tag[tag]:
            continue
        assert "`%s`" % tag in summary
        if tag == prov.ARTIFACT_READ:
            assert "%d of %d rows" % (per_tag[tag], len(body["rows"])) in summary
            continue
        for row in body["rows"]:
            if row["provenance"] == tag:
                assert row["candidate"] in summary, row["candidate"]


def test_the_summary_changes_when_a_row_is_retagged():
    body = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    before = prov.render_summary(body)
    moved = copy.deepcopy(body)
    moved["rows"][0]["provenance"] = prov.OWNER_READING
    moved["rows"][0]["check"] = moved["rows"][0]["check"].replace("112", "many")
    after = prov.render_summary(moved)
    assert after != before, "the count is derived, so a retag must move the paragraph"
    assert prov.counts(moved)[prov.OWNER_READING] == prov.counts(body)[prov.OWNER_READING] + 1


def test_a_protocol_constraint_must_name_a_registration():
    assert _codes(_map(_row(provenance=prov.PROTOCOL_CONSTRAINT))) == [
        "constraint-without-registration"]
    body = _map(_row(provenance=prov.PROTOCOL_CONSTRAINT, evidence=[REGISTRATION],
                     check="the bar is 0.05 and the allocation is 16 seeds"))
    assert prov.check_map(body, ROOT) == []


def test_a_claim_that_quotes_a_figure_must_trace_it_to_a_cited_artifact():
    good = {"claim_id": "C900", "claim": "precision never exceeds 0.3438",
            "supporting_evidence": ["docs/gate13_allocation_rule.json"]}
    assert prov.check_claims({"claims": [good]}, ROOT) == []
    drifted = dict(good, claim="precision never exceeds 0.3443")
    findings = prov.check_claims({"claims": [drifted]}, ROOT)
    assert [f["code"] for f in findings] == ["figure-untraceable"]
    assert "0.3443" in findings[0]["message"]


def test_a_claim_that_quotes_a_figure_and_cites_nothing_is_refused():
    body = {"claims": [{"claim_id": "C901", "claim": "the cap recovers 112 edges",
                        "supporting_evidence": []}]}
    assert [f["code"] for f in prov.check_claims(body, ROOT)] == ["figure-unbacked"]


def test_a_one_decimal_label_is_not_read_as_a_figure():
    claim = {"claim_id": "C902", "claim": "the v1 result (TR 3.2) reproduced",
             "supporting_evidence": [CITING]}
    assert prov.figures_in(claim) == []


def test_the_report_is_derived_from_the_records():
    mapdoc = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    decisions = json.loads(DECISIONS.read_text(encoding="utf-8"))
    report = prov.render_report(mapdoc, ledger, decisions, ROOT)
    assert "{" not in report and "}" not in report
    per_tag = prov.counts(mapdoc)
    for tag in prov.TAGS:
        assert tag in report, tag
        assert str(per_tag[tag]) in report, tag
    for finding in prov.check_claims(ledger, ROOT):
        assert finding["subject"] in report, finding["subject"]


def test_the_report_names_a_figure_that_does_not_trace():
    mapdoc = _map(_row())
    ledger = {"claims": [{"claim_id": "C903", "claim": "the headroom is 0.999999",
                          "supporting_evidence": [CITING],
                          "provenance": prov.OWNER_READING}]}
    report = prov.render_report(mapdoc, ledger, {"decisions": []}, ROOT)
    assert "C903" in report and "0.999999" in report


def test_the_provenance_mode_runs_and_prints_the_map_tally(capsys):
    from benchmarks import research_trace

    assert research_trace.main(["--provenance"]) == 0
    out = capsys.readouterr().out
    rows = len(json.loads(ARTIFACT.read_text(encoding="utf-8"))["rows"])
    assert "Bottleneck map (%d rows)" % rows in out
    assert prov.OWNER_READING in out


def test_every_claim_carries_one_tag_and_the_ledger_passes_its_own_rules():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert prov.check_ledger(ledger, ROOT) == []
    per_tag = prov.claim_counts(ledger)
    assert sum(per_tag.values()) == len(ledger["claims"])
    assert set(ledger["schema"]["provenance"]) == set(prov.TAGS)
    assert ledger["schema"]["provenance_rule"].strip()


def test_a_claim_without_a_tag_is_refused():
    ledger = {"claims": [{"claim_id": "C1", "classification": "HYPOTHESIS",
                          "status": "ACTIVE", "supporting_evidence": [CITING]}]}
    assert [f["code"] for f in prov.check_ledger(ledger, ROOT)] == ["claim-tag-missing"]
    with pytest.raises(ValueError):
        prov.claim_counts(ledger)


def test_an_unknown_claim_tag_is_refused():
    ledger = {"claims": [{"claim_id": "C2", "classification": "HYPOTHESIS",
                          "status": "ACTIVE", "supporting_evidence": [CITING],
                          "provenance": "MEASURED"}]}
    assert [f["code"] for f in prov.check_ledger(ledger, ROOT)] == ["claim-tag-unknown"]


def test_an_agent_inference_may_not_carry_a_demonstrated_claim():
    claim = {"claim_id": "C3", "classification": "DEMONSTRATED", "status": "ACTIVE",
             "supporting_evidence": [CITING], "provenance": prov.AGENT_INFERRED}
    assert [f["code"] for f in prov.check_ledger({"claims": [claim]}, ROOT)] == [
        "inference-supports-claim"]
    claim["classification"] = "HYPOTHESIS"
    assert prov.check_ledger({"claims": [claim]}, ROOT) == []


def test_a_claim_tag_that_claims_support_must_name_an_artifact():
    claim = {"claim_id": "C4", "classification": "SUPPORTED", "status": "ACTIVE",
             "supporting_evidence": [], "provenance": prov.ARTIFACT_READ}
    assert [f["code"] for f in prov.check_ledger({"claims": [claim]}, ROOT)] == [
        "claim-unbacked-tag"]


def test_the_published_ledger_prints_every_claims_tag():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    page = (ROOT / "docs" / "CLAIM-LEDGER.md").read_text(encoding="utf-8")
    assert "What each claim rests on" in page
    assert "| Claim | Statement | Classification | Questions | Provenance |" in page
    for claim in ledger["claims"]:
        assert claim["provenance"] in page, claim["claim_id"]
    findings_page = (ROOT / "docs" / "RESEARCH-FINDINGS.md").read_text(encoding="utf-8")
    for claim in ledger["claims"]:
        if claim["status"] != "ACTIVE":
            assert claim["provenance"] in findings_page, claim["claim_id"]


def test_the_ledger_has_no_untraceable_figure():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert prov.check_claims(ledger, ROOT) == []


def test_the_repaired_claims_cite_the_artifact_that_records_their_figure():
    claims = {c["claim_id"]: c for c in json.loads(LEDGER.read_text(encoding="utf-8"))["claims"]}
    assert "docs/acquisition_endpoint_audit.json" in claims["C010"]["supporting_evidence"]
    assert "docs/FORCE-MATRIX-RESULTS.md" in claims["C011"]["supporting_evidence"]
    for cid in ("C010", "C011"):
        figures = prov.figures_in(claims[cid])
        assert figures, cid
        for figure in figures:
            assert any(figure in (ROOT / path).read_text(encoding="utf-8")
                       for path in claims[cid]["supporting_evidence"]), (cid, figure)


def test_the_report_tallies_the_claims_by_tag():
    mapdoc = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    report = prov.render_report(mapdoc, ledger, {"decisions": []}, ROOT)
    for tag in prov.TAGS:
        assert tag in report, tag
    assert str(prov.claim_counts(ledger)[prov.OWNER_READING]) in report
    assert "figures absent from every artifact the claim cites: 0" in report


def test_the_report_says_where_an_untraced_figure_does_live():
    ledger = {"claims": [{"claim_id": "C904", "claim": "the headroom was 0.005647",
                          "supporting_evidence": ["docs/bottleneck_map.json"],
                          "provenance": prov.OWNER_READING}]}
    report = prov.render_report({"rows": []}, ledger, {"decisions": []}, ROOT)
    assert "recorded in:" in report
    assert "docs/acquisition_endpoint_audit.json" in report

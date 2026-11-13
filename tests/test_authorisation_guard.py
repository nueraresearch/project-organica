"""A preparation-only quote is not a run authorisation."""
LAYER = "static"

from benchmarks import authorisation_guard as guard
from benchmarks import retention_formation_anchored as runner
from benchmarks import retention_formation_anchored_prereg as block

CAP_QUOTE = (
    "Write the dated cap-112 authorisation document for the comparator, Q1 "
    "and Q2, recording the owner's grant against the three frozen records."
)
BAND_QUOTE = (
    "Preregister a repaired band block with fresh seeds and the fixed harness, "
    "with B5 still able to fail, and record its grant before running."
)
RUN_QUOTE = "Fix the post-landmark assertion cycle and rerun the twelve cells."


def test_preparation_only_quotes_are_rejected_on_a_frozen_run_record():
    for quote in (CAP_QUOTE, BAND_QUOTE,
                  "Prepare the dated grant document without running it."):
        body = {"status": "FROZEN, RUN", "authorisation": {"quote": quote}}
        assert guard.preparation_only(quote)
        assert guard.problems(body)


def test_run_quotes_are_accepted():
    for quote in (RUN_QUOTE, "Authorize all runs",
                  "Preregister and run the core+band admission rule.",
                  "Preregister T1b with a denominator gate, then run it."):
        body = {"status": "FROZEN, RUN", "authorisation": {"quote": quote}}
        assert not guard.preparation_only(quote)
        assert guard.problems(body) == []


def test_the_guard_only_applies_to_frozen_run_records():
    body = {"status": "FROZEN, NOT RUN", "authorisation": {"quote": CAP_QUOTE}}
    assert guard.problems(body) == []
    body = {"status": "GRANTED, NOT RUN", "authorisation": {"quote": CAP_QUOTE}}
    assert guard.problems(body) == []


def test_retention_preflight_carries_the_specific_reason(monkeypatch):
    doc = block.record()
    doc["status"] = "FROZEN, RUN"
    doc["authorisation"] = {"required": True, "granted": True,
                            "granted_on": "2026-11-13",
                            "document": "docs/USER-MANUAL.md",
                            "quote": CAP_QUOTE}
    monkeypatch.setattr(block, "record", lambda: doc)
    reasons = runner.preflight()
    assert any("preparation-only" in reason for reason in reasons)


def test_scan_flags_the_known_cap112_records_but_not_the_run_quote_record():
    flagged = dict(guard.scan())
    assert "docs/presence_cap_1_112_prereg.json" in flagged
    assert "docs/presence_comparator_112_prereg.json" in flagged
    assert "docs/retention_formation_anchored_prereg.json" not in flagged


def test_check_mode_exits_zero_when_scan_is_clean(monkeypatch, capsys):
    monkeypatch.setattr(guard, "scan", lambda: [])
    assert guard.main(["--check"]) == 0
    assert "authorisation guard: clean" in capsys.readouterr().out


def test_check_mode_exits_one_on_a_violation(monkeypatch, capsys):
    monkeypatch.setattr(guard, "scan", lambda: [
        ("docs/example.json", "FROZEN, RUN record cites a preparation-only quote")])
    assert guard.main(["--check"]) == 1
    out = capsys.readouterr().out
    assert "docs/example.json" in out
    assert "preparation-only" in out
    assert "1 violation(s)" in out

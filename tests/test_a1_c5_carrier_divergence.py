"""A1 C5 carrier divergence — the record that keeps observed and current cycles apart."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import json
from pathlib import Path

from benchmarks import a1_c5_carrier_divergence as divergence


def _record() -> dict:
    return json.loads(Path("docs/a1_c5_carrier_divergence.json").read_text(
        encoding="utf-8"))


def test_record_is_clean_and_agrees_with_the_c5_audit():
    doc = _record()
    assert divergence.problems(doc) == []
    assert doc["adopted_block_cross_check"]["agrees"] is True

    audit = json.loads(Path("docs/a1_c5_target_timing.json").read_text(
        encoding="utf-8"))
    adopted = next(row for row in doc["blocks"] if row["role"] == "ADOPTED CANDIDATE")
    assert adopted["earliest_observed_carrier_cycle"] == audit[
        "earliest_observed_carrier_cycle"]
    assert adopted["earliest_current_carrier_cycle"] == audit[
        "earliest_current_carrier_cycle"]
    assert adopted["verdict"] == "CLEARS C5"


def test_both_divergence_cases_are_measured_one_clearing_one_failing():
    doc = _record()
    blocks = {row["block"]: row for row in doc["blocks"]}

    assert blocks[2074]["verdict"] == "CLEARS C5"
    assert blocks[2071]["verdict"] == "FAILS C5"
    for row in blocks.values():
        assert row["measured_here"] is True
        assert row["n20_rows"] == 120
        assert row["current_rows"] == 24
        assert len(row["per_seed"]) == 6
        # The separation itself, which is the point of the record.
        assert row["current_minus_observed"] != 0
        assert row["current_minus_observed"] == (
            row["earliest_current_carrier_cycle"]
            - row["earliest_observed_carrier_cycle"])

    assert doc["finding"]["divergence_with_clearing_c5"] is True
    assert doc["finding"]["divergence_with_failing_c5"] is True
    assert set(doc["finding"]["divergent_blocks_measured"]) == {2074, 2071}
    assert doc["finding"]["equal_blocks_measured"] == []


def test_the_equality_case_is_cited_not_remeasured():
    doc = _record()
    cited = doc["cited_cases"][0]

    assert cited["block"] == 2063
    assert cited["measured_here"] is False
    assert cited["earliest_observed_carrier_cycle"] == 5
    assert cited["earliest_current_carrier_cycle"] == 5
    assert "61ac416" in cited["source"]
    assert "spent" in cited["why_not_remeasured"]
    # A spent block is never re-declared as a measured one.
    assert all(row["measured_here"] is True for row in doc["blocks"])
    assert all(row["seeds"][0] // 10000 in (2071, 2074) for row in doc["blocks"])


def test_page_states_the_argument_and_the_limit():
    page = Path("docs/A1-C5-CARRIER-DIVERGENCE.md").read_text(encoding="utf-8")
    assert "| 2074 | ADOPTED CANDIDATE | 6 | 8 | +2 | 0 |" in page
    assert "| 2071 | SCREENED — REJECTED BY C5 | 4 | 10 | +6 |" in page
    assert "| 2063 | SUPERSEDED — EQUALITY CASE | 5 | 5 |" in page
    assert "distinct observables" in page
    assert "cannot order a population" in page


def test_self_test_fires_on_each_inconsistency():
    assert divergence.self_test() == []

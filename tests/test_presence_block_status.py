"""The manual's conversion-block row must be derived from the records, and the derivation checked.

The row was typed when Q1-Q3 were unrun, annotated when they were authorised, and
rewritten when they ran. Each edit was a chance to leave the manual describing a state
the records no longer hold, and the manual is the first thing a reader opens.

These tests hold the row to its source: it must equal a fresh render, every field it
states must match the record it came from, and the check must go red both when the row
is stale and when a record contradicts itself.
"""
from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import presence_block_status as blocks  # noqa: E402

MANUAL = REPO / "docs" / "USER-MANUAL.md"


def manual_text() -> str:
    return MANUAL.read_text(encoding="utf-8")


def test_the_row_is_derived_rather_than_typed():
    assert blocks.region_of(manual_text()) == blocks.render(), (
        "the manual's conversion-block row does not match a fresh render; "
        "run python -m benchmarks.presence_block_status")
    assert blocks.problems() == []


def test_every_field_it_states_matches_the_record():
    fragment = blocks.region_of(manual_text())
    for path in blocks.RECORDS:
        record = json.loads(path.read_text(encoding="utf-8"))
        auth = record["authorisation"]

        assert "`%s`" % record["prereg"] in fragment
        assert record["frozen_on"] in fragment, record["prereg"]
        assert "`%s`" % blocks._rel(path) in fragment
        assert "**%s**" % record["status"] in fragment
        assert "`%s`" % auth["document"] in fragment
        assert auth["granted_on"] in fragment

        if record["status"] == blocks.RUN:
            result = record["result"]
            assert "`%s`" % result["verdict"] in fragment
            assert "`%s`" % result["artifact"] in fragment
            assert "`%s`" % result["page"] in fragment
            # the states the row asserts are states the tree has to hold
            assert (REPO / result["artifact"]).exists()
            assert (REPO / result["page"]).exists()
            assert (REPO / auth["document"]).exists()
            assert record["no_cells_run"] is False


def test_the_check_reports_a_stale_row():
    stale = blocks.with_fragment(manual_text(), "**All three blocks are `FROZEN, NOT RUN`.**")
    found = blocks.problems(text=stale)
    assert any("stale" in sentence for sentence in found), found


def test_the_check_reports_a_record_that_contradicts_itself():
    records = blocks.load_records()

    missing = json.loads(json.dumps(records[0]))
    missing["result"]["artifact"] = "docs/no_such_run_artifact.json"
    found = blocks.problems(records=[missing] + records[1:])
    assert any("no_such_run_artifact" in sentence for sentence in found), found

    unrun = json.loads(json.dumps(records[1]))
    unrun["status"] = blocks.NOT_RUN
    unrun["no_cells_run"] = True
    found = blocks.problems(records=records[:1] + [unrun] + records[2:])
    assert any("carries a result block" in sentence for sentence in found), found

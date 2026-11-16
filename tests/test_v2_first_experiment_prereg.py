"""The first experiment's skeleton fixes what must not be chosen after a result, and quotes the artifact."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "V2-FIRST-EXPERIMENT-PREREGISTRATION.md"
SIZING = ROOT / "docs" / "v2_primitive_sizing.json"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_it_is_a_skeleton_that_authorises_nothing() -> None:
    text = _text()
    assert "DRAFT SKELETON — NOT A PRE-REGISTRATION, AND NO CELL IS AUTHORISED" in text
    assert "**Authorises:** nothing" in text
    decisions = json.loads((ROOT / "docs" / "decisions.json").read_text(encoding="utf-8"))
    assert not [d for d in decisions["decisions"]
                if "PREREGISTRATION" in d["decision_id"] or "FIRST-EXPERIMENT" in d["decision_id"]]


def test_m_is_fixed_here_and_locked() -> None:
    text = _text()
    assert "**`m = 2`, fixed in this section at signing, before any cell runs.**" in text
    assert "**Changing `m` after this skeleton is signed is a new pre-registration.**" in text
    assert "an implementation constant is not a policy" in text


def test_the_threshold_table_is_the_sizing_artifact() -> None:
    art = json.loads(SIZING.read_text(encoding="utf-8"))
    text = _text()
    for threshold, row in art["admission"].items():
        label = "m >= %s" % threshold.split(">=")[1]
        line = "| `%s` | %d | %s |" % (label, row["composites"], format(row["primitive_bytes"], ","))
        assert line in text, line
    headline = art["headline"]
    assert "%.3f×" % headline["ratio_to_pair_tables"] in text
    assert "%.3f%%" % (headline["ratio_to_store"] * 100) in text
    assert "%d of %d" % (headline["composites"], headline["distinct_carriers"]) in text
    assert format(headline["store_bytes"], ",") in text


def test_the_acceptance_gates_and_invariants_are_named() -> None:
    text = _text()
    for gate in ("A1 — canonicalisation", "A2 — identifier invariants", "A3 — mutation invariants",
                 "A4 — cost", "A5 — determinism"):
        assert gate in text, gate
    for invariant in ("I1", "I2", "I3", "I4", "I5", "M1", "M2", "M3", "M4", "M5"):
        assert "`%s`" % invariant in text, invariant
    assert "`A1`–`A5`" in text
    assert "A partial pass is not a pass" in text


def test_the_failure_rule_is_the_charter_s() -> None:
    text = _text()
    assert "interval includes zero" in text
    assert "bookkeeping" in text and "charter fails" in text
    assert "cannot** rescue or fail the charter on its own" in text


def test_no_seed_is_reserved_by_this_draft() -> None:
    text = _text()
    assert "**none reserved by this draft**" in text
    registry = json.loads((ROOT / "docs" / "a1_seed_reservations.json").read_text(encoding="utf-8"))
    owners = {row["owner"] for row in registry["reservations"]}
    assert "docs/V2-FIRST-EXPERIMENT-PREREGISTRATION.md" not in owners


def test_the_open_fields_are_listed_as_open() -> None:
    text = _text()
    for field in ("Seed block", "Number of seeds", "World family and size", "Training / evaluation boundary",
                  "Interval method and level", "Scorer pin", "Readout implementation"):
        assert field in text, field

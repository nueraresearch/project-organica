"""A signed pre-registration fixes what must not be chosen after a result, and quotes the artifact it cites."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "V2-FIRST-EXPERIMENT-PREREGISTRATION.md"
SIZING = ROOT / "docs" / "v2_primitive_sizing.json"
SEEDS = ROOT / "docs" / "v2_first_cell_seeds.json"
PIN = ROOT / "docs" / "v2_first_cell_scorer_pin.json"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_it_is_signed_and_authorises_nothing_by_itself() -> None:
    text = _text()
    assert "SIGNED 2026-11-16 — THE PROTOCOL IS FIXED; NO CELL IS AUTHORISED" in text
    assert "**Authorises:** nothing" in text
    assert "| **Status** | `SIGNED 2026-11-16 — protocol fixed; no cell authorised` |" in text
    assert "_unsigned_" not in text


def test_m_is_fixed_here_and_locked() -> None:
    text = _text()
    assert "**`m = 2`, fixed in this section at signing, before any cell runs.**" in text
    assert "**Changing `m` after this pre-registration is signed is a new pre-registration.**" in text
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


def test_every_open_field_is_now_filled() -> None:
    text = _text()
    # seeds and pairing
    assert "Ten seeds, `20910101`–`20910110`" in text
    assert "paired by seed" in text
    # world and boundary, in blocks
    assert "blocks `0–95`" in text and "blocks `96–119`" in text and "blocks `80–95`" in text
    assert "92 of 120" in text
    # readout: target, smoothing, grid, per-arm selection
    assert "`α = 0.5`" in text
    assert "`{0, 1, 2, 4, 8}`" in text
    assert "selected **per arm**" in text
    # revision rule
    assert "trailing window of **20 sleep cycles**" in text
    # interval and VOID guard
    assert "10,000 resamples, 99% percentile" in text
    assert "fewer than **8 of 10**" in text
    # nothing left open
    assert "Nothing else in this document is open" in text


def test_the_seed_block_is_declared_and_held_not_spent() -> None:
    declared = json.loads(SEEDS.read_text(encoding="utf-8"))
    assert declared["seed_block"]["seeds"] == list(range(20910101, 20910111))
    assert declared["owner"] == "docs/V2-FIRST-EXPERIMENT-PREREGISTRATION.md"
    registry = json.loads((ROOT / "docs" / "a1_seed_reservations.json").read_text(encoding="utf-8"))
    held = [r for r in registry["reservations"] if r["owner"] == "docs/v2_first_cell_seeds.json"]
    assert len(held) == 1
    assert held[0]["seeds"] == list(range(20910101, 20910111))
    assert held[0]["spent"] is False


def test_the_scorer_pin_matches_the_files_on_disk() -> None:
    pin = json.loads(PIN.read_text(encoding="utf-8"))
    for module, digest in pin["modules"].items():
        assert hashlib.sha256((ROOT / module).read_bytes()).hexdigest() == digest, module
    assert pin["adapter"]["sha256"] is None
    assert "benchmarks/v2_first_cell_readout.py" in _text()


def test_the_authorisation_is_drafted_and_unsigned() -> None:
    decision = json.loads((ROOT / "docs" / "decisions.json").read_text(encoding="utf-8"))
    entry = [d for d in decision["decisions"] if d["decision_id"] == "DECISION-V2-FIRST-CELL"]
    assert len(entry) == 1 and entry[0]["status"] == "PENDING"
    doc = (ROOT / "docs" / "DECISION-V2-FIRST-CELL.md").read_text(encoding="utf-8")
    assert "DRAFT — AWAITING THE OWNER'S SIGNATURE; ONE CELL AND NO ENGINE CHANGE" in doc
    assert "no engine change" in doc
    assert "_unsigned_" in doc

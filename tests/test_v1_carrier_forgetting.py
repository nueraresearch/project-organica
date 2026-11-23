"""Carriers are measured against the engine's own prior window, and none are forgotten in this world."""
from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
from pathlib import Path

from benchmarks import v1_carrier_forgetting as forgetting

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "docs" / "v1_carrier_forgetting.json"
DOC = ROOT / "docs" / "V1-CARRIER-FORGETTING.md"


def _doc() -> dict:
    return json.loads(ART.read_text(encoding="utf-8"))


def test_the_page_is_rendered_from_the_artifact() -> None:
    assert DOC.read_text(encoding="utf-8") == forgetting.render_doc(_doc())


def test_the_outcomes_account_for_every_identity() -> None:
    doc = _doc()
    a = doc["accounting"]
    assert a["conserved"] is True
    assert a["retired_final"] + a["live_final"] + a["forgotten_final"] == a["identities"] == 177


def test_no_carrier_is_forgotten_in_this_world() -> None:
    doc = _doc()
    assert doc["forgetting"]["episodes"] == 0
    assert doc["forgetting"]["final"] == 0
    assert doc["window"]["first_forget_cycle"] is None


def test_the_simulation_reproduces_every_retirement_row() -> None:
    doc = _doc()
    assert doc["retirements"]["rows"] == 186
    assert doc["retirements"]["simulated"] == 186
    assert doc["retirements"]["simulation_matches"] is True


def test_the_window_drops_a_live_row_and_keeps_retired_rows_out() -> None:
    def row(rowid, cid, strength, retired=False, ctype="loop_candidate"):
        payload = {"id": cid, "type": ctype, "path": ["a", "b"], "strength": strength}
        if retired:
            payload["retired"] = True
        return {"rowid": rowid, "time": float(rowid), "source": "sleep:loop_candidate",
                "content": json.dumps(payload)}

    rows = [row(1, "loop_old", 0.9)] + [
        row(i, f"other_{i}", 0.5, ctype="concept_candidate") for i in range(2, 4102)]
    live, retired = forgetting._prior_at(rows, 4101)
    assert live == {}                       # rowid 1 is outside the newest 4,000 sleep rows
    rows[0] = row(4101, "loop_old", 0.9)    # the same carrier, now the newest row
    live, _ = forgetting._prior_at(rows, 4101)
    assert list(live) == ["loop_old"]

    rows.append(row(4102, "loop_dead", 0.1, retired=True))
    live, retired = forgetting._prior_at(rows, 4102)
    assert "loop_dead" not in live and "loop_dead" in retired  # a death record supersedes its live copies

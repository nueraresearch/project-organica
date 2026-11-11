"""PRESENCE-BAND-1 ran and is VOID on B5: record, grant, artifact and refusal must agree."""
LAYER = "static"

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import presence_band_rank_prereg as band  # noqa: E402


def test_the_record_checks_and_the_page_is_rendered():
    assert band.problems() == []
    assert band.PAGE.read_text(encoding="utf-8").strip() == band.render(band.record()).strip()


def test_the_block_ran_and_is_void_on_b5():
    doc = band.record()
    assert doc["status"] == "FROZEN, RUN" and doc["no_cells_run"] is False
    assert doc["runner"]["built"] is True and doc["runner"]["cells_run"] == 13
    assert doc["authorisation"]["granted"] is True
    assert doc["result"]["verdict"] == "VOID"
    assert [row["kind"] for row in doc["amendments"]] == [
        "grant-recorded", "harness-fixed", "run-completed", "budget-reconciled"]
    assert "guaranteed floor" in doc["amendments"][-1]["note"]
    assert "BAND-2" in doc["amendments"][-1]["note"]
    art = json.loads(band.RUN.read_text(encoding="utf-8"))
    assert art["verdict"] == "VOID" and art["gates"]["B5_cap_live"]["passed"] is False
    assert sum(1 for gate in art["gates"].values() if gate["passed"]) == 7
    assert sum(art["served_112"].values()) == 62
    assert all(row["served"] == 0 for row in art["cells"] if row["cap"] == 40)


def test_the_grant_quotes_its_document():
    auth = band.record()["authorisation"]
    text = (REPO / auth["document"]).read_text(encoding="utf-8")
    assert auth["quote"] in text and auth["granted_on"] in text


def test_the_preflight_refuses_a_rerun_before_a_cell_can_start():
    from benchmarks import presence_band_rank_arm as arm

    reasons = arm.preflight()
    assert any("closed" in reason for reason in reasons), reasons
    with pytest.raises(SystemExit) as raised:
        arm.main(["--measure"])
    assert raised.value.code == 2
    assert arm.check() == 0


def test_the_dry_run_lists_twelve_cells_and_the_self_test_passes():
    from benchmarks import presence_band_rank_arm as arm

    assert len(arm.planned()) == 12 and arm.self_test() == 0


def test_the_band_is_q4s_sixty_two_edges():
    q4 = json.loads(band.Q4.read_text(encoding="utf-8"))
    table = {str(row["seed"]): row for row in q4["stage_table"]}
    doc = band.record()
    assert doc["band"]["total"] == 62
    for seed, row in doc["band"]["seeds"].items():
        assert len(row["edges"]) == table[seed]["never_served_rank_half_to_cap"]
        assert all(21 <= edge[2] <= 40 for edge in row["edges"])


def test_a_status_rewrite_is_caught():
    doc = band.record(); doc["status"] = "FROZEN, NOT RUN"
    assert any("status" in p for p in band.problems(doc=doc, page=band.render(doc)))


def test_a_grant_without_its_document_is_caught():
    doc = band.record(); doc["authorisation"]["document"] = "docs/NO-SUCH-GRANT.md"
    assert any("does not exist" in p for p in band.problems(doc=doc, page=band.render(doc)))


def test_a_dropped_named_edge_is_caught():
    doc = band.record(); seed = next(iter(doc["band"]["seeds"]))
    doc["band"]["seeds"][seed]["edges"].pop()
    assert any("sum to" in p or "21-40 count" in p
               for p in band.problems(doc=doc, page=band.render(doc)))


def test_a_dropped_direction_is_caught():
    doc = band.record()
    doc["decision_table"] = [r for r in doc["decision_table"]
                             if r["verdict"] != "BAND NOT IN SERVICE"]
    assert any("direction" in p for p in band.problems(doc=doc, page=band.render(doc)))


def test_an_acceptance_quote_that_is_not_the_decisions_is_caught():
    doc = band.record(); doc["acceptance"]["quote"] = "the band should be served somewhere"
    assert any("acceptance" in p for p in band.problems(doc=doc, page=band.render(doc)))


def test_a_stale_page_is_caught():
    doc = band.record()
    stale = band.render(doc).replace("FROZEN, RUN", "FROZEN, NOT RUN", 1)
    assert any("page does not match" in p for p in band.problems(doc=doc, page=stale))


def test_the_engine_at_run_is_the_shipped_one():
    import organica
    from organica.sleep import SleepService

    assert SleepService.MAX_PREDICTIONS == 112
    assert band.record()["engine"]["version"] == organica.__version__ == "0.15.0"
    assert band.record()["engine"]["edit"] == "none"


def test_a_renamed_or_misranked_edge_is_caught_against_its_part():
    part = {"seed": 20611601, "world_digest": "x", "present_edges": [["a", "b"], ["c", "d"]],
            "windows_world": [[], ["a>b"]],
            "universe": [[{"rank": 5, "edge": ["a", "b"], "relation": "transition"},
                          {"rank": 25, "edge": ["c", "d"], "relation": "transition"}]]}
    doc = {"band": {"seeds": {"20611601": {"world_digest": "x", "edges": [["c", "d", 25]]}}}}
    assert band.ledger_problems(doc, {"20611601": part}) == []
    doc["band"]["seeds"]["20611601"]["edges"] = [["c", "d", 26]]
    assert band.ledger_problems(doc, {"20611601": part})
    doc["band"]["seeds"]["20611601"]["edges"] = [["c", "e", 25]]
    assert band.ledger_problems(doc, {"20611601": part})

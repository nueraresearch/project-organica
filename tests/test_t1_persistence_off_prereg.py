"""T1 ran to VOID: the record, its grant and its result must stay consistent.

Each mutation below proves one guard can fail: a status rewrite, a dropped direction,
a grant without its document, and a stale page.
"""
LAYER = "static"

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import t1_persistence_off_prereg as t1  # noqa: E402


def test_the_record_checks_and_the_page_is_rendered():
    assert t1.problems() == []
    assert t1.RECORD.exists() and t1.PAGE.exists()
    assert t1.PAGE.read_text(encoding="utf-8").strip() == t1.render(t1.record()).strip()


def test_the_block_ran_and_is_void_on_g4():
    doc = t1.record()
    assert doc["status"] == "FROZEN, RUN"
    assert doc["no_cells_run"] is False
    assert doc["runner"]["built"] is True
    assert doc["runner"]["cells_run"] == 13
    assert doc["result"]["verdict"] == "VOID"
    assert [row["kind"] for row in doc["amendments"]] == [
        "runner-built", "run-completed", "diagnostic-disclosure"]

    art = json.loads(t1.RUN.read_text(encoding="utf-8"))
    assert art["verdict"] == "VOID"
    assert len(art["cells"]) == 12
    assert art["gates"]["G4_denominator"]["passed"] is False
    assert sum(1 for gate in art["gates"].values() if gate["passed"]) == 6


def test_the_grant_quotes_its_document():
    doc = t1.record()
    auth = doc["authorisation"]
    text = (REPO / auth["document"]).read_text(encoding="utf-8")
    assert auth["granted"] is True
    assert auth["quote"] in text
    assert auth["granted_on"] in text


def test_the_seed_block_is_fresh():
    from benchmarks.presence_cap_experiment import seed_collisions

    doc = t1.record()
    collisions = seed_collisions(
        doc["design"]["seeds"] + [doc["design"]["bootstrap"]],
        allow=(t1.RECORD, t1.PAGE, t1.RUN, t1.RESULT_PAGE, t1.AUTH_DOC,
               t1.ROOT / "docs/persistence_zero_served_diagnostic.json",
               t1.ROOT / "docs/PERSISTENCE-ZERO-SERVED-NOTE.md"))
    assert collisions == {}


def test_a_status_rewrite_is_caught():
    doc = t1.record()
    doc["status"] = "FROZEN, NOT RUN"
    found = t1.problems(doc=doc, page=t1.render(doc))
    assert any("status" in problem for problem in found)


def test_a_dropped_direction_is_caught():
    doc = t1.record()
    doc["decision_table"] = [row for row in doc["decision_table"]
                             if row["verdict"] != "PERSISTENCE NOT LIMITING"]
    found = t1.problems(doc=doc, page=t1.render(doc))
    assert any("direction" in problem for problem in found)


def test_a_grant_without_its_document_is_caught():
    doc = t1.record()
    doc["authorisation"]["document"] = "docs/NO-SUCH-GRANT.md"
    found = t1.problems(doc=doc, page=t1.render(doc))
    assert any("does not exist" in problem for problem in found)


def test_a_stale_page_is_caught():
    doc = t1.record()
    stale = t1.render(doc).replace("FROZEN, RUN", "FROZEN, NOT RUN", 1)
    found = t1.problems(doc=doc, page=stale)
    assert any("page does not match" in problem for problem in found)


def test_the_engine_at_run_is_the_shipped_one():
    import organica
    from organica.sleep import SleepService

    assert SleepService.MAX_PREDICTIONS == 112
    assert t1.record()["engine"]["version"] == organica.__version__ == "0.15.0"
    assert t1.record()["engine"]["edit"] == "none"

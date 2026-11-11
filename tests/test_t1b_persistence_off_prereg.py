"""T1b ran and returned PERSISTENCE CONTRIBUTES: the corrected G4 must admit measured zeros."""
LAYER = "static"

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import t1b_persistence_off_prereg as t1b  # noqa: E402


def test_the_record_checks_and_the_page_is_rendered():
    assert t1b.problems() == []
    assert t1b.PAGE.read_text(encoding="utf-8").strip() == t1b.render(t1b.record()).strip()


def test_the_block_ran_and_adjudicated_the_endpoint():
    doc = t1b.record()
    assert doc["status"] == "FROZEN, RUN" and doc["no_cells_run"] is False
    assert doc["runner"]["built"] is True and doc["runner"]["cells_run"] == 13
    assert doc["result"]["verdict"] == "PERSISTENCE CONTRIBUTES"
    assert [row["kind"] for row in doc["amendments"]] == [
        "runner-built", "run-completed", "diagnostic-disclosure"]
    art = json.loads(t1b.RUN.read_text(encoding="utf-8"))
    assert art["verdict"] == "PERSISTENCE CONTRIBUTES"
    assert all(gate["passed"] for gate in art["gates"].values())
    assert len(art["gates"]) == 7
    g4 = art["gates"]["G4_denominator"]
    assert g4["passed"] is True and g4["zero_p"] == []
    assert len(g4["zero_s_ever"]) == 3
    assert art["bootstrap"]["diffs"] == [101, 94, 100, 100, 98, 96]
    assert art["bootstrap"]["mean"] == pytest.approx(98.16666666666667)
    assert [art["bootstrap"]["lower"], art["bootstrap"]["upper"]] == [96, 100]
    assert art["bootstrap"]["positive_seeds"] == 6


def test_g4_admits_a_measured_zero_s_ever_but_not_a_zero_p():
    art = json.loads(t1b.RUN.read_text(encoding="utf-8"))
    assert all(cell["present"] > 0 for cell in art["cells"])
    assert any(cell["s_ever"] == 0 for cell in art["cells"] if cell["arm"] == "persistence_off")
    doc = t1b.record()
    doc["gates"]["G4_denominator"] = ("P and S_ever are non-zero in every cell; a zero stage is "
                                      "not measurable")
    found = t1b.problems(doc=doc, page=t1b.render(doc))
    assert any("zero s_ever" in problem for problem in found), found
    assert any("admissible" in problem for problem in found), found


def test_the_grant_quotes_its_document():
    auth = t1b.record()["authorisation"]
    text = (REPO / auth["document"]).read_text(encoding="utf-8")
    assert auth["quote"] in text and auth["granted_on"] in text


def test_the_seed_block_is_fresh():
    doc = t1b.record()
    from benchmarks.presence_cap_experiment import seed_collisions
    collisions = seed_collisions(
        doc["design"]["seeds"] + [doc["design"]["bootstrap"]],
        allow=(t1b.RECORD, t1b.PAGE, t1b.RUN, t1b.RESULT_PAGE, t1b.AUTH_DOC,
               t1b.ROOT / "docs/persistence_zero_served_diagnostic.json",
               t1b.ROOT / "docs/PERSISTENCE-ZERO-SERVED-NOTE.md"))
    assert collisions == {}


def test_the_preflight_refuses_a_rerun_before_a_cell_can_start():
    from benchmarks import t1b_persistence_off_arm as arm

    reasons = arm.preflight()
    assert any("closed" in reason for reason in reasons), reasons
    with pytest.raises(SystemExit) as raised:
        arm.main(["--measure"])
    assert raised.value.code == 2
    assert arm.check() == 0


def test_a_status_rewrite_is_caught():
    doc = t1b.record(); doc["status"] = "FROZEN, NOT RUN"
    assert any("status" in p for p in t1b.problems(doc=doc, page=t1b.render(doc)))


def test_a_stale_page_is_caught():
    doc = t1b.record()
    stale = t1b.render(doc).replace("FROZEN, RUN", "FROZEN, NOT RUN", 1)
    assert any("page does not match" in p for p in t1b.problems(doc=doc, page=stale))


def test_the_engine_at_run_is_the_shipped_one():
    import organica
    from organica.sleep import SleepService

    assert SleepService.MAX_PREDICTIONS == 112
    assert t1b.record()["engine"]["version"] == organica.__version__ == "0.15.0"
    assert t1b.record()["engine"]["edit"] == "none"

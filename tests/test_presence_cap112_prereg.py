"""The cap-112 drafts must be frozen, unrun, granted, runner-built, and must reject a cap-40 design."""
LAYER = "static"

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import presence_cap112_prereg as draft  # noqa: E402


def test_each_draft_is_frozen_unrun_and_granted():
    built = draft.records()

    assert len(built) == 3
    document = draft.AUTHORISATION_DOC.read_text(encoding="utf-8")
    for record in built.values():
        assert record["cap"] == 112
        auth = record["authorisation"]
        assert auth["granted"] is True and auth["granted_on"] == draft.GRANT_DATE
        assert auth["quote"] in document and auth["granted_on"] in document
        assert record["runner"]["status"] == "built"
        assert (draft.ROOT / record["runner"]["module"]).exists()
        kinds = [row["kind"] for row in record["amendments"]]
        if record["block"] in ("comparator", "Q2"):
            assert record["status"] == "FROZEN, RUN"
            assert record["no_cells_run"] is False
            assert kinds == ["runner-built", "cap-landed", "run-completed"], kinds
            expected = ("docs/presence_comparator_112_run.json"
                        if record["block"] == "comparator" else "docs/presence_cap_1_112_run.json")
            assert record["result"]["artifact"] == expected
            assert (draft.ROOT / record["result"]["artifact"]).exists()
        else:
            assert record["status"] == "FROZEN, NOT RUN"
            assert record["no_cells_run"] is True
            assert kinds == ["runner-built", "cap-landed"], kinds
            assert record["result"] is None
        assert record["amendments"][-1]["date"] == draft.FROZEN_ON
        assert record["gates"] and record["gates_control"]


def test_the_three_drafts_are_the_comparator_q1_and_q2():
    built = draft.records()

    assert {r["block"] for r in built.values()} == {"comparator", "Q1", "Q2"}
    q2 = [r for r in built.values() if r["block"] == "Q2"][0]
    assert q2["design"]["shipped_cap"] == 112
    assert q2["design"]["levels"] == [40, 80, 112, draft.cap.UNCAPPED]
    assert q2["design"]["cells"] == 24
    assert q2["design"]["witness_cell"]["cap"] == 112


def test_the_record_and_its_page_are_current():
    built = draft.records()

    for name, record in built.items():
        stored = json.loads((draft.DOCS / name).read_text(encoding="utf-8"))
        assert stored == record
        page = draft.DOCS / record["page"]
        assert page.read_text(encoding="utf-8") == draft.render({name: record})[record["page"]]
        assert draft.problems(record, allow=[draft.DOCS / name]) == []


def test_a_cap_40_design_is_rejected():
    record = copy.deepcopy(list(draft.records().values())[0])
    record["cap"] = 40
    record["design"]["cap"] = 40

    assert draft.problems(record), "a cap-40 record must not pass the cap-112 check"


def test_a_grant_without_its_document_is_rejected():
    record = copy.deepcopy(list(draft.records().values())[0])
    record["authorisation"]["document"] = "docs/NO-SUCH-AUTHORISATION.md"

    assert draft.problems(record), "a grant must name a document that exists"


def test_a_grant_whose_quote_is_missing_is_rejected():
    record = copy.deepcopy(list(draft.records().values())[0])
    record["authorisation"]["quote"] = "Authorize all runs"

    assert draft.problems(record), "the quoted words must appear in the document"

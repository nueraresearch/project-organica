"""The lineage record carries a build only when it can prove the rows did not move.

The mechanism exists so a behaviour-preserving engine edit can land without re-running the frozen
presence blocks (which would re-derive their verdicts) and without restamping a measurement. Its
whole safety rests on the proof: a link must name every canary digest the predecessor recorded,
the authorising decision must be ADOPTED, and the recorded canaries must still be the ones on disk.
These tests fail the mechanism if any of those stops being enforced.
"""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
from pathlib import Path

from benchmarks import engine_lineage as el

ROOT = Path(__file__).resolve().parent.parent
CANARIES = ROOT / "docs/block_canaries.json"
RECORD = ROOT / "docs/engine_lineage.json"
HISTORICAL = ROOT / "docs/engine_lineage_0.14.0.json"


def retired() -> dict:
    """The 0.14.0 link, kept as a historical record after the cap-112 landing."""
    links = json.loads(HISTORICAL.read_text(encoding="utf-8"))["links"]
    assert links, "the retired 0.14.0 link is not recorded"
    return links[-1]


def test_the_recorded_lineage_is_valid_and_its_head_is_the_shipped_engine():
    assert RECORD.exists(), "no lineage record; run python -m benchmarks.engine_lineage --init"
    assert el.problems() == []
    assert el.load()["links"] == [], "the 0.14.0 link must be retired, not carried past the cap"
    assert el.same_build(el.engine_stamp.engine_sha256())


def test_the_build_the_canaries_recorded_is_reachable_through_the_recorded_link():
    predecessor = json.loads(CANARIES.read_text(encoding="utf-8"))["engine_sha256"]
    assert el.same_build(predecessor), (
        "the build the canaries were recorded on is not the shipped engine and no link joins them")
    assert not el.same_build("0" * 64), "an unrecorded build must never pass a build check"


def test_every_link_proves_the_digests_the_canaries_recorded():
    links = json.loads(HISTORICAL.read_text(encoding="utf-8"))["links"]
    assert links, "the split has no recorded link"
    for link in links:
        cells = el.proof_cells(link)
        assert set(link["proof"]) == set(cells)
        assert link["proof"] == cells


def test_a_link_missing_a_cell_is_rejected():
    link = dict(retired())
    proof = dict(link["proof"])
    proof.pop(sorted(proof)[0])
    link["proof"] = proof
    assert any("omits" in problem for problem in el.link_problems(link))


def test_a_moved_digest_is_rejected():
    link = dict(retired())
    proof = dict(link["proof"])
    block = sorted(proof)[0]
    proof[block] = "0" * 64
    link["proof"] = proof
    assert any("moved" in problem for problem in el.link_problems(link))


def test_a_pending_decision_cannot_authorise_equivalence():
    link = dict(retired())
    link["decision"] = "DECISION-DENSITY-EXCLUSION"  # a recorded PENDING decision
    assert any("ADOPTED" in problem for problem in el.link_problems(link))


def test_equivalence_follows_a_chain_of_links():
    cells = el.canary_cells()
    older, middle, current = "a" * 64, "b" * 64, "c" * 64
    chain = {"kind": el.KIND, "links": [
        {"from": older, "to": middle, "from_commit": "f" * 40,
         "decision": "DECISION-CAP-SEMANTICS", "changed_files": ["organica/sleep_extraction.py"],
         "proof": cells, "note": "chain"},
        {"from": middle, "to": current, "from_commit": "e" * 40,
         "decision": "DECISION-CAP-SEMANTICS", "changed_files": ["organica/sleep_extraction.py"],
         "proof": cells, "note": "chain"},
    ]}
    assert el.same_build(older, current=current, record=chain)
    assert el.same_build(middle, current=current, record=chain)
    assert not el.same_build("d" * 64, current=current, record=chain)


def test_a_commit_is_carried_only_on_the_build_the_lineage_recorded():
    link = retired()
    assert el.carried_commit(link["from_commit"], link["from"])
    assert not el.carried_commit("0" * 40, link["from"]), "a forged commit must not be carried"
    assert not el.carried_commit(link["from_commit"], "0" * 64), "the commit belongs to its build"


def test_a_link_must_name_a_proof_record_that_exists():
    link = dict(retired())
    link["proof_record"] = "docs/no_such_canaries.json"
    assert any("proof_record" in problem for problem in el.link_problems(link))


def test_the_retired_link_still_carries_its_own_build():
    link = retired()
    assert el.same_build(link["from"], current=link["to"], record={"links": [link]})


def test_a_stale_head_is_a_problem():
    record = {"kind": el.KIND,
              "links": [dict(link) for link in
                        json.loads(HISTORICAL.read_text(encoding="utf-8"))["links"]]}
    record["links"][-1]["to"] = "0" * 64
    assert any("head" in problem for problem in el.problems(record))

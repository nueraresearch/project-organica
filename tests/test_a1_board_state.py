"""Both halves of the A1 board are generated, and stale rows must fail.

The first guard checked one direction on a hand-written table: every pending decision had to appear.
A row could then outlive its status. The decision block closed that for decisions; the branch block
closes it for artifacts, whose state is derived from a manifest that names, per branch, the record or
file that settles it and the check that proves it.

These tests hold the properties that make the derivation worth having:

* both committed blocks are their renders, so a change on either side (a decision's status, an
  artifact's contents, a manifest assertion) leaves the board stale rather than passing;
* a branch whose artifact assertion is unmet renders OPEN, never closed;
* every link in either block resolves from `docs/`.
"""

from __future__ import annotations

import json
from pathlib import Path

from benchmarks import a1_board

LAYER = "static"

DOCS = Path(__file__).resolve().parents[1] / "docs"
CHECKLIST = DOCS / "A1-PRE-FREEZE-CHECKLIST.md"
STALE_SENTENCE = "No substantive owner choice remains open"


def _text() -> str:
    return CHECKLIST.read_text(encoding="utf-8")


def _entries() -> list[dict]:
    return json.loads((DOCS / "decisions.json").read_text(encoding="utf-8"))["decisions"]


def _branches() -> list[dict]:
    return json.loads((DOCS / "a1_board_manifest.json").read_text(encoding="utf-8"))["branches"]


def test_both_committed_blocks_are_their_renders() -> None:
    found = a1_board.block_problems(_text())
    assert not found, found


def test_every_a1_decision_is_rendered_exactly_once() -> None:
    body = a1_board.block(_text())
    assert body is not None
    a1 = [entry for entry in _entries() if entry["decision_id"].startswith(a1_board.PREFIX)]
    assert len(a1) == 11
    for entry in a1:
        assert body.count("[`%s`]" % entry["decision_id"]) == 1, entry["decision_id"]


def test_every_branch_is_rendered_exactly_once() -> None:
    body = a1_board.artifact_block(_text())
    assert body is not None
    for branch in _branches():
        assert body.count("| %s |" % branch["branch"]) == 1, branch["id"]


def test_row_states_are_a_function_of_the_index() -> None:
    body = a1_board.block(_text())
    for entry in _entries():
        if not entry["decision_id"].startswith(a1_board.PREFIX):
            continue
        row = next(line for line in body.splitlines() if "[`%s`]" % entry["decision_id"] in line)
        assert "| %s |" % a1_board._state(entry) in row, entry["decision_id"]
    awaiting = [row["id"] for row in a1_board.rows() if row["state"] == "**AWAITING SIGNATURE**"]
    assert awaiting == ["DECISION-A1-C1-CEILING", "DECISION-A1-COMPETENT-ESTIMAND"]


def test_a_decision_status_change_makes_both_blocks_stale() -> None:
    """The branch block follows the index too, not just the decision block."""
    entries = json.loads(json.dumps(_entries()))
    target = next(entry for entry in entries if entry["decision_id"] == "DECISION-A1-C8-NMIN")
    target["status"] = "WITHDRAWN"
    target["status_quote"] = "WITHDRAWN"
    found = a1_board.block_problems(_text(), entries)
    assert any("decision block is stale" in problem for problem in found), found
    assert any("branch block is stale" in problem for problem in found), found


def test_an_unmet_artifact_assertion_renders_open_not_closed() -> None:
    branches = json.loads(json.dumps(_branches()))
    victim = next(branch for branch in branches if branch["id"] == "c4-completeness")
    victim["contains"] = [{"path": "benchmarks/a1_arms.py", "strings": ["NOT_A_REAL_SYMBOL"]}]
    assert "OPEN" in a1_board.branch_state(victim, _entries())
    found = a1_board.block_problems(_text(), _entries(), branches)
    assert any("branch block is stale" in problem for problem in found), found


def test_the_freeze_acts_read_their_own_status_lines() -> None:
    branch = next(item for item in _branches() if item["id"] == "freeze-acts")
    state = a1_board.branch_state(branch, _entries())
    assert state == "**NOT SIGNED**", state
    statuses = a1_board._status_lines(branch["docs"])
    assert all("DRAFT" in line for line in statuses), statuses


def test_the_prose_no_longer_claims_the_work_is_finished() -> None:
    text = _text()
    assert STALE_SENTENCE not in text
    # A record's multiplicity the operative block cannot produce stays visible in the branch block.
    body = a1_board.artifact_block(text)
    posture = next(line for line in body.splitlines() if "C4 posture clause 1" in line)
    assert "324" in posture and "1,944" in posture
    assert "OPEN UNTIL THE ESTIMAND IS ADOPTED" in posture


def test_every_link_in_both_blocks_resolves() -> None:
    text = _text()
    for body in (a1_board.block(text), a1_board.artifact_block(text)):
        assert body
        for part in body.split("["):
            if "](" not in part:
                continue
            href = part.split("](", 1)[1].split(")", 1)[0]
            if href.startswith(("http", "#")):
                continue
            assert (DOCS / href.split("#", 1)[0]).exists(), href


def test_identifier_needles_must_match_whole() -> None:
    """A renamed symbol must not satisfy the assertion it was renamed from.

    The first probe of this mechanism renamed `CONTROL_NOT_SCORED` to
    `CONTROL_NOT_SCORED_PROBE` and the board stayed closed, because the assertion was a plain
    substring test. Whole-identifier matching is what makes the branch state mean something.
    """
    assert a1_board._present("delta_status = CONTROL_NOT_SCORED\n", "CONTROL_NOT_SCORED")
    assert not a1_board._present("CONTROL_NOT_SCORED_PROBE", "CONTROL_NOT_SCORED")
    assert a1_board._present("sizes 20/17/20/20/18/20 here", "20/17/20/20/18/20")


def test_every_note_number_is_pinned_to_its_source() -> None:
    """A note quoting a counted figure is a restatement, and restatements drift."""
    claims = 0
    for branch in _branches():
        claims += len(branch.get("note_claims") or [])
        assert a1_board.claim_problems(branch) == [], branch["id"]
    assert claims == 6


def test_a_green_state_cannot_hide_a_drifted_count() -> None:
    """The row stays CLOSED when the artifact it cites drifts; the claim is what fails.

    This is the case the branch state cannot see: the file still exists and still contains the
    strings the manifest asserts, so only the number comparison catches that the note and the
    artifact no longer agree.
    """
    branch = next(item for item in _branches() if item["id"] == "c1-denominator-invariance")
    assert "CLOSED" in a1_board.branch_state(branch, _entries())

    drifted_note = json.loads(json.dumps(branch))
    drifted_note["note"] = drifted_note["note"].replace("79/64/79/74/72/74", "78/64/79/74/72/74")
    assert a1_board.claim_problems(drifted_note), "a note quoting a different count was accepted"

    drifted_source = json.loads(json.dumps(branch))
    drifted_source["note_claims"][0]["field"] = "per_seed.*.n_selected"
    assert a1_board.claim_problems(drifted_source), "a source that states other numbers was accepted"


def test_the_ceiling_clause_is_armed_and_cannot_close_without_the_rule() -> None:
    """Adoption alone must not turn the row green.

    The decision says adopting it amends one clause of `A1-PATH-A-C1-RULE-1`. If the owner adopts
    the decision and the rule is not amended, the branch must report the missing restatement rather
    than inherit the decision's status — which is what a purely status-derived row would do.
    """
    branch = next(item for item in _branches() if item["id"] == "c1-ceiling-universe")
    assert a1_board.branch_state(branch, _entries()) == "**AWAITING THE CEILING DECISION**"

    adopted = json.loads(json.dumps(_entries()))
    entry = next(item for item in adopted if item["decision_id"] == "DECISION-A1-C1-CEILING")
    entry["status"] = "ADOPTED"
    entry["status_quote"] = "ADOPTED BY OWNER"
    assert a1_board.branch_state(branch, adopted) == "**OPEN — RESTATEMENT MISSING**"

    # With the rule stating the clause, the same adoption closes the row.
    restated = json.loads(json.dumps(branch))
    restated["restated"] = [{"path": "docs/DECISION-A1-C1-CEILING.md",
                             "strings": ["preplanned universe", "DECISION-A1-C1-CEILING"]}]
    assert a1_board.branch_state(restated, adopted) == "**CLOSED — UNIVERSE RESTATED**"


def test_the_ceiling_note_is_pinned_to_the_baseline_universe() -> None:
    branch = next(item for item in _branches() if item["id"] == "c1-ceiling-universe")
    assert a1_board.claim_problems(branch) == []
    drifted = json.loads(json.dumps(branch))
    drifted["note"] = drifted["note"].replace("79 / 64", "78 / 64")
    assert a1_board.claim_problems(drifted), "a ceiling note quoting another universe was accepted"


def test_the_coverage_block_is_counted_not_typed() -> None:
    """The inventory is derived, so pinning a branch must change it."""
    data = a1_board.coverage()
    assert data["claims"] == sum(len(b.get("note_claims") or []) for b in _branches())
    assert data["number_free"] == sum(1 for b in _branches()
                                      if not a1_board.TOKEN.search(b.get("note") or ""))
    assert len(data["unpinned"]) == sum(1 for b in _branches() if a1_board._unpinned_numbers(b))
    text = a1_board.CHECKLIST_PATH.read_text(encoding="utf-8")
    assert a1_board.coverage_block(text) == a1_board.render_coverage()

    pinning = json.loads(json.dumps(_branches()))
    pinned = next(b for b in pinning if b["id"] == "competence-contract")
    pinned["note_claims"] = [{"note_regex": "N_min = ([0-9]+)",
                              "doc": "docs/DECISION-A1-C8-NMIN.md",
                              "doc_regex": "\\*\\*N_min\\*\\* \\| \\*\\*([0-9]+)"}]
    after = a1_board.coverage(pinning)
    assert after["claims"] == data["claims"] + 1
    assert after["numbers"] == data["numbers"] + 1
    # Pinning one number does not pin the row: the other two are still quoted bare.
    still_bare = dict(after["unpinned"])
    assert still_bare.get("Competence contract, N_min, capacity") == ["0.05", "3"]
    assert a1_board.render_coverage(pinning) != a1_board.render_coverage()
    assert any("coverage block is stale" in problem
               for problem in a1_board.block_problems(text, _entries(), pinning))


def test_a_record_name_is_not_a_quantity() -> None:
    """C1, C4, C8 and "the N=4 act" contain digits that are names, not measurements."""
    branch = {"id": "probe", "note": "C1 and C4 and C8; the N=4 act; 12 rows", "note_claims": []}
    assert a1_board._unpinned_numbers(branch) == ["12"]


def test_a_bare_number_must_be_allowlisted() -> None:
    """The report was a statement; this makes it an invariant that fails."""
    assert a1_board.coverage_problems() == []
    leaking = json.loads(json.dumps(_branches()))
    leaky = next(b for b in leaking if b["id"] == "c1-unit")
    leaky["note"] = leaky["note"] + ", measured on 543 rows"
    found = a1_board.coverage_problems(leaking)
    assert any("543 with no pin and no allowlist entry" in problem for problem in found), found


def test_an_allowlist_entry_must_still_be_bare() -> None:
    """Pinning an excused number must retire its excuse, so the debt can only shrink."""
    pinning = json.loads(json.dumps(_branches()))
    pinned = next(b for b in pinning if b["id"] == "competence-contract")
    pinned["note_claims"] = [{"note_regex": "N_min = ([0-9]+)",
                              "doc": "docs/DECISION-A1-C8-NMIN.md",
                              "doc_regex": "\\*\\*N_min\\*\\* \\| \\*\\*([0-9]+)"}]
    found = a1_board.coverage_problems(pinning)
    assert any("no longer quotes 17 bare" in problem for problem in found), found


def test_the_allowlist_names_real_branches_and_says_why() -> None:
    ids = {branch["id"] for branch in _branches()}
    for label, entry in a1_board.allowlist().items():
        assert label in ids, label
        assert entry.get("why"), label
        assert entry.get("numbers"), label


def test_a_note_claim_must_name_exactly_one_source() -> None:
    branch = json.loads(json.dumps(
        next(item for item in _branches() if item["id"] == "competent-construction")))
    branch["note_claims"][0]["doc_regex"] = "x"
    found = a1_board.manifest_problems([branch])
    assert any("exactly one source" in problem for problem in found), found


def test_the_manifest_names_checks_that_exist() -> None:
    found = a1_board.manifest_problems()
    assert not found, found
    proved = {target for branch in _branches() for target in branch.get("proved_by") or []}
    assert any(target.startswith("tests/") for target in proved)

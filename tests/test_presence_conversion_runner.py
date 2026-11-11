"""The Q3 authorisation path and runner must refuse unauthorised cells and execute the block.

The record is unrun, so these tests drive the runner on synthetic parts: the authorisation is a
dated document whose quote must be present, `--measure` and `--cell` refuse while `granted` is
false, the four verdicts are reachable in the record's declared order, and a finished artifact
is checked against its own rows rather than trusted.
"""
LAYER = "dry-run"  # benchmarks/test_layers.py: the module's execution layer

import copy
import json

import pytest

from benchmarks import presence_conversion_observer as O

BODY = O.prereg()
SEEDS = list(BODY["design"]["seeds"])


def _document(tmp_path, quote="i authorise it", requested=False):
    docs = tmp_path / "docs"
    docs.mkdir()
    doc = docs / O.AUTHORISATION_DOC.name
    status = "REQUESTED — NOT GRANTED" if requested else "AUTHORISED"
    doc.write_text("# AUTHORISATION\n\n**Status: %s**\n\n> %s\n" % (status, quote),
                   encoding="utf-8")
    return doc


def _granted(tmp_path, quote="i authorise it", requested=False):
    doc = _document(tmp_path, quote, requested)
    body = copy.deepcopy(BODY)
    body["authorisation"] = {"required": True, "granted": True, "granted_on": "2026-11-11",
                             "document": "docs/" + doc.name, "quote": quote}
    return body, doc


def _cell(seed, arm, present=112, constructed=112, ever=80, asserted=40, bypass=41,
          unexplained=(), observed=True):
    cell = {
        "kind": O.CELL_KIND,
        "seed": seed,
        "arm": arm,
        "cycles": BODY["design"]["cycles"],
        "world_edges": 112,
        "present_world_edges": present,
        "present_fingerprint": "present-%d" % seed,
        "windows": [[["a", "b"]]],
        "s_cycle_max": 40,
        "s_ever_world_edges": ever,
        "s_ever_fingerprint": "ever-%d" % seed,
        "asserted_world_edges": asserted,
        "asserted_world_fingerprint": "world-%d" % seed,
        "asserted_fingerprint": "asserted-%d" % seed,
        "asserted_without_admission": bypass,
        "constructed_world_edges": constructed,
        "a_w_subset_of_p": True,
        "candidates": [{"rank": 1}] if observed else None,
        "eligibility": {"a->b": "constructed"} if observed else None,
        "unexplained": list(unexplained),
    }
    return cell


def _run(rows=None, witness=None, control=None):
    rows = rows or [O._row(seed, _cell(seed, "off"), _cell(seed, "on")) for seed in SEEDS]
    return {
        "rows": rows,
        "witness": witness or {"reproduces": True, "differs": []},
        "control": control or {"neutral": True, "differs": []},
    }


def _write_parts(base, body):
    parts = base / "parts"
    parts.mkdir()
    for seed in body["design"]["seeds"]:
        for arm in body["design"]["arms"]:
            (parts / ("%s_%s.json" % (seed, arm))).write_text(
                json.dumps(_cell(seed, arm)), encoding="utf-8")
    witness = body["design"]["witness_cell"]
    (parts / ("%s_%s_witness.json" % (witness["seed"], witness["arm"]))).write_text(
        json.dumps(_cell(witness["seed"], "off")), encoding="utf-8")
    (parts / ("%s_on_control.json" % body["design"]["seeds"][0])).write_text(
        json.dumps(_cell(body["design"]["seeds"][0], "on")), encoding="utf-8")
    return parts


def test_a_grant_without_a_document_is_refused(tmp_path):
    body = copy.deepcopy(BODY)
    body["authorisation"] = {"required": True, "granted": True}
    assert O.authorisation_problems(body, tmp_path / "docs" / O.AUTHORISATION_DOC.name)


def test_a_grant_with_a_matching_document_passes(tmp_path):
    body, doc = _granted(tmp_path)
    assert O.authorisation_problems(body, doc) == []


def test_a_grant_whose_quote_is_absent_is_refused(tmp_path):
    body, doc = _granted(tmp_path)
    body["authorisation"]["quote"] = "words that are not in the document"
    assert any("quote" in problem for problem in O.authorisation_problems(body, doc))


def test_a_grant_naming_another_document_is_refused(tmp_path):
    body, doc = _granted(tmp_path)
    body["authorisation"]["document"] = "docs/AUTHORISATION-SOMETHING-ELSE.md"
    assert any("names" in problem for problem in O.authorisation_problems(body, doc))


def test_a_document_that_still_says_requested_is_refused(tmp_path):
    body, doc = _granted(tmp_path, requested=True)
    assert any("REQUESTED" in problem for problem in O.authorisation_problems(body, doc))


def test_authorisation_leaves_the_protocol_untouched(tmp_path):
    body, doc = _granted(tmp_path)
    assert O.authorisation_problems(body, doc) == []
    assert body["design"] == BODY["design"]
    assert body["gates"] == BODY["gates"]
    assert body["decision_table"] == BODY["decision_table"]
    assert body["loss"] == BODY["loss"]


def test_measure_refuses_while_unauthorised(monkeypatch, tmp_path):
    """Driven by a forged ungranted record: the shipped record is authorised, so calling
    `measure` against it would run fourteen cells."""
    request = _document(tmp_path, requested=True)
    body = copy.deepcopy(BODY)
    body["authorisation"] = {"required": True, "granted": False,
                             "request": "docs/" + request.name}
    monkeypatch.setattr(O, "prereg", lambda: body)
    monkeypatch.setattr(O, "AUTHORISATION_DOC", request)
    with pytest.raises(SystemExit, match="not authorised"):
        O.measure()


def test_a_cell_refuses_while_unauthorised(tmp_path, monkeypatch):
    body = copy.deepcopy(BODY)
    body["authorisation"] = {"required": True, "granted": False}
    monkeypatch.setattr(O, "prereg", lambda: body)
    out = tmp_path / "cell.json"
    with pytest.raises(SystemExit, match="not authorised"):
        O.main(["--cell", "1", "--arm", "on", "--out", str(out)])
    assert not out.exists()


def test_measure_runs_the_twelve_cells_the_witness_and_the_control(tmp_path, monkeypatch):
    body, doc = _granted(tmp_path)
    calls = []
    monkeypatch.setattr(O, "prereg", lambda: body)
    monkeypatch.setattr(O, "AUTHORISATION_DOC", doc)
    monkeypatch.setattr(O, "ARTIFACT", tmp_path / "absent.json")
    monkeypatch.setattr(O, "_run_part",
                        lambda seed, arm, suffix="": calls.append((seed, arm, suffix)))
    assert O.measure() == 0
    assert len(calls) == 14, calls
    assert calls[-1] == (SEEDS[0], "on", "_control")
    assert (BODY["design"]["witness_cell"]["seed"],
            BODY["design"]["witness_cell"]["arm"], "_witness") in calls


def test_an_observer_divergence_is_not_a_conversion_result():
    run = _run()
    run["rows"][0]["neutral"] = {"neutral": False, "differs": ["admission windows"]}
    label, details = O.verdict(BODY, run)
    assert label == "OBSERVER NOT NEUTRAL"
    assert details["gate"] == "X1_observer_neutral"


def test_a_witness_that_misses_the_audit_row_is_void():
    label, details = O.verdict(BODY, _run(witness={"reproduces": False,
                                                   "differs": ["asserted world edges"]}))
    assert label == "VOID" and details["gate"] == "X8_control_reproduces_audit"


def test_a_control_that_does_not_reproduce_the_first_seed_is_void():
    label, details = O.verdict(BODY, _run(control={"neutral": False,
                                                   "differs": ["admitted union"]}))
    assert label == "VOID" and details["gate"] == "X7_determinism"


def test_an_unexplained_edge_is_void():
    rows = [O._row(seed, _cell(seed, "off"), _cell(seed, "on")) for seed in SEEDS]
    rows[2]["unexplained"] = ["a->b"]
    label, details = O.verdict(BODY, _run(rows))
    assert label == "VOID" and details["gate"] == "X2_stage_complete"


def test_a_zero_denominator_is_void():
    rows = [O._row(seed, _cell(seed, "off"), _cell(seed, "on")) for seed in SEEDS]
    rows[0]["counts"]["C"] = 0
    label, details = O.verdict(BODY, _run(rows))
    assert label == "VOID" and details["gate"] == "X2_stage_complete"
    assert details["zero_denominator"]


def test_an_object_mismatch_is_void():
    rows = [O._row(seed, _cell(seed, "off"), _cell(seed, "on")) for seed in SEEDS]
    rows[1]["a_w_subset_of_p"] = False
    label, details = O.verdict(BODY, _run(rows))
    assert label == "VOID" and details["gate"] == "X4_same_object"


def test_an_unobserved_stage_is_partial_not_a_conversion_result():
    rows = [O._row(seed, _cell(seed, "off"),
                   _cell(seed, "on", ever=80 + index, observed=index != 0))
            for index, seed in enumerate(SEEDS)]
    label, details = O.verdict(BODY, _run(rows))
    assert label == "PARTIAL OBSERVATION"
    assert details["unobserved"] == [SEEDS[0]]


def test_a_seed_axis_that_does_not_move_is_void():
    label, details = O.verdict(BODY, _run())
    assert label == "VOID" and details["gate"] == "X6_seed_axis"


def test_a_complete_neutral_block_produces_a_target():
    rows = [O._row(seed, _cell(seed, "off"),
                   _cell(seed, "on", ever=80 + index, asserted=40 + index, bypass=41))
            for index, seed in enumerate(SEEDS)]
    label, details = O.verdict(BODY, _run(rows))
    assert label == "CONVERSION OBSERVED"
    assert len(details["suspects"]) == len(SEEDS)


def test_finish_refuses_when_a_part_is_missing(tmp_path, monkeypatch):
    body, doc = _granted(tmp_path)
    monkeypatch.setattr(O, "prereg", lambda: body)
    monkeypatch.setattr(O, "PARTS", tmp_path / "parts")
    monkeypatch.setattr(O, "ARTIFACT", tmp_path / "run.json")
    monkeypatch.setattr(O, "AUTHORISATION_DOC", doc)
    with pytest.raises(SystemExit, match="missing part"):
        O.finish()


def test_finish_writes_the_artifact_and_page_and_check_accepts(tmp_path, monkeypatch):
    body, doc = _granted(tmp_path)
    parts = _write_parts(tmp_path, body)
    monkeypatch.setattr(O, "prereg", lambda: body)
    monkeypatch.setattr(O, "PARTS", parts)
    monkeypatch.setattr(O, "ARTIFACT", tmp_path / "run.json")
    monkeypatch.setattr(O, "RESULT", tmp_path / "RESULT.md")
    monkeypatch.setattr(O, "AUTHORISATION_DOC", doc)
    monkeypatch.setattr(O, "_witness_matches",
                        lambda witness: {"reproduces": True, "differs": [], "audit": {}})
    assert O.finish() == 0
    art = json.loads((tmp_path / "run.json").read_text(encoding="utf-8"))
    assert art["verdict"] in O.VERDICTS
    assert "{" not in (tmp_path / "RESULT.md").read_text(encoding="utf-8")
    assert O.check() == 0


def test_a_stale_result_page_fails_the_check(tmp_path, monkeypatch):
    body, doc = _granted(tmp_path)
    parts = _write_parts(tmp_path, body)
    monkeypatch.setattr(O, "prereg", lambda: body)
    monkeypatch.setattr(O, "PARTS", parts)
    monkeypatch.setattr(O, "ARTIFACT", tmp_path / "run.json")
    monkeypatch.setattr(O, "RESULT", tmp_path / "RESULT.md")
    monkeypatch.setattr(O, "AUTHORISATION_DOC", doc)
    monkeypatch.setattr(O, "_witness_matches",
                        lambda witness: {"reproduces": True, "differs": [], "audit": {}})
    assert O.finish() == 0
    (tmp_path / "RESULT.md").write_text("edited\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="stale"):
        O.check()

def test_x8_compares_the_three_fields_the_audit_row_publishes():
    audit = json.loads(O.AUDIT.read_text(encoding="utf-8"))
    seed = BODY["design"]["witness_cell"]["seed"]
    row = next(item for item in audit["rows"] if item["seed"] == seed)
    witness = {key: row[key] for key in
               ("seed", "present_world_edges", "asserted_world_edges", "asserted_fingerprint")}
    assert O._witness_matches(witness)["reproduces"] is True
    for field, label in (("present_world_edges", "present world edges"),
                         ("asserted_world_edges", "asserted world edges"),
                         ("asserted_fingerprint", "asserted fingerprint")):
        changed = dict(witness)
        changed[field] = (changed[field] + 1 if isinstance(changed[field], int)
                          else "0" * len(changed[field]))
        result = O._witness_matches(changed)
        assert result["reproduces"] is False, field
        assert label in result["differs"], field

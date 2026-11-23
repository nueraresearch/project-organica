"""The Q1 construct-audit preregistration must stay frozen, audit-derived and unauthorised.

The record reuses the published audit's six seeds, so the tests check that the seed block and
the comparator build are the audit's rather than a typed claim, that every verdict is
reachable from the decision table, and that each way of moving the record fails the gate.
"""
LAYER = "synthetic"  # benchmarks/test_layers.py: the module's execution layer

import copy
import inspect
import json

import pytest

from benchmarks import acquisition_harness as H
from benchmarks import presence_construct_audit as C
from benchmarks.acquisition_compositional import generate_compositional_world

BODY = C.prereg()
AUDIT = C.audit()
SEEDS = [row["seed"] for row in AUDIT["rows"]]


def test_the_record_is_frozen_authorised_and_run():
    assert BODY["prereg"] == "PRESENCE-CONSTRUCT-1"
    assert BODY["status"] == "FROZEN, RUN"
    assert BODY["no_cells_run"] is False
    assert BODY["design"]["no_cells_run"] is False
    auth = BODY["authorisation"]
    assert auth["granted"] is True
    assert auth["granted_on"] == "2026-11-10"
    assert auth["quote"] == "Authorize all runs"
    assert auth["document"] == "docs/" + C.AUTHORISATION_DOC.name
    assert auth["scope"].startswith("all three frozen conversion blocks")
    assert C.authorisation_problems(BODY) == []
    assert C.ARTIFACT.exists(), "the authorised block ran and wrote its artifact"
    assert BODY["result"]["verdict"] == "CONSTRUCT VALID"
    assert BODY["result"]["artifact"] == "docs/" + C.ARTIFACT.name
    assert C.check() == 0
    assert C.audit_preflight_problems(BODY) == []
    assert C.validate(BODY) == []


def test_the_seeds_are_the_published_audits_and_the_reuse_is_disclosed():
    assert BODY["design"]["seeds"] == SEEDS
    assert len(SEEDS) == 6 and len(set(SEEDS)) == 6
    assert BODY["design"]["fresh"] is False
    assert "reuse" in BODY["design"]["freshness"].lower()
    assert BODY["design"]["control_cell"]["seed"] in SEEDS


def test_the_design_is_the_audit_block_at_the_shipped_cap():
    assert BODY["design"]["cycles"] == 120
    assert BODY["design"]["cells"] == len(SEEDS) == 6
    superseded = BODY["build_superseded"]
    assert BODY["design"]["cap"] == superseded["recorded_cap"] == 40
    assert C.shipped_cap() == 112, "the record is superseded only while the cap has landed"
    assert BODY["engine"]["edit"] == "none"
    assert BODY["engine"]["version"] == superseded["recorded_version"]


def test_every_gate_is_declared_and_each_verdict_is_reachable():
    assert tuple(BODY["gates"]) == C.GATES
    assert set(C.VERDICT_ORDER) == set(C.GATES)
    assert len(C.VERDICT_ORDER) == len(C.GATES)
    verdicts = [row["verdict"] for row in BODY["decision_table"]]
    assert set(verdicts) == set(C.VERDICTS)
    for verdict in C.VERDICTS:
        rows = [row for row in BODY["decision_table"] if row["verdict"] == verdict]
        assert rows, verdict
        assert all(row["decision"] and row["licenses"] for row in rows)


def test_the_page_is_generated_from_the_record_and_carries_no_placeholder():
    page = C.DOC.read_text(encoding="utf-8")
    assert page == C.render_prereg(BODY)
    assert "{" not in page and "}" not in page


def test_the_pages_numbers_are_the_audits_numbers():
    page = C.DOC.read_text(encoding="utf-8")
    low = min(row["asserted_world_edges"] for row in AUDIT["rows"])
    high = max(row["asserted_world_edges"] for row in AUDIT["rows"])
    assert ("%d-%d" % (low, high)) in page
    assert str(AUDIT["rows"][0]["world_edges"]) in page
    assert str(AUDIT["rows"][0]["present_world_edges"]) in page


def test_check_prereg_is_clean():
    assert C.check_prereg() == 0


def test_a_moved_seed_is_caught():
    forged = copy.deepcopy(BODY)
    forged["design"]["seeds"][0] += 1
    assert any("seed" in problem for problem in C.validate(forged))


def test_a_changed_cycle_count_is_caught():
    forged = copy.deepcopy(BODY)
    forged["design"]["cycles"] = 300
    assert any("cycle" in problem for problem in C.validate(forged))


def test_a_removed_gate_is_caught():
    forged = copy.deepcopy(BODY)
    forged["gates"].pop("C5_object")
    assert any("gate" in problem for problem in C.validate(forged))


def test_a_removed_verdict_is_caught():
    forged = copy.deepcopy(BODY)
    forged["decision_table"] = [row for row in forged["decision_table"]
                                if row["verdict"] != "OBJECT MISMATCH"]
    assert any("decision table" in problem for problem in C.validate(forged))


def test_a_grant_is_an_owner_decision_not_a_field():
    forged = copy.deepcopy(BODY)
    forged["authorisation"] = {"required": True, "granted": True}
    assert any("authorisation" in problem for problem in C.validate(forged))


def test_an_engine_edit_is_refused():
    forged = copy.deepcopy(BODY)
    forged["engine"]["edit"] = "the cap was changed in organica/sleep.py"
    assert any("engine" in problem for problem in C.validate(forged))


def test_a_comparator_audit_from_another_build_is_refused(monkeypatch, tmp_path):
    art = copy.deepcopy(AUDIT)
    art["engine_sha256"] = "0" * 64
    forged = tmp_path / "audit.json"
    forged.write_text(json.dumps(art), encoding="utf-8")
    monkeypatch.setattr(C, "AUDIT", forged)
    assert any("comparator audit" in problem for problem in C.validate(BODY))


def test_a_stale_page_fails_the_gate(monkeypatch, tmp_path):
    page = tmp_path / "prereg.md"
    page.write_text(C.render_prereg(BODY) + "\n", encoding="utf-8")
    monkeypatch.setattr(C, "DOC", page)
    with pytest.raises(SystemExit) as caught:
        C.check_prereg()
    assert "stale" in str(caught.value)


def test_the_runner_refuses_an_ungranted_record(monkeypatch, tmp_path):
    """The refusal path is driven by a forged ungranted record, never by the real one.

    The shipped record is authorised, so testing this against it would run a cell. The
    forged record is internally consistent: it points at a document that still carries the
    ungranted status, which is what `validate` requires of an ungranted record.
    """
    assert BODY["runner"]["status"] == "built"
    assert "--dry-run" in BODY["runner"]["entry_points"]
    assert hasattr(C, "measure") and hasattr(C, "run_cell")
    request = tmp_path / C.AUTHORISATION_DOC.name
    request.write_text("REQUESTED — NOT GRANTED\n", encoding="utf-8")
    forged = copy.deepcopy(BODY)
    forged["status"] = "FROZEN, NOT RUN"
    forged["no_cells_run"] = True
    forged["design"]["no_cells_run"] = True
    forged.pop("result", None)
    forged["authorisation"] = {"required": True, "granted": False,
                               "request": "docs/" + request.name,
                               "note": "an ungranted record is refused"}
    monkeypatch.setattr(C, "prereg", lambda: forged)
    monkeypatch.setattr(C, "AUTHORISATION_DOC", request)
    for argv in (["--measure"], ["--cell", str(SEEDS[0]), "--out", str(tmp_path / "x.json")]):
        with pytest.raises(SystemExit) as caught:
            C.main(argv)
        assert "not authorised" in str(caught.value)


def test_a_grant_names_a_dated_document_and_a_quote(tmp_path):
    doc = tmp_path / "AUTHORISATION-PRESENCE-CONSTRUCT-1.md"
    doc.write_text("Granted on 2026-11-11. The owner authorises six cells.\n", encoding="utf-8")
    forged = copy.deepcopy(BODY)
    forged["authorisation"].update({
        "granted": True, "granted_on": "2026-11-11",
        "document": "docs/" + doc.name,
        "quote": "The owner authorises six cells.",
    })
    assert C.authorisation_problems(forged, doc) == []

    bare = copy.deepcopy(forged)
    bare["authorisation"].pop("quote")
    assert any("quote" in problem for problem in C.authorisation_problems(bare, doc))

    still_requested = tmp_path / "request.md"
    still_requested.write_text("REQUESTED — NOT GRANTED\n", encoding="utf-8")
    assert any("NOT GRANTED" in problem
               for problem in C.authorisation_problems(forged, still_requested))


@pytest.mark.parametrize(
    ("mutation", "needle"),
    (("fingerprint", "16-hex"), ("row_count", "frozen seeds")),
)
def test_measure_refuses_a_grant_when_the_audit_preflight_fails(
        mutation, needle, monkeypatch, tmp_path):
    doc = tmp_path / C.AUTHORISATION_DOC.name
    doc.write_text("The owner authorises six cells.\n", encoding="utf-8")
    art = copy.deepcopy(AUDIT)
    if mutation == "fingerprint":
        art["rows"][0]["asserted_fingerprint"] = "g" * 16
    else:
        art["rows"] = art["rows"][:-1]
    forged_audit = tmp_path / "audit.json"
    forged_audit.write_text(json.dumps(art), encoding="utf-8")

    forged = copy.deepcopy(BODY)
    forged["authorisation"].update({
        "granted": True, "granted_on": "2026-11-11",
        "document": "docs/" + doc.name,
        "quote": "The owner authorises six cells.",
    })
    monkeypatch.setattr(C, "prereg", lambda: forged)
    monkeypatch.setattr(C, "AUDIT", forged_audit)
    monkeypatch.setattr(C, "AUTHORISATION_DOC", doc)
    seen = []
    monkeypatch.setattr(C, "_run_part", lambda seed, suffix="": seen.append(seed))
    with pytest.raises(SystemExit) as caught:
        C.measure()
    assert needle in str(caught.value)
    assert seen == []


def test_measure_refuses_a_grant_without_the_document(monkeypatch, tmp_path):
    forged = copy.deepcopy(BODY)
    forged["authorisation"].update({
        "granted": True, "granted_on": "2026-11-11",
        "document": "docs/" + C.AUTHORISATION_DOC.name,
        "quote": "The owner authorises six cells.",
    })
    monkeypatch.setattr(C, "prereg", lambda: forged)
    monkeypatch.setattr(C, "AUTHORISATION_DOC", tmp_path / C.AUTHORISATION_DOC.name)
    seen = []
    monkeypatch.setattr(C, "_run_part", lambda seed, suffix="": seen.append(seed))
    with pytest.raises(SystemExit) as caught:
        C.measure()
    assert "not valid" in str(caught.value)
    assert seen == []


def test_measure_runs_six_reading_cells_and_the_control(monkeypatch, tmp_path):
    doc = tmp_path / C.AUTHORISATION_DOC.name
    doc.write_text("The owner authorises six cells.\n", encoding="utf-8")
    forged = copy.deepcopy(BODY)
    forged["authorisation"].update({
        "granted": True, "granted_on": "2026-11-11",
        "document": "docs/" + doc.name,
        "quote": "The owner authorises six cells.",
    })
    monkeypatch.setattr(C, "prereg", lambda: forged)
    monkeypatch.setattr(C, "AUTHORISATION_DOC", doc)
    seen = []
    monkeypatch.setattr(C, "_run_part",
                        lambda seed, suffix="": seen.append((seed, suffix)))
    assert C.measure() == 0
    assert seen == [(seed, "") for seed in SEEDS] + [(SEEDS[0], "_control")]


def test_dry_run_prints_seven_commands_without_running_a_cell(monkeypatch, capsys):
    def fail(*args, **kwargs):
        raise AssertionError("dry run executed a cell")

    monkeypatch.setattr(C, "run_cell", fail)
    monkeypatch.setattr(C, "_run_part", fail)
    monkeypatch.setattr(C.subprocess, "run", fail)
    assert C.main(["--dry-run"]) == 0
    out = capsys.readouterr().out
    expected = [(seed, "") for seed in SEEDS] + [(SEEDS[0], "_control")]
    assert out.count("  command: ") == 7
    assert out.count("  part: ") == 7
    commands = [line for line in out.splitlines() if line.startswith("  command: ")]
    assert all("--cell" in line for line in commands)
    for seed, suffix in expected:
        assert "cell seed=%d%s" % (seed, suffix) in out
        assert str(C._part_path(seed, suffix)) in out
    assert "No cell was run." in out


def _cell(seed):
    present = [("a", "b"), ("b", "c")]
    asserted = [("a", "b")]
    cell = {
        "kind": C.CELL_KIND, "seed": seed, "cycles": 120, "cap": C.shipped_cap(),
        "engine_version": C.engine_stamp.engine_version(),
        "engine_sha256": C.engine_stamp.engine_sha256(),
        "world_edges": 2, "world_digest": C._digest({("a", "b"), ("b", "c")}),
        "present_world_edges": 2, "present_fingerprint": C._digest(set(present)),
        "s_cycle_world_edges": [2], "s_cycle_max": 2,
        "s_ever_world_edges": 2, "s_ever_fingerprint": C._digest(set(present)),
        "s_final_world_edges": 1, "s_final_fingerprint": C._digest(set(asserted)),
        "asserted_total": 1, "asserted_fingerprint": C._digest(set(asserted)),
        "asserted_world_edges": 1, "asserted_world_fingerprint": C._digest(set(asserted)),
        "a_pred_world_edges": 1, "a_other_world_edges": 0, "a_w_subset_of_p": True,
        "stage_fingerprint": C._fingerprint("seed=%d" % seed),
        "pse_fingerprint": C._fingerprint("seed=%d" % seed),
        "windows_world": [["a>b"]],
        "edges": [
            {"source": "a", "target": "b", "present": True, "admitted": True,
             "asserted": True, "admissions": 1},
            {"source": "b", "target": "c", "present": True, "admitted": True,
             "asserted": False, "admissions": 1},
        ],
    }
    return C.engine_stamp.stamp(cell)


def _fake_audit_row(seed):
    return {"seed": seed, "world_edges": 2, "present_world_edges": 2,
            "asserted_world_edges": 1, "asserted_fingerprint": C._digest({("a", "b")})}


def _verdict(monkeypatch, rows=None, control=None):
    monkeypatch.setattr(C, "audit_row", _fake_audit_row)
    rows = rows or [_cell(seed) for seed in SEEDS]
    control = control or copy.deepcopy(rows[0])
    return C.verdict(BODY, rows, control)


def test_a_clean_table_is_a_construct_pass(monkeypatch):
    assert _verdict(monkeypatch) == ("CONSTRUCT VALID", {"seeds": len(SEEDS)})


def test_a_mixed_build_is_void(monkeypatch):
    rows = [_cell(seed) for seed in SEEDS]
    rows[2]["engine_sha256"] = "0" * 64
    assert _verdict(monkeypatch, rows)[0] == "VOID"
    assert _verdict(monkeypatch, rows)[1]["gate"] == "C1_build"


def test_a_nondeterministic_control_is_void(monkeypatch):
    rows = [_cell(seed) for seed in SEEDS]
    control = copy.deepcopy(rows[0])
    control["windows_world"] = [["b>c"]]
    assert _verdict(monkeypatch, rows, control) == (
        "VOID", {"gate": "C8_determinism", "seed": SEEDS[0],
                 "differs": ["windows_world"]})


def test_an_asserted_edge_outside_presence_is_an_object_mismatch(monkeypatch):
    rows = [_cell(seed) for seed in SEEDS]
    rows[1]["edges"][0]["present"] = False
    rows[1]["a_w_subset_of_p"] = False
    label, details = _verdict(monkeypatch, rows)
    assert label == "OBJECT MISMATCH" and details["gate"] == "C5_object"
    assert details["edges"] == ["a>b"]


def test_an_empty_stage_is_not_measurable(monkeypatch):
    rows = [_cell(seed) for seed in SEEDS]
    rows[3]["s_ever_world_edges"] = 0
    label, details = _verdict(monkeypatch, rows)
    assert label == "NOT MEASURABLE" and details["gate"] == "C4_denominator"


def test_a_moved_world_is_void(monkeypatch):
    rows = [_cell(seed) for seed in SEEDS]
    rows[4]["world_edges"] = 3
    assert _verdict(monkeypatch, rows)[1]["gate"] == "C2_world"


def test_a_count_without_membership_is_void(monkeypatch):
    rows = [_cell(seed) for seed in SEEDS]
    rows[0]["edges"] = rows[0]["edges"][:1]
    label, details = _verdict(monkeypatch, rows)
    assert label == "VOID" and details["gate"] == "C3_presence"


def test_a_missing_negative_witness_is_void(monkeypatch):
    rows = [_cell(seed) for seed in SEEDS]
    rows[5]["edges"][1]["asserted"] = True
    assert _verdict(monkeypatch, rows)[1]["gate"] == "C6_witnesses"


def test_one_fingerprint_across_seeds_is_void(monkeypatch):
    rows = [_cell(seed) for seed in SEEDS]
    for row in rows:
        row["pse_fingerprint"] = rows[0]["pse_fingerprint"]
    label, details = _verdict(monkeypatch, rows)
    assert label == "VOID" and details["gate"] == "C7_seed_axis"
    assert details["distinct"] == 1


def test_a_cell_that_does_not_reproduce_its_audit_row_is_void(monkeypatch):
    rows = [_cell(seed) for seed in SEEDS]
    rows[2]["asserted_fingerprint"] = "0" * 16
    label, details = _verdict(monkeypatch, rows)
    assert label == "VOID" and details["gate"] == "C9_audit_row_reproduced"
    assert details["differs"] == ["asserted_fingerprint"]


def test_finish_writes_an_artifact_and_check_accepts_it(monkeypatch, tmp_path):
    doc = tmp_path / C.AUTHORISATION_DOC.name
    doc.write_text("The owner authorises six cells.\n", encoding="utf-8")
    forged = copy.deepcopy(BODY)
    forged["authorisation"].update({
        "granted": True, "granted_on": "2026-11-11",
        "document": "docs/" + doc.name,
        "quote": "The owner authorises six cells.",
    })
    parts = tmp_path / "parts"
    parts.mkdir()
    rows = [_cell(seed) for seed in SEEDS]
    for row in rows:
        (parts / ("%d.json" % row["seed"])).write_text(json.dumps(row), encoding="utf-8")
    control = copy.deepcopy(rows[0])
    (parts / ("%d_control.json" % SEEDS[0])).write_text(json.dumps(control), encoding="utf-8")

    monkeypatch.setattr(C, "prereg", lambda: forged)
    monkeypatch.setattr(C, "audit_row", _fake_audit_row)
    monkeypatch.setattr(C, "AUTHORISATION_DOC", doc)
    monkeypatch.setattr(C, "PARTS", parts)
    monkeypatch.setattr(C, "ARTIFACT", tmp_path / "run.json")
    monkeypatch.setattr(C, "RESULT", tmp_path / "result.md")
    assert C.finish() == 0
    assert C.check() == 0
    C.RESULT.write_text(C.RESULT.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(SystemExit) as caught:
        C.check()
    assert "stale" in str(caught.value)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("engine_version", "0.13.0", "built by engine 0.13.0"),
        ("engine_sha256", "0" * 64, "different engine bytes"),
        ("engine_commit", "0" * 40, "predates the current engine pin"),
    ),
)
def test_check_rejects_a_part_from_a_different_build_or_before_the_pin(
        field, value, message, monkeypatch, tmp_path):
    doc = tmp_path / C.AUTHORISATION_DOC.name
    doc.write_text("The owner authorises six cells.\n", encoding="utf-8")
    forged = copy.deepcopy(BODY)
    forged["authorisation"].update({
        "granted": True, "granted_on": "2026-11-11",
        "document": "docs/" + doc.name,
        "quote": "The owner authorises six cells.",
    })
    parts = tmp_path / "parts"
    parts.mkdir()
    rows = [_cell(seed) for seed in SEEDS]
    for row in rows:
        (parts / ("%d.json" % row["seed"])).write_text(json.dumps(row), encoding="utf-8")
    control = copy.deepcopy(rows[0])
    (parts / ("%d_control.json" % SEEDS[0])).write_text(
        json.dumps(control), encoding="utf-8")
    monkeypatch.setattr(C, "prereg", lambda: forged)
    monkeypatch.setattr(C, "audit_row", _fake_audit_row)
    monkeypatch.setattr(C, "AUTHORISATION_DOC", doc)
    monkeypatch.setattr(C, "PARTS", parts)
    monkeypatch.setattr(C, "ARTIFACT", tmp_path / "run.json")
    monkeypatch.setattr(C, "RESULT", tmp_path / "result.md")
    assert C.finish() == 0

    victim = parts / ("%d.json" % SEEDS[0])
    part = json.loads(victim.read_text(encoding="utf-8"))
    part[field] = value
    victim.write_text(json.dumps(part), encoding="utf-8")
    with pytest.raises(SystemExit) as caught:
        C.check()
    assert message in str(caught.value)


def test_the_neighbouring_frozen_blocks_still_validate():
    from benchmarks import presence_cap_experiment as cap
    from benchmarks import presence_conversion_observer as observer

    assert cap.validate(cap.prereg()) == []
    assert observer.validate(observer.prereg()) == []


def test_the_record_names_its_authorisation_document():
    auth = BODY["authorisation"]
    assert auth["request"] == "docs/" + C.AUTHORISATION_DOC.name
    assert C.AUTHORISATION_DOC.exists()
    text = C.AUTHORISATION_DOC.read_text(encoding="utf-8")
    assert "AUTHORISED — RUN" in text
    assert auth["quote"] in text
    assert "REQUESTED — NOT GRANTED" not in text
    assert C.validate(BODY) == []


def test_removing_the_request_reference_is_caught():
    forged = copy.deepcopy(BODY)
    forged["authorisation"].pop("request")
    assert any("request" in problem for problem in C.validate(forged))


def test_the_request_names_the_cells_and_the_reuse():
    text = C.AUTHORISATION_DOC.read_text(encoding="utf-8")
    for phrase in ("six reading cells", "C8", "20261100", "120", "not fresh", "C9"):
        assert phrase in text, phrase
    assert "PRESENCE-CONSTRUCT-1" in text


def test_a_grant_quoting_the_request_is_accepted(tmp_path):
    text = C.AUTHORISATION_DOC.read_text(encoding="utf-8")
    authorised = text.replace("REQUESTED — NOT GRANTED", "AUTHORISED")
    doc = tmp_path / C.AUTHORISATION_DOC.name
    doc.write_text(authorised, encoding="utf-8")
    quote = "The seed block is **not fresh**."
    assert quote in authorised
    forged = copy.deepcopy(BODY)
    forged["authorisation"].update({
        "granted": True, "granted_on": "2026-11-11",
        "document": "docs/" + doc.name, "quote": quote,
    })
    assert C.authorisation_problems(forged, doc) == []


def test_q1_digest_is_the_audit_fingerprint_rule():
    pairs = {("b", "c"), ("a", "b"), ("z", "a")}
    expected = C.hashlib.sha256(
        "|".join("%s>%s" % edge for edge in sorted(pairs)).encode("utf-8")
    ).hexdigest()[:16]
    assert C._digest(pairs) == expected
    assert len(expected) == 16
    assert int(expected, 16) >= 0


def test_q1_world_edges_are_the_audit_harness_derivation():
    world = generate_compositional_world(seed=SEEDS[0], cycles=BODY["design"]["cycles"])
    assert C._world_compositional_edges(world) == H._world_compositional_edges(world)
    assert len(C._world_compositional_edges(world)) == 112


def test_c9_uses_the_harness_fingerprint_function():
    """C9 records the audit's whole-set digest through the harness's own function."""
    audit_source = inspect.getsource(H.gate_acquisition_sufficiency)
    assert '"asserted_fingerprint": asserted_fingerprint(asserted_pairs)' in audit_source
    assert "def asserted_fingerprint" in inspect.getsource(H)
    assert "hexdigest()[:16]" in inspect.getsource(H.asserted_fingerprint)

    pairs = {("b", "c"), ("a", "b"), ("z", "a")}
    expected = C.hashlib.sha256(
        "|".join("%s>%s" % edge for edge in sorted(pairs)).encode("utf-8")
    ).hexdigest()[:16]
    assert H.asserted_fingerprint(pairs) == expected
    assert C.asserted_fingerprint(pairs) == expected
    assert C.witness_rows.fingerprint(pairs) == expected
    helper_source = inspect.getsource(C.witness_rows.fingerprint)
    assert "from benchmarks.acquisition_harness import asserted_fingerprint" in helper_source
    assert "return asserted_fingerprint(pairs)" in helper_source

    cell_source = inspect.getsource(C.run_cell)
    assert '"asserted_fingerprint": asserted_fingerprint(asserted_pairs)' in cell_source
    assert 'asserted_fingerprint(asserted_world)' not in cell_source
    assert 'asserted_fingerprint(final)' not in cell_source

    assert "asserted_fingerprint" in C.witness_rows.AUDIT_ROW_FIELDS
    failures_source = inspect.getsource(C._failures)
    assert "witness_rows.compare(" in failures_source
    assert 'audit_row(cell["seed"])' in failures_source
    assert "fields=witness_rows.AUDIT_ROW_FIELDS" in failures_source


def test_c9_compares_the_whole_asserted_fingerprint_not_the_a_w_subset(monkeypatch):
    rows = [_cell(seed) for seed in SEEDS]
    whole = {("a", "b"), ("x", "y")}
    subset = {("a", "b")}
    assert C._digest(whole) != C._digest(subset)
    rows[0]["asserted_fingerprint"] = C._digest(whole)

    def audit_with(whole_fingerprint):
        def fake(seed):
            return {"seed": seed, "world_edges": 2, "present_world_edges": 2,
                    "asserted_world_edges": 1,
                    "asserted_fingerprint": (whole_fingerprint
                                             if seed == SEEDS[0]
                                             else C._digest(subset))}
        return fake

    monkeypatch.setattr(C, "audit_row", audit_with(C._digest(whole)))
    label, details = C.verdict(BODY, rows, copy.deepcopy(rows[0]))
    assert label == "CONSTRUCT VALID", details

    rows[0]["asserted_fingerprint"] = C._digest(subset)
    label, details = C.verdict(BODY, rows, copy.deepcopy(rows[0]))
    assert label == "VOID" and details["gate"] == "C9_audit_row_reproduced"
    assert details["differs"] == ["asserted_fingerprint"]


def test_the_record_states_the_c9_basis():
    basis = BODY["freeze_notes"]["c9_fingerprint_basis"]
    assert "whole asserted set" in basis
    assert "A_W" in basis
    assert "not over" in basis
